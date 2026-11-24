# Local verification results

Executed 2026-11-08 (Asia/Manila). Ten unittest contract tests passed in 0.222 seconds (final rerun) using approved local execution. Successful database operations were mocked. All 25 original seed records validated. All six frontend JavaScript files passed node --check; Python compileall passed. No configured cloud database was used.

Command: `.\.venv\Scripts\python -m unittest discover -s tests -p test_local.py -v`

Test methods: seed validation/uniqueness; frontend delivery; fail-closed writes; invalid bodies; query and named routes; validated write delegation; clean failure responses; database exception translation; parameterized search; CORS denial.

## Real HTTP smoke checks

A local uvicorn index:app process was started on port 8765 without reload and stopped after these curl checks. Database operations correctly fail with 503 because DATABASE_URL is absent; these are failure-path passes, not database integration successes.

| Request | Expected | Actual | Result |
|---|---|---|---|
| GET / | 200 | 200 | PASS |
| GET /catalog | 200 | 200 | PASS |
| GET /perfume?id=1 | 200 | 200 | PASS |
| GET /compare?ids=1,2 | 200 | 200 | PASS |
| GET /quiz | 200 | 200 | PASS |
| GET /health | 503 | 503 | PASS |
| GET /perfumes | 503 | 503 | PASS |
| GET /perfumes/search?q=Dior | 503 | 503 | PASS |
| GET /perfumes/compare?ids=1,2 | 503 | 503 | PASS |
| GET /perfumes/1 | 503 | 503 | PASS |
| POST /perfumes without key | 401 | 401 | PASS |
| PUT /perfumes/1 without key | 401 | 401 | PASS |
| DELETE /perfumes/1 without key | 401 | 401 | PASS |

Cloud schema execution, seed idempotence, real CRUD, RLS, deployment, restart persistence and browser console/data flow remain PENDING. See test-results.md for the live runner invocation, which correctly reports its blocked database prerequisite.
