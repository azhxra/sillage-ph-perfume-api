"""Sillage PH database-backed API."""
import logging
import os
import secrets
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from . import database as db
from .models import PerfumeInput, Gender, Family, Sort

app = FastAPI(title="Sillage PH Perfume API", version="3.0.0")
app.add_middleware(CORSMiddleware,
    allow_origins=[o.strip() for o in os.getenv('ALLOWED_ORIGINS', '').split(',') if o.strip() and o.strip() != '*'],
    allow_credentials=False, allow_methods=['GET', 'POST', 'PUT', 'DELETE'],
    allow_headers=['Content-Type', 'X-API-Key'])

@app.exception_handler(RequestValidationError)
async def invalid_request(request, exc):
    return JSONResponse(status_code=422, content={'detail': 'Invalid request data.'})

@app.exception_handler(Exception)
async def unexpected_error(request, exc):
    logging.getLogger(__name__).error('Unhandled request error', exc_info=(type(exc), exc, exc.__traceback__))
    return JSONResponse(status_code=500, content={'detail': 'Internal server error'})

def require_admin(x_api_key: Annotated[str | None, Header()] = None):
    expected = os.getenv('ADMIN_API_KEY', '')
    if not expected or not x_api_key or not secrets.compare_digest(x_api_key.encode(), expected.encode()):
        raise HTTPException(401, 'Invalid or missing API key.')

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

@app.get('/perfumes')
def get_perfumes(gender: Gender | None = None, scent_family: Family | None = None, sort: Sort | None = None):
    records = db.list_perfumes(gender, scent_family, sort)
    return {'count': len(records), 'perfumes': records}

@app.get('/perfumes/search')
def search_perfumes(q: str = Query(..., min_length=1, max_length=100)):
    if not q.strip():
        raise HTTPException(422, 'Enter at least one non-space character.')
    records = db.list_perfumes(query=q.strip())
    return {'query': q.strip(), 'count': len(records), 'results': records}

# Named routes must precede the integer id route.
@app.get('/perfumes/compare')
def compare_perfumes(ids: str = Query(..., max_length=100)):
    try:
        wanted = [int(i) for i in ids.split(',') if i.strip()]
    except ValueError:
        raise HTTPException(422, 'ids must be whole numbers separated by commas.') from None
    if not 2 <= len(wanted) <= 3 or len(set(wanted)) != len(wanted):
        raise HTTPException(422, 'Choose 2 or 3 different perfumes.')
    return {'count': len(wanted), 'perfumes': db.compare(wanted)}

@app.get('/perfumes/{perfume_id}')
def get_perfume(perfume_id: int):
    return db.get_perfume(perfume_id)

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
PAGES = {"/catalog": "index.html", "/quiz": "quiz.html", "/compare": "compare.html", "/perfume": "perfume.html"}

# Files the pages are allowed to load (anything else is a 404)
STATIC_FILES = {
    "index.html": "text/html", "quiz.html": "text/html", "compare.html": "text/html", "perfume.html": "text/html",
    "style.css": "text/css",
    "config.js": "application/javascript", "app.js": "application/javascript",
    "quiz.js": "application/javascript", "compare.js": "application/javascript",
    "perfume.js": "application/javascript",
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
