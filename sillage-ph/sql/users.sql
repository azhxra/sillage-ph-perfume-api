-- Run in Supabase SQL Editor as the project administrator.
-- Adds a separate public users table to the schema supplied from Supabase.
-- Does not copy passwords, change roles, or replace authentication.
BEGIN;

CREATE TABLE IF NOT EXISTS public.users (
    id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email text,
    created_at timestamptz NOT NULL DEFAULT now()
);
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
-- "public" is a schema name here, not permission to expose account emails.
REVOKE ALL ON public.users FROM PUBLIC, anon, authenticated;

CREATE OR REPLACE FUNCTION public.sillage_sync_user_profile()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
BEGIN
    INSERT INTO public.users (id, email, created_at)
    VALUES (NEW.id, NEW.email, COALESCE(NEW.created_at, now()))
    ON CONFLICT (id) DO UPDATE SET email = EXCLUDED.email;
    RETURN NEW;
END;
$$;
REVOKE ALL ON FUNCTION public.sillage_sync_user_profile() FROM PUBLIC, anon, authenticated;

DROP TRIGGER IF EXISTS sillage_sync_user_profile ON auth.users;
CREATE TRIGGER sillage_sync_user_profile
AFTER INSERT OR UPDATE OF email ON auth.users
FOR EACH ROW EXECUTE FUNCTION public.sillage_sync_user_profile();

-- Include accounts that existed before this migration.
INSERT INTO public.users (id, email, created_at)
SELECT id, email, COALESCE(created_at, now()) FROM auth.users
ON CONFLICT (id) DO UPDATE SET email = EXCLUDED.email;

-- Retain the existing auth.users foreign key and role values. This additional
-- relationship makes Users -> Account roles visible in the public diagram.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'public.app_user_roles'::regclass
          AND conname = 'app_user_roles_public_user_fkey'
    ) THEN
        ALTER TABLE public.app_user_roles
        ADD CONSTRAINT app_user_roles_public_user_fkey
        FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;
    END IF;
END;
$$;

COMMIT;

-- Verification: all existing Auth accounts should have a public users record.
SELECT count(*) AS missing_user_profiles
FROM auth.users a LEFT JOIN public.users u ON u.id = a.id
WHERE u.id IS NULL;
