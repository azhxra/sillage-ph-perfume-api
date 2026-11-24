# Existing API assessment

Sillage PH compares designer perfumes with affordable Philippine inspired alternatives. The original catalogue contains 25 perfumes with notes, fragrance characteristics, prices, a primary seller and alternative sellers. Records were constructed in `api/index.py` using `ian_darcy()`, `cg_scent()` and `cg_alt()`, sorted by ID and scanned in Python. There were no write routes or authentication. Runtime edits would disappear on restart or serverless cold start, while permanent changes required source edits and redeployment. Data and route code were mixed.

The original already included numeric `price_php_min` alongside display text `dupe_price_php`; numeric prices are not a new field in this migration.

The actual app root is `sillage-ph-perfume-api-main/sillage-ph` beneath the supplied workspace. Python lives in `api/`, with HTML/CSS/JavaScript in `frontend/`. The original `Path(__file__).resolve().parent.parent / "frontend"` is correct. `vercel.json` selects FastAPI. Originally requirements.txt contained only FastAPI and Uvicorn. The supplied archive has no .git directory.

| Method | Original path | Purpose and parameters | Response | Migration |
|---|---|---|---|---|
| GET | / | Welcome; no parameters | message, endpoints, website, docs | Retained |
| GET | /perfumes | Entire catalogue; originally no filters | count, perfumes[] | Modified: SQL; optional gender, scent_family, sort |
| GET | /perfumes/search | Required q, 1–100 characters | query, count, results[] | Modified: SQL search |
| GET | /perfumes/compare | Required ids, 2 or 3 distinct integers | count, perfumes[] in requested order | Modified: SQL |
| GET | /perfumes/{perfume_id} | Integer identifier | Single perfume or 404 | Modified: SQL |
| GET | /catalog, /quiz, /compare, /perfume | Pretty page URLs | HTML | Retained |
| GET | /{filename} | Allowlisted frontend filename | File or 404 | Retained |
| GET | /docs, /redoc, /openapi.json | Framework documentation | HTML / JSON | Retained |
| GET | /health | Real table query | status/database or 503 | New |
| POST | /perfumes | Full validated body, X-API-Key | 201 perfume | New |
| PUT | /perfumes/{perfume_id} | Full replacement, X-API-Key | 200 perfume or 404 | New |
| DELETE | /perfumes/{perfume_id} | ID, X-API-Key | 204 or 404 | New |

Database operations now live in `api/database.py`, validation in `api/models.py`, and the manual initial catalogue in `seed_data.py`. Only the seed loader and tests import the catalogue. Public response envelopes and nested seller fields remain compatible. The unchanged browser uses same-origin requests through frontend/config.js.
