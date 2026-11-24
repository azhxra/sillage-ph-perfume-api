# 7 Testing Methodology and Results

> Current status: the cloud project is now accessible and 25 records are seeded. See [cloud verification update](../cloud-verification.md) for verified results and the remaining private connection setup. Earlier statements below describe the initial implementation session.


Ten unittest/FastAPI TestClient tests passed locally. They cover validation of all 25 seeds; static/page delivery; missing/wrong/unconfigured administrator keys; malformed/invalid bodies; query and comparison rules; write delegation; safe failures; CORS; and SQL parameter binding. Successful database operations are mocked. They establish API contracts, not PostgreSQL integration. See ../local-test-results.md for executed results.

tests/run_api_tests.py uses requests against API_BASE_URL with ADMIN_API_KEY from environment/.env. It creates unique records, tests list/get/search/filter/sort/compare/update/delete, validation and unauthorized writes, then cleans up created IDs in finally. TEST_RESTART_PAUSE=1 adds manual checkpoints for live and deleted records across restart/redeploy. Default mode reports persistence as PENDING, never PASS. A failed real health query blocks cloud CRUD. See ../test-results.md for the actual invocation status.

Cloud CRUD, applied SQL constraints, repeated seeding, RLS denial, browser console behavior, deployment and persistence remain unverified. The connected account had zero projects and provider setup was left to the user. These are evidence gaps. The ten required verification checks and screenshot placements are in ../07-deployment.md.

[SCREENSHOT: full live API test output after setup]
[SCREENSHOT: independently verified create, update and deletion in Supabase]
[SCREENSHOT: surviving rows and deleted ID verified after redeploy]
