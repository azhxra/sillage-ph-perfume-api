# Vercel deployment and evidence

1. Set the Vercel root to the directory containing vercel.json and requirements.txt: `sillage-ph-perfume-api-main/sillage-ph` relative to the supplied workspace. Framework is FastAPI. Root index.py re-exports the app; include api/ and frontend/ in the deployment.
2. Complete database setup and real local /health verification first. Use separate development/production projects where possible.
3. In Vercel Project Settings → Environment Variables set **DATABASE_URL**, **ADMIN_API_KEY**, **ALLOWED_ORIGINS** for the intended Preview/Production environments. Enter values privately. Use the transaction-pooler URI and exact frontend origin. API_BASE_URL is only for the external runner.
4. Redeploy after setting variables. Open /, /docs and /health. Investigate any 503 using private server logs and Supabase health.
5. Set API_BASE_URL locally to the deployed HTTPS URL and run tests/run_api_tests.py with the matching private key. Set TEST_RESTART_PAUSE=1 and rerun, redeploying at both prompts. A normal GET alone does not prove restart persistence.
6. In a browser open /catalog, /perfume?id=1, /compare?ids=1,2 and /quiz. Complete a quiz and inspect console/network errors. File delivery and JavaScript syntax tests do not establish successful browser execution.

Save screenshots under docs/screenshots/ and replace the report markers. Hide all credentials, connection strings and request headers.

| Check | Action | Evidence | Report |
|---|---|---|---|
| 1 | Deployed / and /docs reachable | 01-reachable.png | 8 |
| 2 | /health connected | 02-health.png | 5.1, 8 |
| 3 | /perfumes seeded data | 03-read.png | 5.3, 7 |
| 4 | POST unique test record: 201 | 04-create.png | 5.3, 6 |
| 5 | Created ID in Supabase | 05-created-in-db.png | 7 |
| 6 | PUT changed vibe: 200 | 06-update.png | 5.3, 6 |
| 7 | Updated value in Supabase and GET | 07-updated-in-db.png | 7 |
| 8 | DELETE test ID: 204 | 08-delete.png | 5.3, 6 |
| 9 | GET 404 and row absent | 09-deleted-in-db.png | 7 |
| 10 | Redeploy: survivors unchanged, deleted ID absent | 10-persistence.png | 7, 8 |

Also capture schema/indexes/RLS, environment variable names only, test output, and all four frontend pages with a clean console. Place these in report sections 3, 5.5, 7, 8 and 13.

Deployment was not attempted: no cloud project or credentials were configured and you chose setup instructions. No deployed URL, screenshot or cloud success is claimed.
