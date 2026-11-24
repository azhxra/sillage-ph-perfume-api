"""Sillage PH API: live PostgreSQL, Supabase Auth, and labeled read-only preview."""
import logging
import os
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, Query, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from . import database as db, preview, auth
from .models import PerfumeInput, LoginInput, SignupInput, Gender, Family, Sort

app = FastAPI(title='Sillage PH Perfume API', version='4.0.0')
app.add_middleware(CORSMiddleware, allow_origins=[o.strip() for o in os.getenv('ALLOWED_ORIGINS','').split(',') if o.strip() and o.strip() != '*'], allow_credentials=False, allow_methods=['GET','POST','PUT','DELETE'], allow_headers=['Content-Type','Authorization'], expose_headers=['X-Sillage-Preview'])

@app.exception_handler(RequestValidationError)
async def invalid_request(request, exc):
    return JSONResponse(status_code=422, content={'detail':'Invalid request data.'})

@app.exception_handler(Exception)
async def unexpected_error(request, exc):
    logging.getLogger(__name__).error('Unhandled request error', exc_info=(type(exc),exc,exc.__traceback__))
    return JSONResponse(status_code=500, content={'detail':'Internal server error'})

def catalog(response, operation, fallback):
    try:
        if db.pool is None:
            raise HTTPException(503,'Database unavailable')
        result = operation()
    except HTTPException as exc:
        if exc.status_code != 503:
            raise
        result = fallback()
        response.headers['X-Sillage-Preview'] = '1'
    response.headers['Cache-Control'] = 'no-store'
    return result

def preview_one(perfume_id):
    for p in preview.list_perfumes():
        if p['id'] == perfume_id:
            return p
    raise HTTPException(404,'Perfume not found.')

@app.get('/')
def home():
    return {'message':'Welcome to Sillage PH','website':'/catalog','docs':'/docs','schema':'/schema'}

@app.get('/health')
def health():
    try:
        db.health()
    except Exception:
        raise HTTPException(503,'Database unavailable') from None
    return {'status':'ok','database':'connected'}

@app.get('/perfumes')
def list_perfumes(response: Response, gender: Gender | None = None, scent_family: Family | None = None, sort: Sort | None = None):
    args = dict(gender=gender,scent_family=scent_family,sort=sort)
    records = catalog(response,lambda:db.list_perfumes(**args),lambda:preview.list_perfumes(**args))
    return {'count':len(records),'perfumes':records}

@app.get('/perfumes/search')
def search(response: Response,q: str = Query(...,min_length=1,max_length=100)):
    q = q.strip()
    if not q: raise HTTPException(422,'Enter a search term.')
    records = catalog(response,lambda:db.list_perfumes(query=q),lambda:preview.list_perfumes(query=q))
    return {'query':q,'count':len(records),'results':records}

@app.get('/perfumes/compare')
def compare(response: Response,ids: str = Query(...,max_length=100)):
    try: wanted = [int(v) for v in ids.split(',')]
    except ValueError: raise HTTPException(422,'Choose 2 or 3 distinct integer IDs.') from None
    if not 2 <= len(wanted) <= 3 or len(set(wanted)) != len(wanted) or any(i <= 0 or i > 2147483647 for i in wanted):
        raise HTTPException(422,'Choose 2 or 3 distinct positive integer IDs.')
    records = catalog(response,lambda:db.compare(wanted),lambda:[preview_one(i) for i in wanted])
    return {'count':len(records),'perfumes':records}

@app.get('/perfumes/{perfume_id}')
def get_perfume(perfume_id:int,response:Response):
    if not 0 < perfume_id <= 2147483647: raise HTTPException(404,'Perfume not found.')
    return catalog(response,lambda:db.get_perfume(perfume_id),lambda:preview_one(perfume_id))

@app.post('/perfumes',status_code=201)
def create(body:PerfumeInput,user=Depends(auth.require_admin)):
    return db.create(body.model_dump(mode='json'),user['id'])

@app.put('/perfumes/{perfume_id}')
def replace(perfume_id:int,body:PerfumeInput,user=Depends(auth.require_admin)):
    if not 0 < perfume_id <= 2147483647: raise HTTPException(404,'Perfume not found.')
    return db.replace(perfume_id,body.model_dump(mode='json'))

@app.delete('/perfumes/{perfume_id}',status_code=204)
def delete(perfume_id:int,user=Depends(auth.require_admin)):
    if not 0 < perfume_id <= 2147483647: raise HTTPException(404,'Perfume not found.')
    db.delete(perfume_id)
    return Response(status_code=204)

@app.post('/auth/signup')
def signup(body:SignupInput): return auth.signup(body.email,body.password)

@app.post('/auth/login')
def login(body:LoginInput,response:Response):
    response.headers['Cache-Control']='no-store'
    return auth.login(body.email,body.password)

@app.get('/auth/me')
def me(response:Response,user=Depends(auth.current_user)):
    response.headers['Cache-Control']='no-store'
    return user

@app.get('/auth/favorites')
def favorites(response:Response,user=Depends(auth.current_user)):
    response.headers['Cache-Control']='no-store'
    return {'perfumes':db.favorites(user['id'])}

@app.put('/auth/favorites/{perfume_id}',status_code=204)
def add_favorite(perfume_id:int,user=Depends(auth.current_user)):
    if not 0 < perfume_id <= 2147483647: raise HTTPException(404,'Perfume not found.')
    db.favorites(user['id'],perfume_id,'PUT')
    return Response(status_code=204)

@app.delete('/auth/favorites/{perfume_id}',status_code=204)
def remove_favorite(perfume_id:int,user=Depends(auth.current_user)):
    if not 0 < perfume_id <= 2147483647: raise HTTPException(404,'Perfume not found.')
    db.favorites(user['id'],perfume_id,'DELETE')
    return Response(status_code=204)

FRONTEND=Path(__file__).resolve().parents[1]/'frontend'
PAGES={'catalog':'index.html','quiz':'quiz.html','compare':'compare.html','perfume':'perfume.html','login':'login.html','account':'account.html','admin':'admin.html','schema':'schema.html'}
ASSETS=set(PAGES.values()) | {'style.css','config.js','app.js','quiz.js','compare.js','perfume.js','session.js','login.js','dashboard.js','schema.js','schema.css'}
@app.get('/{filename}',include_in_schema=False)
def frontend(filename:str):
    filename=PAGES.get(filename,filename)
    if filename not in ASSETS: raise HTTPException(404,'Not found.')
    return FileResponse(FRONTEND/filename)
