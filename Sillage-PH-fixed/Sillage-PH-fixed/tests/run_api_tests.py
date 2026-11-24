"""Opt-in live integration check. Reads private credentials only from environment.
Requires dedicated admin and two confirmed test-user accounts. Creates and removes only its own record.
"""
import os, uuid, copy, sys
from pathlib import Path
import requests
from dotenv import load_dotenv
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));load_dotenv(ROOT/'.env')
from seed_data import perfumes
base=os.getenv('API_BASE_URL','http://127.0.0.1:8000').rstrip('/')
created=None; admin={}; results=[]

def call(method,path,expected,headers=None,**kw):
    r=requests.request(method,base+path,headers=headers or {},timeout=20,**kw)
    if r.status_code!=expected: raise AssertionError(f'{method} {path}: expected {expected}, got {r.status_code}')
    if r.headers.get('X-Sillage-Preview')=='1': raise AssertionError('Preview is not live database evidence')
    results.append(f'PASS {method} {path} {expected}');return r

def login(prefix,role):
    email=os.getenv(prefix+'_EMAIL'); password=os.getenv(prefix+'_PASSWORD')
    if not email or not password: raise RuntimeError(f'Set {prefix}_EMAIL and {prefix}_PASSWORD privately')
    r=call('POST','/auth/login',200,json={'email':email,'password':password}).json()
    if r['role']!=role: raise AssertionError(f'Unexpected role for {prefix}')
    return {'Authorization':'Bearer '+r['access_token']},r['id']

def main():
    global created,admin
    call('GET','/health',200)
    admin,aid=login('TEST_ADMIN','admin'); user,uid=login('TEST_USER','user'); other,oid=login('TEST_OTHER','user')
    if len({aid,uid,oid})!=3: raise AssertionError('Use three different test accounts')
    payload=copy.deepcopy(perfumes[0]);payload.pop('id');payload['name']='Integration '+uuid.uuid4().hex
    call('POST','/perfumes',401,json=payload);call('POST','/perfumes',403,user,json=payload);call('POST','/perfumes',422,admin,json={})
    record=call('POST','/perfumes',201,admin,json=payload).json();created=record['id'];path=f'/perfumes/{created}';fav=f'/auth/favorites/{created}'
    assert call('GET',path,200).json()==record
    call('POST','/perfumes',409,admin,json=payload)
    assert call('GET','/perfumes/search',200,params={'q':payload['name']}).json()['count']==1
    call('PUT',fav,204,user);call('PUT',fav,204,user)
    assert sum(p['id']==created for p in call('GET','/auth/favorites',200,user).json()['perfumes'])==1
    assert not any(p['id']==created for p in call('GET','/auth/favorites',200,other).json()['perfumes'])
    call('PUT',fav,204,other);call('DELETE',fav,204,user)
    assert not any(p['id']==created for p in call('GET','/auth/favorites',200,user).json()['perfumes'])
    assert any(p['id']==created for p in call('GET','/auth/favorites',200,other).json()['perfumes'])
    payload['vibe']='Updated integration record';call('PUT',path,200,admin,json=payload)
    assert call('GET',path,200).json()['vibe']==payload['vibe']
    if os.getenv('TEST_RESTART_PAUSE')=='1':
        input('Restart/redeploy the server, then press Enter: ');assert call('GET',path,200).json()['vibe']==payload['vibe']
    call('DELETE',path,204,admin);call('GET',path,404);created=None
    assert not any(p['id']==record['id'] for p in call('GET','/auth/favorites',200,other).json()['perfumes'])
    results.append('PASS live CRUD, duplicate rejection, favorites isolation, cascade cleanup')

if __name__=='__main__':
    status=0
    try: main()
    except Exception as exc:
        # Avoid printing raw request exceptions (could contain URLs).
        results.append('FAIL '+(str(exc) if isinstance(exc,(AssertionError,RuntimeError)) else type(exc).__name__));status=1
    finally:
        if created is not None:
            try: call('DELETE',f'/perfumes/{created}',204,admin)
            except Exception: results.append(f'Cleanup required for test perfume ID {created}');status=1
        output='\n'.join(results)+'\n'; print(output); (ROOT/'docs/live-test-results.txt').write_text(output)
    sys.exit(status)
