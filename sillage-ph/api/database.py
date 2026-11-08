"""Parameterized PostgreSQL operations. No catalogue records are cached."""
import logging
import os
from contextlib import contextmanager
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from fastapi import HTTPException
from psycopg import sql
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from psycopg_pool import ConnectionPool, PoolTimeout

from .models import PerfumeInput

load_dotenv(Path(__file__).resolve().parent.parent / '.env')
logger = logging.getLogger(__name__)
FIELDS = tuple(PerfumeInput.model_fields)
JSON_FIELDS = {'where_to_buy', 'other_stores'}
url = os.getenv('DATABASE_URL', '')
# Supavisor transaction mode requires prepared statements to be disabled.
pool = ConnectionPool(url, min_size=0, max_size=3, open=True,
    timeout=8, reconnect_timeout=5,
    kwargs={'prepare_threshold': None, 'row_factory': dict_row,
            'connect_timeout': 5, 'sslmode': 'require'},
    check=ConnectionPool.check_connection) if url else None


@contextmanager
def connection():
    if pool is None:
        raise HTTPException(503, 'Database unavailable')
    try:
        with pool.connection() as conn:
            # Transaction-local settings work with Supavisor transaction pooling.
            conn.execute("SET LOCAL statement_timeout = '8s'")
            yield conn
    except psycopg.errors.UniqueViolation:
        raise HTTPException(409, 'A perfume with this brand and name already exists.') from None
    except (psycopg.OperationalError, psycopg.InterfaceError, PoolTimeout):
        logger.exception('Database connection failed')
        raise HTTPException(503, 'Database unavailable') from None
    except psycopg.Error:
        logger.exception('Database query failed')
        raise HTTPException(500, 'Internal server error') from None


def values(data):
    return [Jsonb(data[k]) if k in JSON_FIELDS else data[k] for k in FIELDS]


def health():
    with connection() as conn:
        # Query the application table, verifying schema and access as well as connectivity.
        conn.execute('SELECT id FROM public.perfumes LIMIT 1').fetchall()


def list_perfumes(gender=None, scent_family=None, sort=None, query=None):
    clauses, params = [], []
    for field, value in [('gender', gender), ('scent_family', scent_family)]:
        if value:
            clauses.append(sql.SQL('{} = %s').format(sql.Identifier(field)))
            params.append(value)
    if query:
        clauses.append(sql.SQL('strpos(lower(search_text), lower(%s)) > 0'))
        params.append(query)
    order = sql.SQL('price_php_min DESC, id') if sort == 'price_desc' else sql.SQL('price_php_min, id') if sort else sql.SQL('id')
    statement = sql.SQL('SELECT {} FROM public.perfumes').format(columns())
    if clauses:
        statement += sql.SQL(' WHERE ') + sql.SQL(' AND ').join(clauses)
    with connection() as conn:
        return conn.execute(statement + sql.SQL(' ORDER BY ') + order, params).fetchall()


def columns():
    return sql.SQL(', ').join(map(sql.Identifier, ('id', *FIELDS)))


def get_perfume(perfume_id):
    with connection() as conn:
        record = conn.execute(sql.SQL('SELECT {} FROM public.perfumes WHERE id=%s').format(columns()), (perfume_id,)).fetchone()
    if record is None:
        raise HTTPException(404, 'Perfume not found.')
    return record


def compare(ids):
    with connection() as conn:
        records = conn.execute(sql.SQL('SELECT {} FROM public.perfumes WHERE id = ANY(%s)').format(columns()), (ids,)).fetchall()
    by_id = {r['id']: r for r in records}
    if any(i not in by_id for i in ids):
        raise HTTPException(404, 'Perfume not found.')
    return [by_id[i] for i in ids]


def create(data):
    statement = sql.SQL('INSERT INTO public.perfumes ({}) VALUES ({}) RETURNING {}').format(
        sql.SQL(', ').join(map(sql.Identifier, FIELDS)), sql.SQL(', ').join(sql.Placeholder() for _ in FIELDS), columns())
    with connection() as conn:
        return conn.execute(statement, values(data)).fetchone()


def replace(perfume_id, data):
    assignments = sql.SQL(', ').join(sql.SQL('{}=%s').format(sql.Identifier(k)) for k in FIELDS)
    with connection() as conn:
        record = conn.execute(sql.SQL('UPDATE public.perfumes SET {} WHERE id=%s RETURNING {}').format(assignments, columns()), [*values(data), perfume_id]).fetchone()
    if record is None:
        raise HTTPException(404, 'Perfume not found.')
    return record


def delete(perfume_id):
    with connection() as conn:
        record = conn.execute('DELETE FROM public.perfumes WHERE id=%s RETURNING id', (perfume_id,)).fetchone()
    if record is None:
        raise HTTPException(404, 'Perfume not found.')
