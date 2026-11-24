"""Sillage PH database-backed API."""
import logging
import os
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query, Response, Path as PathParam
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from . import database as db
from .models import PerfumeInput, Gender, Family, Sort, LoginInput, SignupInput
from .auth import current_user, require_admin, login as auth_login, signup as auth_signup

app = FastAPI(title="Sillage PH Perfume API", version="3.0.0")
app.add_middleware(CORSMiddleware,
    allow_origins=[o.strip() for o in os.getenv('ALLOWED_ORIGINS', '').split(',') if o.strip() and o.strip() != '*'],
    allow_credentials=False, allow_methods=['GET', 'POST', 'PUT', 'DELETE'],
    allow_headers=['Content-Type', 'Authorization'], expose_headers=['X-Sillage-Preview'])

@app.exception_handler(RequestValidationError)
async def invalid_request(request, exc):
    return JSONResponse(status_code=422, content={'detail': 'Invalid request data.'})

@app.exception_handler(Exception)
async def unexpected_error(request, exc):
    logging.getLogger(__name__).error('Unhandled request error', exc_info=(type(exc), exc, exc.__traceback__))
    return JSONResponse(status_code=500, content={'detail': 'Internal server error'})

@app.post('/auth/login', tags=['Accounts'])
def sign_in(body: LoginInput):
    return auth_login(body.email, body.password)

@app.post('/auth/signup', status_code=201, tags=['Accounts'])
def sign_up(body: SignupInput):
    return auth_signup(body.email, body.password)


@app.get('/auth/favorites', tags=['Favorites'])
def list_favorites(user=Depends(current_user)):
    return {'perfumes': db.favorites(user['id'])}


@app.put('/auth/favorites/{perfume_id}', status_code=204, tags=['Favorites'])
def save_favorite(perfume_id: int = PathParam(ge=1, le=2147483647), user=Depends(current_user)):
    db.favorites(user['id'], perfume_id, 'PUT')
    return Response(status_code=204)


@app.delete('/auth/favorites/{perfume_id}', status_code=204, tags=['Favorites'])
def remove_favorite(perfume_id: int = PathParam(ge=1, le=2147483647), user=Depends(current_user)):
    db.favorites(user['id'], perfume_id, 'DELETE')
    return Response(status_code=204)


@app.get('/auth/me', tags=['Accounts'])
def account_info(user=Depends(current_user)):
    return user

@app.get('/')
def home():
    return {'message': 'Welcome to Sillage PH', 'endpoints': ['/perfumes', '/perfumes/search?q=', '/perfumes/compare?ids=1,2,3', '/perfumes/{perfume_id}'], 'website': '/catalog', 'docs': '/docs'}

@app.get('/health')
def health():
    try:
        db.health()
    except Exception:
        logging.getLogger(__name__).exception('Database health check failed')
        raise HTTPException(503, 'Database unavailable') from None
    return {'status': 'ok', 'database': 'connected'}

def catalog_records(response, **filters):
    if db.pool is not None:
        return db.list_perfumes(**filters)
    from . import preview
    response.headers['X-Sillage-Preview'] = '1'
    return preview.list_perfumes(**filters)


def selected_records(response, ids):
    if db.pool is not None:
        return db.compare(ids)
    records = {p['id']: p for p in catalog_records(response)}
    if any(perfume_id not in records for perfume_id in ids):
        raise HTTPException(404, 'Perfume not found.')
    return [records[perfume_id] for perfume_id in ids]


@app.get('/perfumes')
def get_perfumes(response: Response, gender: Gender | None = None, scent_family: Family | None = None, sort: Sort | None = None):
    records = catalog_records(response, gender=gender, scent_family=scent_family, sort=sort)
    return {'count': len(records), 'perfumes': records}

@app.get('/perfumes/search')
def search_perfumes(response: Response, q: str = Query(..., min_length=1, max_length=100)):
    if not q.strip():
        raise HTTPException(422, 'Enter at least one non-space character.')
    records = catalog_records(response, query=q.strip())
    return {'query': q.strip(), 'count': len(records), 'results': records}

# Named routes must precede the integer id route.
@app.get('/perfumes/compare')
def compare_perfumes(response: Response, ids: str = Query(..., max_length=100)):
    try:
        wanted = [int(i) for i in ids.split(',') if i.strip()]
    except ValueError:
        raise HTTPException(422, 'ids must be whole numbers separated by commas.') from None
    if not 2 <= len(wanted) <= 3 or len(set(wanted)) != len(wanted):
        raise HTTPException(422, 'Choose 2 or 3 different perfumes.')
    return {'count': len(wanted), 'perfumes': selected_records(response, wanted)}

@app.get('/perfumes/{perfume_id}')
def get_perfume(perfume_id: int, response: Response):
    if db.pool is not None:
        return db.get_perfume(perfume_id)
    return selected_records(response, [perfume_id])[0]

@app.post('/perfumes', status_code=201, dependencies=[Depends(require_admin)])
def create_perfume(body: PerfumeInput):
    return db.create(body.model_dump(mode='json'))

@app.put('/perfumes/{perfume_id}', dependencies=[Depends(require_admin)])
def replace_perfume(perfume_id: int, body: PerfumeInput):
    return db.replace(perfume_id, body.model_dump(mode='json'))

@app.delete('/perfumes/{perfume_id}', status_code=204, dependencies=[Depends(require_admin)])
def delete_perfume(perfume_id: int):
    db.delete(perfume_id)
    return Response(status_code=204)

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"

# Pretty page URLs -> file
PAGES = {"/catalog": "index.html", "/quiz": "quiz.html", "/compare": "compare.html", "/perfume": "perfume.html", "/login": "login.html", "/account": "account.html", "/admin": "admin.html", "/schema": "schema.html"}

# Files the pages are allowed to load (anything else is a 404)
STATIC_FILES = {
    "index.html": "text/html", "quiz.html": "text/html", "compare.html": "text/html", "perfume.html": "text/html", "login.html": "text/html",
    "account.html": "text/html", "admin.html": "text/html", "schema.html": "text/html",
    "session.js": "application/javascript", "dashboard.js": "application/javascript",
    "style.css": "text/css",
    "config.js": "application/javascript", "app.js": "application/javascript",
    "quiz.js": "application/javascript", "compare.js": "application/javascript",
    "perfume.js": "application/javascript", "login.js": "application/javascript",
}


def _make_page_route(filename):
    return lambda: FileResponse(FRONTEND / filename)


for _path, _file in PAGES.items():
    app.add_api_route(_path, _make_page_route(_file), methods=["GET"], include_in_schema=False)


@app.get("/{filename}", include_in_schema=False)
def static_file(filename: str):
    if filename not in STATIC_FILES:
        raise HTTPException(status_code=404, detail="Not found.")
    return FileResponse(FRONTEND / filename, media_type=STATIC_FILES[filename])
