# 5 Implementation Details

> Current status: the cloud project is now accessible and 25 records are seeded. See [cloud verification update](../cloud-verification.md) for verified results and the remaining private connection setup. Earlier statements below describe the initial implementation session.


## 5.1 Database connection

api/database.py creates one module-level Psycopg pool from DATABASE_URL. It uses TLS, bounded connection counts, timeouts and no prepared statements. The intended URI is Supavisor transaction mode. Health checks application-table access, not merely process availability:

```python
with connection() as conn:
    conn.execute('SELECT id FROM public.perfumes LIMIT 1').fetchall()
```

No database URL was supplied, so local health correctly reports unavailable.

[SCREENSHOT: /health connected against Supabase]

## 5.2 Data model and initial records

api/models.py validates full input. seed_data.py contains the original 25 records and helpers; api/ does not import it. seed.py locks the table, inserts original IDs with ON CONFLICT DO NOTHING and advances the identity sequence without moving it backwards. All 25 records pass model validation locally. Real seed execution and repeatability remain pending.

## 5.3 CRUD and search

Routes delegate to list_perfumes, get_perfume, compare, create, replace and delete in the database module. Filtering, ordering and search execute as SQL. Identity generation avoids max-ID races. PUT replaces the complete input; omitted optional other_stores becomes []. DELETE RETURNING distinguishes absence from success. Compare preserves requested order and permits two or three distinct IDs. Only public columns are selected, excluding internal search_text.

## 5.4 Validation and errors

Models reject unknown fields, malformed bodies, empty strings and wrong types. They validate enums, HTTPS URLs, lengths, list counts, year and price. SQL also constrains domain values. Invalid requests return 422, uniqueness conflicts 409, unreachable connections 503 and unexpected failures generic 500. Traces remain in private server logs.

## 5.5 Security

```python
expected = os.getenv('ADMIN_API_KEY', '')
if not expected or not x_api_key or not secrets.compare_digest(x_api_key.encode(), expected.encode()):
    raise HTTPException(401, 'Invalid or missing API key.')
```

POST, PUT and DELETE use this dependency. RLS permits only the backend login; anon/authenticated grants are revoked. Browser code receives no database credentials. See the security assessment and deployment guide for configuration and limitations.

[SCREENSHOT: RLS restricted to sillage_api with secrets hidden]

## 5.6 Frontend integration

Frontend files remain unchanged. Responses retain count/perfumes, query/count/results and single-perfume formats. Original frontend path resolution is correct. Root index.py exports the app for Vercel and local uvicorn. All four pages and allowlisted assets pass HTTP delivery checks, and JavaScript syntax checks pass. Database-backed browser execution and console inspection still require configured Supabase and a browser.
