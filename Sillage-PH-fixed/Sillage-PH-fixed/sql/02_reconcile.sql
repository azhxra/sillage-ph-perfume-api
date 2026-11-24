-- Run as Supabase project administrator AFTER taking a database backup.
-- For a new project run schema.sql first; for your existing project run only this file.
-- Canonical application schema: users, app_user_roles, scent_families, perfumes, perfume_favorites.
-- No catalogue or account records are deleted. Any conflict aborts the transaction.
BEGIN;
DO $$ BEGIN
 IF to_regclass('public.perfumes') IS NULL THEN RAISE EXCEPTION 'Run schema.sql first on an empty project'; END IF;
 IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='sillage_api') THEN CREATE ROLE sillage_api LOGIN NOINHERIT; END IF;
END $$;
CREATE TABLE IF NOT EXISTS public.users (
 id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
 email text, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS public.app_user_roles (
 user_id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
 role text NOT NULL CHECK (role IN ('admin','user')), created_at timestamptz NOT NULL DEFAULT now()
);
INSERT INTO public.users(id,email,created_at)
 SELECT id,email,coalesce(created_at,now()) FROM auth.users
 ON CONFLICT(id) DO UPDATE SET email=excluded.email;
INSERT INTO public.app_user_roles(user_id,role)
 SELECT id,'user' FROM auth.users ON CONFLICT(user_id) DO NOTHING;
-- Make delete semantics explicit and identical in the fresh and existing database.
ALTER TABLE public.users DROP CONSTRAINT IF EXISTS users_id_fkey;
ALTER TABLE public.users ADD CONSTRAINT users_id_fkey FOREIGN KEY(id) REFERENCES auth.users(id) ON DELETE CASCADE;
ALTER TABLE public.app_user_roles DROP CONSTRAINT IF EXISTS app_user_roles_public_user_fkey;
ALTER TABLE public.app_user_roles ADD CONSTRAINT app_user_roles_public_user_fkey FOREIGN KEY(user_id) REFERENCES public.users(id) ON DELETE CASCADE;
ALTER TABLE public.app_user_roles DROP CONSTRAINT IF EXISTS app_user_roles_user_id_fkey;
ALTER TABLE public.app_user_roles ADD CONSTRAINT app_user_roles_user_id_fkey FOREIGN KEY(user_id) REFERENCES auth.users(id) ON DELETE CASCADE;
CREATE OR REPLACE FUNCTION public.sillage_sync_user_profile() RETURNS trigger
 LANGUAGE plpgsql SECURITY DEFINER SET search_path='' AS $$
BEGIN
 INSERT INTO public.users(id,email,created_at) VALUES(NEW.id,NEW.email,coalesce(NEW.created_at,now()))
 ON CONFLICT(id) DO UPDATE SET email=excluded.email;
 INSERT INTO public.app_user_roles(user_id,role) VALUES(NEW.id,'user') ON CONFLICT(user_id) DO NOTHING;
 RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION public.sillage_sync_user_profile() FROM PUBLIC, anon, authenticated;
DROP TRIGGER IF EXISTS sillage_sync_user_profile ON auth.users;
CREATE TRIGGER sillage_sync_user_profile AFTER INSERT OR UPDATE OF email ON auth.users
 FOR EACH ROW EXECUTE FUNCTION public.sillage_sync_user_profile();
CREATE TABLE IF NOT EXISTS public.scent_families(name varchar(20) PRIMARY KEY, description text NOT NULL DEFAULT '');
INSERT INTO public.scent_families(name,description) VALUES
 ('Amber','Warm, rich and often resinous'),('Floral','Flower-forward fragrances'),('Fruity','Fruit-forward fragrances'),('Fresh','Clean, citrus, green or aquatic'),('Woody','Wood-forward fragrances'),('Gourmand','Dessert-like sweet fragrances'),('Leather','Leather-forward fragrances')
 ON CONFLICT(name) DO NOTHING;
ALTER TABLE public.perfumes ADD COLUMN IF NOT EXISTS created_by uuid;
ALTER TABLE public.perfumes DROP CONSTRAINT IF EXISTS perfumes_created_by_fkey;
ALTER TABLE public.perfumes ADD CONSTRAINT perfumes_created_by_fkey FOREIGN KEY(created_by) REFERENCES public.app_user_roles(user_id) ON DELETE SET NULL;
ALTER TABLE public.perfumes DROP CONSTRAINT IF EXISTS perfumes_scent_family_fkey;
ALTER TABLE public.perfumes ADD CONSTRAINT perfumes_scent_family_fkey FOREIGN KEY(scent_family) REFERENCES public.scent_families(name) ON UPDATE CASCADE ON DELETE RESTRICT;
-- Enforce unique brand/name, without deleting duplicates. Avoid a second index if already enforced.
DO $$ BEGIN
 IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conrelid='public.perfumes'::regclass AND contype='u' AND pg_get_constraintdef(oid)='UNIQUE (brand, name)') THEN
   ALTER TABLE public.perfumes ADD CONSTRAINT sillage_perfume_brand_name_unique UNIQUE(brand,name);
 END IF;
END $$;
ALTER TABLE public.perfumes ALTER COLUMN id SET GENERATED ALWAYS;
ALTER TABLE public.perfumes ADD COLUMN IF NOT EXISTS search_text text NOT NULL DEFAULT '';
CREATE OR REPLACE FUNCTION public.perfumes_search_update() RETURNS trigger LANGUAGE plpgsql SECURITY INVOKER SET search_path='' AS $$
BEGIN
 NEW.search_text := NEW.name || ' ' || NEW.brand || ' ' || NEW.scent_family || ' ' || NEW.gender || ' ' ||
 array_to_string(NEW.key_notes,' ') || ' ' || array_to_string(NEW.dupes,' ') || ' ' || NEW.where_to_buy::text || ' ' || NEW.other_stores::text;
 RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION public.perfumes_search_update() FROM PUBLIC;
