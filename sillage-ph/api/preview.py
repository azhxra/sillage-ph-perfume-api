"""Read-only catalogue for a checkout without DATABASE_URL."""
import json

from seed_data import perfumes


def list_perfumes(gender=None, scent_family=None, sort=None, query=None):
    records = [
        p for p in perfumes
        if (not gender or p['gender'] == gender)
        and (not scent_family or p['scent_family'] == scent_family)
        and (not query or query.lower() in ' '.join(
            [p['name'], p['brand'], p['scent_family'], p['gender'],
             *p['key_notes'], *p['dupes'], json.dumps(p['where_to_buy']),
             json.dumps(p['other_stores'])]
        ).lower())
    ]
    if sort:
        return sorted(records, key=lambda p: (
            -p['price_php_min'] if sort == 'price_desc' else p['price_php_min'], p['id']))
    return records
