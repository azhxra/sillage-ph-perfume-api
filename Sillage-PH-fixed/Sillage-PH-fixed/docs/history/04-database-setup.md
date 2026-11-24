# Supabase setup

> Current status: the cloud project is now accessible and 25 records are seeded. See [cloud verification update](cloud-verification.md) for verified results and the remaining private connection setup. Earlier statements below describe the initial implementation session.


Cloud setup is left to you as requested. The connected account returned no projects. No cloud tables, roles or data were created here.

1. Open [Supabase Dashboard](https://supabase.com/dashboard), select your intended organization and create a project in a suitable region. Review any quoted cost first. Set the database password privately and wait for a healthy project. For an existing project, inspect and back up relevant data first.
2. Open SQL Editor. Review and run `sql/schema.sql` once as administrator. It creates the table, indexes, search trigger, RLS and sillage_api login in a transaction. It intentionally fails instead of replacing existing tables or roles. If names already exist, inspect and adapt the schema first.
3. Set a strong password for sillage_api privately using a trusted PostgreSQL administrative client and `\password sillage_api`, which prompts without embedding a secret in saved SQL. Use the database role management UI if it supports password changes. Do not save password literals in source, chat, SQL Editor history or shell command history. The new role cannot log in until its password is set.
4. Click Connect in the dashboard and select **Transaction pooler** (Supavisor, normally port 6543). Copy its URI privately. Replace the username with `sillage_api.<project-reference>` and use that role's password, URL-encoding special characters. Preserve the dashboard-provided host, port and database. Do not use the direct IPv6 connection or a Supabase API key as the database password.
5. From the app root containing requirements.txt, copy .env.example to .env. Set DATABASE_URL privately to the pooled URI, ADMIN_API_KEY to an independent random secret of at least 32 random bytes, and ALLOWED_ORIGINS to exact local/deployed browser origins. Never place these secrets in frontend/config.js. API_BASE_URL configures the external test runner.
6. Install Python 3.12 or newer, create a virtual environment and install the locked dependencies:

   ```powershell
   python -m venv .venv
   python -m pip --python .venv install -r requirements-lock.txt
   ```

   If ensurepip fails but the environment interpreter exists, the base interpreter's pip can still install into it with `--python .venv`. That fallback worked during this implementation.
7. Run `.\.venv\Scripts\python seed.py` twice before public traffic. It validates all original records, locks the table, inserts original IDs, skips conflicts, preserves edited rows and advances the identity sequence without moving it backwards. Existing conflicting IDs or brand/name pairs are skipped; inspect the results on a prepopulated table.
8. Run `.\.venv\Scripts\python -m uvicorn index:app --reload`. In another terminal run `curl.exe -i http://127.0.0.1:8000/health` and `curl.exe http://127.0.0.1:8000/perfumes`. Healthy output is 200 with `{"status":"ok","database":"connected"}` after a real application-table query. Missing configuration or failed schema access returns 503 with `{"detail":"Database unavailable"}`.
9. In Table Editor, verify all 25 seed records. Inspect RLS and grants: anon/authenticated must have no table access, while only the backend login has the backend policy. Run Supabase Security and Performance Advisors. Do not disable RLS to resolve an access error.
10. Run `.\.venv\Scripts\python tests/run_api_tests.py`. Then set `$env:TEST_RESTART_PAUSE='1'` and rerun. Restart/redeploy at each prompt and press Enter when reachable. The runner only updates/deletes records it created and attempts cleanup in finally. Prefer a development database.

The backend role has table CRUD and sequence permissions needed for seeding, without schema or role administration. After initial seeding an administrator may revoke sequence UPDATE (retain USAGE and SELECT), granting it temporarily for later seed runs. No service-role API key is needed for this direct PostgreSQL integration. Never use a database password as the API write key.

[SCREENSHOT: healthy Supabase project with connection strings and passwords hidden]
[SCREENSHOT: perfumes schema, indexes, RLS and seeded rows]
[SCREENSHOT: successful real database health response]