DROP TRIGGER IF EXISTS perfumes_search_update ON public.perfumes;
CREATE TRIGGER perfumes_search_update BEFORE INSERT OR UPDATE ON public.perfumes FOR EACH ROW EXECUTE FUNCTION public.perfumes_search_update();
UPDATE public.perfumes SET search_text='' ;
CREATE INDEX IF NOT EXISTS perfumes_gender_idx ON public.perfumes(gender);
CREATE INDEX IF NOT EXISTS perfumes_family_idx ON public.perfumes(scent_family);
CREATE INDEX IF NOT EXISTS perfumes_price_idx ON public.perfumes(price_php_min,id);
CREATE INDEX IF NOT EXISTS perfumes_name_idx ON public.perfumes(name);
CREATE INDEX IF NOT EXISTS perfumes_created_by_idx ON public.perfumes(created_by);
CREATE TABLE IF NOT EXISTS public.perfume_favorites(
 user_id uuid NOT NULL REFERENCES public.app_user_roles(user_id) ON DELETE CASCADE,
 perfume_id integer NOT NULL REFERENCES public.perfumes(id) ON DELETE CASCADE,
 created_at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY(user_id,perfume_id)
);
ALTER TABLE public.perfume_favorites DROP CONSTRAINT IF EXISTS perfume_favorites_user_id_fkey;
ALTER TABLE public.perfume_favorites ADD CONSTRAINT perfume_favorites_user_id_fkey FOREIGN KEY(user_id) REFERENCES public.app_user_roles(user_id) ON DELETE CASCADE;
ALTER TABLE public.perfume_favorites DROP CONSTRAINT IF EXISTS perfume_favorites_perfume_id_fkey;
ALTER TABLE public.perfume_favorites ADD CONSTRAINT perfume_favorites_perfume_id_fkey FOREIGN KEY(perfume_id) REFERENCES public.perfumes(id) ON DELETE CASCADE;
-- If an earlier favorites table exists, merge once, preserving the earlier save time.
-- Keep the old table in a separate restricted schema so it does not interfere with the ERD.
DO $$ BEGIN
 IF to_regclass('public.favorites') IS NOT NULL THEN
   INSERT INTO public.perfume_favorites(user_id,perfume_id,created_at)
   SELECT user_id,perfume_id,created_at FROM public.favorites
   ON CONFLICT(user_id,perfume_id) DO UPDATE SET created_at=least(public.perfume_favorites.created_at,excluded.created_at);
   CREATE SCHEMA IF NOT EXISTS sillage_archive;
   IF to_regclass('sillage_archive.favorites') IS NOT NULL THEN RAISE EXCEPTION 'Archive already exists; inspect old favorites before merging'; END IF;
   -- Remove old FKs so legacy snapshots cannot block active-table deletions.
   ALTER TABLE public.favorites DROP CONSTRAINT IF EXISTS favorites_user_id_fkey;
   ALTER TABLE public.favorites DROP CONSTRAINT IF EXISTS favorites_perfume_id_fkey;
   ALTER TABLE public.favorites SET SCHEMA sillage_archive;
   REVOKE ALL ON sillage_archive.favorites FROM PUBLIC,anon,authenticated,sillage_api;
   REVOKE ALL ON SCHEMA sillage_archive FROM PUBLIC,anon,authenticated,sillage_api;
 END IF;
END $$;
CREATE INDEX IF NOT EXISTS perfume_favorites_perfume_idx ON public.perfume_favorites(perfume_id);
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.app_user_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scent_families ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.perfumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.perfume_favorites ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.users,public.app_user_roles,public.scent_families,public.perfumes,public.perfume_favorites FROM PUBLIC,anon,authenticated;
REVOKE ALL ON public.users,public.app_user_roles,public.scent_families,public.perfumes,public.perfume_favorites FROM sillage_api;
REVOKE ALL ON SEQUENCE public.perfumes_id_seq FROM PUBLIC,anon,authenticated;
GRANT USAGE ON SCHEMA public TO sillage_api;
GRANT SELECT ON public.app_user_roles TO sillage_api;
GRANT SELECT,INSERT,UPDATE,DELETE ON public.perfumes TO sillage_api;
GRANT USAGE,SELECT,UPDATE ON SEQUENCE public.perfumes_id_seq TO sillage_api;
GRANT SELECT,INSERT,DELETE ON public.perfume_favorites TO sillage_api;
DROP POLICY IF EXISTS api_can_read_roles ON public.app_user_roles;
CREATE POLICY api_can_read_roles ON public.app_user_roles FOR SELECT TO sillage_api USING(true);
DROP POLICY IF EXISTS backend_access ON public.perfumes;
CREATE POLICY backend_access ON public.perfumes FOR ALL TO sillage_api USING(true) WITH CHECK(true);
DROP POLICY IF EXISTS favorites_owner ON public.perfume_favorites;
CREATE POLICY favorites_owner ON public.perfume_favorites FOR ALL TO sillage_api
 USING(user_id::text=current_setting('sillage.user_id',true)) WITH CHECK(user_id::text=current_setting('sillage.user_id',true));
-- Advance identity sequence, never rewind it.
SELECT setval('public.perfumes_id_seq', greatest((SELECT coalesce(max(id),1) FROM public.perfumes),(SELECT last_value FROM public.perfumes_id_seq)),true);
COMMIT;
