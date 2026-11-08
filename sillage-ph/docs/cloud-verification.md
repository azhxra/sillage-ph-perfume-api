# Cloud verification update

Verified on 2026-11-08 through the connected Supabase tool. This supersedes the earlier statement that no project was accessible.

- The Sillage project is active and healthy.
- public.perfumes exists and RLS is enabled.
- The 25 original records were inserted through the authenticated SQL tool using the same validated data and conflict-skipping logic as the local seed loader. The SQL was repeated and the row count remained 25. The identity sequence value is 25.
- The sillage_api role can log in, is not a superuser and does not bypass RLS. Its backend_access policy permits its table operations. The anon/authenticated roles have no table grants.
- Supabase Security Advisor returned no findings. Performance Advisor reported four unused-index informational notices on this newly created table; indexes were retained for expected filter/order queries. See [unused-index guidance](https://supabase.com/docs/guides/database/database-linter?lint=0005_unused_index).
- Attempting SET LOCAL ROLE sillage_api through the administrator tool failed because that session cannot assume the role. No role membership was granted to work around this. Seeding succeeded under the tool's existing administrator identity; this does not prove runtime-role authentication.

The FastAPI connection is still pending. A private, gitignored .env was created with an empty DATABASE_ADMIN_URL field and an independently generated API write key that was not printed. The user must fill DATABASE_ADMIN_URL privately from the dashboard's Transaction pooler connection URI, including the project database password. No publishable key or REST URL can replace that PostgreSQL URI.

After that configuration, the remaining work is to set the dedicated login's password, configure DATABASE_URL, run the actual seed.py twice, run live API CRUD tests, verify restart persistence and inspect browser data/console behavior. Deployment remains pending. Earlier local-test results are valid historical results, not a claim of completed cloud API integration.
