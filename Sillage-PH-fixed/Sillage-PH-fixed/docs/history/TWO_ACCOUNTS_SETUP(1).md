# Live accounts and favorites

## Supabase setup

1. For an empty database, run `sql/schema.sql` first and load the 25 bundled perfumes with `python seed.py` using the server environment. For an existing catalog, check `/health` and `/perfumes` before reseeding.
2. In the Supabase SQL Editor, run `user_roles.sql` and then `sql/favorites.sql`. These migrations can run against the existing catalog.
3. Enable email sign-ups in Supabase Auth. Set the Auth Site URL to your deployed login URL (for example, your site origin followed by /login) so confirmation emails return to the sign-in page. Confirm accounts before logging in if email confirmation is enabled.
4. Create or sign up the admin account. Assign its admin role using the commented admin statement at the end of `user_roles.sql`, after substituting the account's real email. Other verified accounts default to the user role.

## Server configuration

Set `DATABASE_URL` to the pooler URL for the existing `sillage_api` database login, `SUPABASE_URL` to the same project's URL, and `SUPABASE_PUBLISHABLE_KEY` (or `SUPABASE_ANON_KEY`) to its public Auth key. Use `ALLOWED_ORIGINS` only if the frontend is hosted separately. For local development, set these in a private `.env` at the app root. For Vercel, set them in the appropriate deployment environment and redeploy.

Open `/health` and confirm it says the database is connected. Open `/perfumes` and confirm the count is greater than zero. Without `DATABASE_URL`, the read endpoints serve a labeled seed preview and `/health` reports the missing connection. If `DATABASE_URL` is set but the database is unreachable, check the pooler address, login, and private runtime logs.

## Class demonstration

1. Open `/schema` to show how a user's ID and perfume ID become one row in `public.favorites`.
2. Go to `/catalog`, select **Add to favorites**, then create an account or sign in. Save a perfume and open **Account** to see it. Refresh the page to show the saved favorite persists.
3. Sign in as a different user and show their own favorites. Sign in as the admin to show `/admin`, which manages perfume records through a JSON editor. Use a temporary perfume to demonstrate changes.
