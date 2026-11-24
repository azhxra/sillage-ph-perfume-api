-- Run after sql/schema.sql and user_roles.sql.
BEGIN;
CREATE TABLE IF NOT EXISTS public.favorites (
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    perfume_id integer NOT NULL REFERENCES public.perfumes(id) ON DELETE CASCADE,
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (user_id, perfume_id)
);
CREATE INDEX IF NOT EXISTS favorites_perfume_idx ON public.favorites (perfume_id);
ALTER TABLE public.favorites ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.favorites FROM PUBLIC, anon, authenticated;
GRANT SELECT, INSERT, DELETE ON public.favorites TO sillage_api;
DROP POLICY IF EXISTS favorites_owner ON public.favorites;
CREATE POLICY favorites_owner ON public.favorites FOR ALL TO sillage_api
    USING (user_id::text = current_setting('sillage.user_id', true))
    WITH CHECK (user_id::text = current_setting('sillage.user_id', true));
COMMIT;
