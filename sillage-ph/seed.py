"""Run manually after schema setup. Existing rows are never overwritten."""
from psycopg import sql
from api import database as db
from api.models import PerfumeInput
from seed_data import perfumes

def main():
    with db.connection() as conn:
        # Serialize seed runs and reserve original IDs before concurrent writes.
        conn.execute('LOCK TABLE public.perfumes IN ACCESS EXCLUSIVE MODE')
        for original in perfumes:
            data = PerfumeInput.model_validate({k: v for k,v in original.items() if k != 'id'}).model_dump(mode='json')
            statement = sql.SQL('INSERT INTO public.perfumes ({}) VALUES ({}) ON CONFLICT DO NOTHING').format(
                db.columns(), sql.SQL(', ').join(sql.Placeholder() for _ in range(len(db.FIELDS)+1)))
            conn.execute(statement, [original['id'], *db.values(data)])
        # Never move the sequence backwards, even after deleting a recent record.
        conn.execute("SELECT setval('public.perfumes_id_seq', greatest((SELECT coalesce(max(id),1) FROM public.perfumes), (SELECT last_value FROM public.perfumes_id_seq)), true)")
    print('Seed completed; existing records preserved.')

if __name__ == '__main__':
    try:
        main()
    finally:
        if db.pool is not None:
            db.pool.close()
