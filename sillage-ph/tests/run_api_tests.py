"""Run against a configured API. Never prints credentials or raw error responses."""
import copy
import os
from pathlib import Path
import sys
import uuid

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env')
sys.path.insert(0, str(ROOT))
from seed_data import perfumes

rows = []
base = os.getenv('API_BASE_URL', 'http://127.0.0.1:8000').rstrip('/')
key = os.getenv('ADMIN_API_KEY', '')
created = []


def check(category, description, expected, actual, passed):
    rows.append([f'T{len(rows)+1:02}', category, description, str(expected), str(actual), 'PASS' if passed else 'FAIL'])


def call(method, path, expected, category, description, **kwargs):
    headers = kwargs.pop('headers', {'X-API-Key': key})
    response = requests.request(method, base + path, headers=headers, timeout=15, **kwargs)
    check(category, description, expected, response.status_code, response.status_code == expected)
    return response


def run():
    health = call('GET', '/health', 200, 'Integration', 'Real database health query')
    if health.status_code != 200 or not key:
        rows.append(['BLOCKED', 'Cloud CRUD', 'Configure database and ADMIN_API_KEY before CRUD checks', 'connected', 'not configured', 'BLOCKED'])
        return
    payload = copy.deepcopy(perfumes[0])
    payload.pop('id')
    payload['name'] = 'Integration ' + uuid.uuid4().hex
    for method, path in [('POST', '/perfumes'), ('PUT', '/perfumes/1'), ('DELETE', '/perfumes/1')]:
        for headers in [{}, {'X-API-Key': 'invalid-test-key'}]:
            call(method, path, 401, 'Security', f'{method} rejects missing/invalid key', headers=headers, json=payload)
    for desc, body in [('Empty body', {}), ('Missing name', {k:v for k,v in payload.items() if k != 'name'}), ('Wrong type', {**payload, 'price_php_min':'450'}), ('Bad enum', {**payload, 'gender':'Other'}), ('Bad URL', {**payload, 'where_to_buy':{**payload['where_to_buy'], 'url':'http://example.com'}}), ('Unknown field', {**payload, 'unexpected':True}), ('Null', {**payload, 'name':None})]:
        call('POST', '/perfumes', 422, 'Validation', desc, json=body)
    call('POST', '/perfumes', 422, 'Validation', 'Malformed JSON', data='{', headers={'X-API-Key':key, 'Content-Type':'application/json'})
    for n in range(2):
        body = {**payload, 'name': payload['name']+str(n), 'price_php_min':100+n}
        response = call('POST', '/perfumes', 201, 'Functional', 'Create test record', json=body)
        if response.status_code != 201:
            return
        record = response.json()
        created.append(record['id'])
        got = call('GET', f'/perfumes/{record["id"]}', 200, 'Functional', 'Read created record').json()
        check('Integration', 'POST equals GET', True, got == record, got == record)
    first, second = created
    duplicate = {**payload, 'name':payload['name']+'0', 'price_php_min':100}
    call('POST', '/perfumes', 409, 'Validation', 'Duplicate brand and name', json=duplicate)
    listing = call('GET', '/perfumes', 200, 'Functional', 'List').json()['perfumes']
    check('Integration', 'Created records in list', True, all(any(p['id']==i for p in listing) for i in created), all(any(p['id']==i for p in listing) for i in created))
    result = call('GET', '/perfumes/search', 200, 'Functional', 'Search', params={'q':payload['name']}).json()['results']
    check('Integration', 'Search finds created records', 2, len(result), len(result)==2)
    expected_records={p['id']:p for p in listing if p['id'] in created}
    check('Integration', 'Search objects equal GET/list objects', True,
          all(p==expected_records.get(p['id']) for p in result),
          all(p==expected_records.get(p['id']) for p in result))
    comparison = call('GET', '/perfumes/compare', 200, 'Integration', 'Compare created records', params={'ids':f'{second},{first}'}).json()['perfumes']
    check('Integration', 'Compare order', [second, first], [p['id'] for p in comparison], [p['id'] for p in comparison]==[second,first])
    check('Integration', 'Compare objects equal GET/list objects', True,
          all(p==expected_records.get(p['id']) for p in comparison),
          all(p==expected_records.get(p['id']) for p in comparison))
    for field in ['gender','scent_family']:
        filtered=call('GET','/perfumes',200,'Functional',field+' filter',params={field:payload[field]}).json()['perfumes']
        check('Functional',field+' values match',True,all(p[field]==payload[field] for p in filtered),all(p[field]==payload[field] for p in filtered))
    for sort in ['price_asc','price_desc']:
        prices=[p['price_php_min'] for p in call('GET','/perfumes',200,'Functional',sort,params={'sort':sort}).json()['perfumes']]
        check('Functional','Prices sorted',True,prices==sorted(prices,reverse=sort=='price_desc'),prices==sorted(prices,reverse=sort=='price_desc'))
    updated={**duplicate,'vibe':'Updated test record'}
    call('PUT',f'/perfumes/{first}',200,'Functional','Full replacement',json=updated)
    got=call('GET',f'/perfumes/{first}',200,'Persistence','Updated record retained').json()
    check('Persistence','Updated value',updated['vibe'],got['vibe'],got['vibe']==updated['vibe'])
    if os.getenv('TEST_RESTART_PAUSE') == '1':
        input('Restart or redeploy the API, then press Enter. Test records will be cleaned up afterwards: ')
        got=call('GET',f'/perfumes/{first}',200,'Persistence','Record after restart').json()
        check('Persistence','Update after restart',updated['vibe'],got['vibe'],got['vibe']==updated['vibe'])
    else:
        rows.append(['PENDING','Persistence','Set TEST_RESTART_PAUSE=1 for manual restart checkpoint','restart','not attempted','PENDING'])
    call('DELETE',f'/perfumes/{first}',204,'Functional','Delete')
    call('GET',f'/perfumes/{first}',404,'Persistence','Deleted record absent')
    call('DELETE',f'/perfumes/{first}',404,'Functional','Repeated delete')
    call('PUT',f'/perfumes/{first}',404,'Functional','Update missing record',json=updated)
    if os.getenv('TEST_RESTART_PAUSE') == '1':
        input('Restart or redeploy again, then press Enter to verify the deletion persists: ')
        call('GET',f'/perfumes/{first}',404,'Persistence','Deletion after restart')


if __name__ == '__main__':
    try:
        run()
    except requests.RequestException:
        rows.append(['BLOCKED','Connectivity','API unreachable','reachable','connection failed','BLOCKED'])
    except Exception as exc:
        rows.append(['ERROR','Runner','Unexpected runner failure','none',type(exc).__name__,'FAIL'])
    finally:
        for record_id in created:
            try:
                response=requests.delete(base+f'/perfumes/{record_id}',headers={'X-API-Key':key},timeout=15)
                if response.status_code not in (204,404):
                    check('Cleanup',f'Remove test record {record_id}', '204 or 404', response.status_code,False)
            except requests.RequestException:
                check('Cleanup',f'Remove test record {record_id}','reachable','failed',False)
        output='# Live API test results\n\n'+ '| Test ID | Category | Description | Expected | Actual | PASS/FAIL |\n|---|---|---|---|---|---|\n'+'\n'.join('| '+' | '.join(r)+' |' for r in rows)+'\n'
        print(output)
        (ROOT/'docs').mkdir(exist_ok=True)
        (ROOT/'docs/test-results.md').write_text(output,encoding='utf-8')
    sys.exit(1 if any(r[-1] in ('FAIL','BLOCKED','PENDING') for r in rows) else 0)
