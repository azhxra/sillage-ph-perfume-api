-- Run AFTER schema.sql, in the Supabase SQL Editor as project administrator.
-- Authentication passwords live in Supabase Auth, NOT this table.
-- This migration is safe to run against an existing perfume database.
BEGIN;
CREATE TABLE IF NOT EXISTS public.app_user_roles (
    user_id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    role text NOT NULL CHECK (role IN ('admin', 'user')),
    created_at timestamptz NOT NULL DEFAULT now()
);
ALTER TABLE public.app_user_roles ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.app_user_roles FROM PUBLIC, anon, authenticated;
GRANT SELECT ON public.app_user_roles TO sillage_api;
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies
                   WHERE schemaname = 'public' AND tablename = 'app_user_roles'
                   AND policyname = 'api_can_read_roles') THEN
       CREATE POLICY api_can_read_roles ON public.app_user_roles
           FOR SELECT TO sillage_api USING (true);
    END IF;
END $$;
COMMIT;

-- Create two accounts in Supabase Dashboard > Authentication > Users > Add user.
-- THEN run the statements below with YOUR real emails (not example values).
-- Only administrators of the database should run these SQL statements.

-- INSERT INTO public.app_user_roles (user_id, role)
-- SELECT id, 'admin' FROM auth.users WHERE email = 'YOUR_ADMIN_EMAIL'
-- ON CONFLICT (user_id) DO UPDATE SET role = EXCLUDED.role;

-- INSERT INTO public.app_user_roles (user_id, role)
-- SELECT id, 'user' FROM auth.users WHERE email = 'YOUR_USER_EMAIL'
-- ON CONFLICT (user_id) DO UPDATE SET role = EXCLUDED.role;

-- Verify assigned roles without exposing password hashes:
-- SELECT u.email, r.role FROM public.app_user_roles AS r
-- JOIN auth.users AS u ON u.id = r.user_id;
