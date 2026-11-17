# Sillage PH — 2 accounts (Admin + User)

This add-on is based on the repaired project and keeps all existing perfume functionality. It does not create your real accounts or deploy them: complete the steps below using your own Supabase/Vercel dashboards.

## 1. Create the role table

In **Supabase Dashboard > SQL Editor**, run `user_roles.sql`. Do **not** rerun `schema.sql` against an existing database. The migration creates `public.app_user_roles` alongside `public.perfumes`. Passwords are NOT stored here; only a UUID and `admin`/`user` role.

## 2. Create two REAL Auth users

In **Supabase Dashboard > Authentication > Users > Add user**:
- Create an admin account with an email you control and a strong unique password.
- Create a separate regular-user account with a different email and password.
- Ensure both accounts can sign in (verify/confirm email if required).

Then return to SQL Editor. Run the role assignments at the end of `user_roles.sql` **after replacing** `YOUR_ADMIN_EMAIL` and `YOUR_USER_EMAIL` with your accounts' real addresses and removing the leading `--` comment markers. The quoted placeholders are NOT real emails.

Run the optional verification query to confirm one `admin` and one `user`. Never share your passwords, tokens, or connection URLs.

## 3. Configure the server

In Vercel > Project > Settings > Environment Variables (Production), configure:
- `DATABASE_URL`: existing working server-side PostgreSQL connection URL as `sillage_api` or other role with `SELECT` permission on `public.app_user_roles`.
- `SUPABASE_URL`: e.g. `https://your-project-ref.supabase.co`.
- `SUPABASE_PUBLISHABLE_KEY`: Supabase public/publishable API key. Alternatively use `SUPABASE_ANON_KEY` for a legacy anon key. **Never put a secret/service-role key in these fields or in frontend source.**
- `ALLOWED_ORIGINS`: for separate web origins if needed (same-origin does not need CORS).

The account verification uses Supabase Auth with the public project key and the user's access token. Role authorization uses a server-side query to the protected `app_user_roles` table, **not** user-editable metadata or a role supplied by the browser.

Your `schema.sql` creates database role `sillage_api` but does not set a password. Make sure your `DATABASE_URL` actually authenticates to PostgreSQL and can SELECT the `public.perfumes` and `public.app_user_roles` tables. If you already use a different backend database role, apply the SELECT grant and RLS policy to that role appropriately.

**Redeploy** to make new server-side settings active. Environment variables changed after a deployment do not retroactively update the old deployment.

## 4. Use the new website login page

Go to `https://sillage-ph.vercel.app/login` after deploying, or run locally using uvicorn and open `http://127.0.0.1:8000/login`.

Log in with each account. The page shows the role. It stores an access token in tab `sessionStorage` for the demo (not the password); after expiration you will need to sign in again.

### Demonstrate the difference between roles

1. Open `/docs` (FastAPI Swagger UI). Click **Authorize**; use the copied token from `/login` as a Bearer token.
2. Admin: `POST /perfumes` with valid body should return 201. `PUT /perfumes/{id}` and `DELETE /perfumes/{id}` are also allowed.
3. Regular user: the same POST, PUT, DELETE calls should return 403 `Administrator access required.`
4. No token: writes should return 401 `Sign in to use this endpoint.`
5. Both accounts can call `GET /perfumes`, search, and comparison. Anonymous visitors can still browse, as before.
6. Create a **temporary test perfume** rather than deleting or modifying your seeded 25 original perfumes. Confirm it appears, update it, and delete it.

The login page allows copying a session token for an API demonstration. A bearer token grants access until it expires, so do not paste it into public reports, commit it, or share it with classmates. Removing a token from sessionStorage signs out the browser tab but does not instantly revoke a previously copied token.

## Important distinctions

- **Supabase Auth users** = actual people who log in, with email/password managed by Supabase.
- **`public.app_user_roles`** = each Auth user's *application* privilege (`admin` or `user`).
- **`sillage_api` PostgreSQL role** = the backend's database connection identity; it is **not** a human login.
- The old `ADMIN_API_KEY` approach was removed from write-route authorization in the modified API. Remove that unused variable from Vercel when your migration is complete. This is a change to the write authentication scheme.

## Files changed

- `api/auth.py` (NEW): Supabase Auth sign-in/token verification and app-role authorization.
- `api/index.py`: `/auth/login`, `/auth/me` and Bearer-protected POST/PUT/DELETE.
- `api/models.py`: login request validation.
- `api/database.py`: role lookup via parameterized SQL.
- `user_roles.sql` (NEW): non-destructive roles-table migration.
- `frontend/login.html`, `frontend/login.js` (NEW): sign-in, status, sign-out, token copy for demos.
- `frontend/*.html`, `style.css`: add sign-in links and styling.

## Testing caveat

The code was syntax-checked and the route/authorization contract can be tested with mocks. Actual authentication, database privileges, live CRUD, and deployment must be checked in **your own** Supabase/Vercel environments.
