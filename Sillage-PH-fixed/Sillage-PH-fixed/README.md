# Sillage PH — reconciled project

This package reconstructs the missing API router and aligns the application with the five-table Supabase schema supplied by the project owner. It retains the existing catalogue, comparison, quiz, account and admin interfaces and adds an interactive ERD at `/schema`.

## Quick start (Windows PowerShell)

Open this extracted folder in VS Code, then run:

```powershell
py -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements-dev.txt
.\.venv\Scripts\python -m uvicorn index:app --reload
```

Visit http://127.0.0.1:8000/catalog and http://127.0.0.1:8000/schema. Without a configured database, the 25 original records are served as an explicitly labeled **read-only preview**. Health returns 503 and account features do not simulate success.

## Connect the existing Supabase database

1. Back up your existing project (including catalogue, roles and favorites). In the Supabase SQL Editor, run **only `sql/02_reconcile.sql`** on the existing project. For a new empty project, run `sql/schema.sql` first, then `sql/02_reconcile.sql`. Never rerun the original non-idempotent schema on an existing database. If reconciliation fails, do not force it or drop data; inspect the error. Duplicate brand/name records must be resolved manually. The migration merges any legacy `public.favorites` into `public.perfume_favorites`, moves the legacy table into a restricted archive schema, syncs account profiles and roles, adds constraints and RLS. It explicitly changes deletion actions; review them before running.
2. Run `sql/03_verify.sql`. Confirm the five tables, seven foreign keys, seven scent families, and zero missing profiles/roles. Compare catalogue and favorite counts to your backup. Check existing triggers, grants and policies for unexpected custom rules. The migration assumes the names/types in your supplied schema and the original project; it is not a general repair script for arbitrary databases.
3. In Supabase, enable email signup and configure the Auth Site URL to your login page. Confirm email as required. The trigger creates a profile and a default user role; existing admin roles are retained. Promote your own confirmed account in the SQL Editor by substituting your real email:

   ```sql
   UPDATE public.app_user_roles r SET role='admin'
   FROM auth.users a WHERE r.user_id=a.id AND a.email='YOUR_ADMIN_EMAIL';
   ```

4. Set a password privately for the dedicated `sillage_api` PostgreSQL login if it has no working password. Use a trusted admin client and its password prompt (e.g. psql `\password sillage_api`); never put it into committed SQL. Use the Supabase **transaction pooler** connection string with the dedicated role username (`sillage_api.<project-ref>`) and its password, not the postgres owner or a Supabase API key. URL-encode special characters in the password. Copy `.env.example` to `.env`, fill the connection URL and Auth project URL and publishable/anon key privately. Do not expose the database URL to frontend JavaScript. Leave `ALLOWED_ORIGINS` empty for same-origin hosting.
5. Restart Uvicorn. Check `/health` returns 200 and `/perfumes` returns current records without `X-Sillage-Preview`. Only for an empty catalogue or intentionally adding missing original records, run `python seed.py` from the configured environment. The seed preserves existing conflicting records and supports GENERATED ALWAYS identity.
6. Test signup, login, favorites across two separate accounts, admin create/update/delete using a temporary perfume. `/schema` shows the target migrated ERD, not live introspection. API docs are at `/docs`.

## Deploy on Vercel

Use this folder as project root; FastAPI framework. Set DATABASE_URL, SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY (or SUPABASE_ANON_KEY), and optionally ALLOWED_ORIGINS in Production environment settings, then redeploy. Confirm Auth Site URL for the deployed login page. Do not upload `.env`.

## Verification

```powershell
.\.venv\Scripts\python -m unittest discover -s tests -p "test_*.py" -v
```

The no-database contract suite alone can run with `requirements-preview.txt` and `python -m unittest discover -s tests -p test_preview.py -v`. Live tests require private credentials for three different confirmed test accounts: `TEST_ADMIN_EMAIL/PASSWORD`, `TEST_USER_EMAIL/PASSWORD`, `TEST_OTHER_EMAIL/PASSWORD`, optionally `API_BASE_URL` and `TEST_RESTART_PAUSE=1`. Run `python tests/run_api_tests.py` only after configuring the database. Do not commit those values. The runner creates a unique temporary perfume and cleans it up.

See `docs/CHANGELOG.md` and `docs/verified-local.txt` for this package's actual test results. The old documentation and original migration examples are preserved in `docs/history/` for reference, not current setup instructions. Live database migration, Supabase authentication and Vercel deployment have not been verified in this environment.
