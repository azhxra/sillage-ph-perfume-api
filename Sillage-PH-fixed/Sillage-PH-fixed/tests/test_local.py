"""Contract and failure tests; these do not claim cloud database coverage."""
import copy
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.pop('DATABASE_URL', None)
from fastapi.testclient import TestClient
from fastapi import HTTPException
try:
    import psycopg
except ModuleNotFoundError:
    raise unittest.SkipTest("Psycopg is not installed; use test_preview.py for offline contracts")
from api.index import app
from api.auth import current_user
from api import database as db
from api.models import PerfumeInput
from seed_data import perfumes


class Contracts(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app, raise_server_exceptions=False)
        self.body = {k:v for k,v in copy.deepcopy(perfumes[0]).items() if k != 'id'}
        self.auth = {'Authorization':'Bearer local-test-only'}

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.pop(current_user, None)

    def test_all_seed_records_valid_and_unique(self):
        self.assertEqual(len(perfumes),25)
        self.assertEqual(len({(p['brand'],p['name']) for p in perfumes}),25)
        for p in perfumes:
            PerfumeInput.model_validate({k:v for k,v in p.items() if k != 'id'})

    def test_frontend_files(self):
        for path in ['/catalog','/perfume','/compare','/quiz','/style.css','/config.js','/app.js','/perfume.js','/compare.js','/quiz.js','/login','/account','/admin','/schema','/session.js','/dashboard.js']:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code,200)
        self.assertEqual(self.client.get('/.env').status_code,404)

    def test_writes_fail_closed(self):
        for method,path in [('post','/perfumes'),('put','/perfumes/1'),('delete','/perfumes/1')]:
            for headers in [{},{'X-API-Key':'wrong'}]:
                self.assertEqual(self.client.request(method,path,headers=headers,json=self.body).status_code,401)
        app.dependency_overrides[current_user] = lambda: {'role': 'user'}
        self.assertEqual(self.client.post('/perfumes',headers=self.auth,json=self.body).status_code,403)

    def test_invalid_bodies(self):
        app.dependency_overrides[current_user] = lambda: {'id': '3058b2c2-2183-4cb4-851c-62597517c2ab', 'role': 'admin'}
        cases=[{}, {**self.body,'name':'  '}, {**self.body,'brand':123}, {**self.body,'year_launched':True},
            {**self.body,'year_launched':1899}, {**self.body,'year_launched':9999}, {**self.body,'price_php_min':'450'},
            {**self.body,'gender':'invalid'}, {**self.body,'scent_family':'invalid'}, {**self.body,'key_notes':[]},
            {**self.body,'dupes':['x']*31}, {**self.body,'extra':True}, {**self.body,'where_to_buy':{**self.body['where_to_buy'],'url':'http://example.com'}},
            {**self.body,'other_stores':[{'store':'A','dupe':'B','url':'javascript:alert(1)'}]}]
        for body in cases:
            with self.subTest(body=body):
                response=self.client.post('/perfumes',headers=self.auth,json=body)
                self.assertEqual(response.status_code,422)
                self.assertEqual(response.json(),{'detail':'Invalid request data.'})
        self.assertEqual(self.client.post('/perfumes',headers={**self.auth,'Content-Type':'application/json'},content='{').status_code,422)

    def test_named_routes_and_queries(self):
        for path in ['/perfumes/search?q=%20','/perfumes/compare?ids=1','/perfumes/compare?ids=1,1','/perfumes/compare?ids=a,b','/perfumes?gender=Other','/perfumes?sort=unknown']:
            self.assertEqual(self.client.get(path).status_code,422)
        with patch.object(db,'pool',object()), patch.object(db,'list_perfumes',return_value=perfumes) as operation:
            self.assertEqual(self.client.get('/perfumes').json(),{'count':25,'perfumes':perfumes})
            self.client.get('/perfumes?gender=Men&scent_family=Fresh&sort=price_desc')
            operation.assert_called_with(gender='Men', scent_family='Fresh', sort='price_desc')
            self.assertEqual(self.client.get('/perfumes/search?q=Chanel').json()['results'],perfumes)
            operation.assert_called_with(query='Chanel')
        with patch.object(db,'pool',object()), patch.object(db,'compare',return_value=perfumes[:2]) as operation:
            self.assertEqual(self.client.get('/perfumes/compare?ids=2,1').status_code,200)
            operation.assert_called_once_with([2,1])

    def test_writes_delegate_validated_data(self):
        app.dependency_overrides[current_user] = lambda: {'id': '3058b2c2-2183-4cb4-851c-62597517c2ab', 'role': 'admin'}
        with patch.object(db,'create',return_value=perfumes[0]) as operation:
            response=self.client.post('/perfumes',headers=self.auth,json=self.body)
            self.assertEqual(response.status_code,201)
            self.assertNotIn('id',operation.call_args.args[0])
        with patch.object(db,'replace',return_value=perfumes[0]):
            self.assertEqual(self.client.put('/perfumes/1',headers=self.auth,json=self.body).status_code,200)
            self.assertEqual(self.client.put('/perfumes/1',headers=self.auth,json={'name':'Partial'}).status_code,422)
        with patch.object(db,'delete',return_value=None):
            self.assertEqual(self.client.delete('/perfumes/1',headers=self.auth).status_code,204)

    def test_clean_failure_responses(self):
        with patch.object(db,'pool',None):
            self.assertEqual(self.client.get('/health').json(),{'detail':'Database unavailable'})
            self.assertEqual(self.client.get('/health').status_code,503)
            response = self.client.get('/perfumes')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['X-Sillage-Preview'], '1')
            self.assertEqual(response.json()['count'], len(perfumes))
            self.assertEqual(self.client.get('/perfumes/1').status_code, 200)
            self.assertEqual(self.client.get('/perfumes/search?q=Chanel').status_code, 200)
            compared = self.client.get('/perfumes/compare?ids=2,1').json()['perfumes']
            self.assertEqual([p['id'] for p in compared], [2,1])
        for status,detail in [(404,'Perfume not found.'),(409,'Duplicate')]:
            with patch.object(db,'pool',object()), patch.object(db,'get_perfume',side_effect=HTTPException(status,detail)):
                self.assertEqual(self.client.get('/perfumes/1').status_code,status)
        with patch.object(db,'pool',object()), patch.object(db,'get_perfume',side_effect=RuntimeError('private database details')):
            response=self.client.get('/perfumes/1')
            self.assertEqual(response.status_code,500)
            self.assertEqual(response.json(),{'detail':'Internal server error'})

    def test_database_exception_translation(self):
        for error,status in [(psycopg.errors.UniqueViolation('private'),409),(psycopg.OperationalError('private'),503),(psycopg.ProgrammingError('private'),500)]:
            fake=MagicMock()
            fake.connection.side_effect=error
            with patch.object(db,'pool',fake):
                with self.assertRaises(HTTPException) as raised:
                    db.health()
                self.assertEqual(raised.exception.status_code,status)
                self.assertNotIn('private',raised.exception.detail)

    def test_configured_database_outage_keeps_public_catalog_available(self):
        with patch.object(db, 'pool', object()):
            for operation in ['list_perfumes', 'compare', 'get_perfume']:
                with patch.object(db, operation, side_effect=HTTPException(503, 'Database unavailable')):
                    paths = ['/perfumes', '/perfumes/search?q=Chanel', '/perfumes?gender=Women&sort=price_desc'] if operation == 'list_perfumes' else ['/perfumes/compare?ids=2,1'] if operation == 'compare' else ['/perfumes/1']
                    for path in paths:
                        with self.subTest(path=path):
                            response = self.client.get(path)
                            self.assertEqual(response.status_code, 200)
                            self.assertEqual(response.headers['X-Sillage-Preview'], '1')
                            self.assertEqual(response.headers['Cache-Control'], 'no-store')
                            data = response.json()
                            if path == '/perfumes':
                                self.assertEqual(data['count'], 25)
                            elif 'search' in path:
                                self.assertTrue(data['results'])
                                self.assertTrue(all('chanel' in p['brand'].lower() for p in data['results']))
                            elif 'gender' in path:
                                self.assertTrue(all(p['gender'] == 'Women' for p in data['perfumes']))
                                prices = [p['price_php_min'] for p in data['perfumes']]
                                self.assertEqual(prices, sorted(prices, reverse=True))
                            elif 'compare' in path:
                                self.assertEqual([p['id'] for p in data['perfumes']], [2, 1])
                            else:
                                self.assertEqual(data['id'], 1)
            # The next successful read returns current database records immediately.
            with patch.object(db, 'list_perfumes', return_value=perfumes[:1]):
                response = self.client.get('/perfumes')
                self.assertEqual(response.json()['count'], 1)
                self.assertNotIn('X-Sillage-Preview', response.headers)

    def test_outage_does_not_simulate_successful_writes_or_health(self):
        app.dependency_overrides[current_user] = lambda: {'id': '3058b2c2-2183-4cb4-851c-62597517c2ab', 'role': 'admin'}
        with patch.object(db, 'pool', object()), patch.object(db, 'health', side_effect=HTTPException(503)), patch.object(db, 'create', side_effect=HTTPException(503)):
            self.assertEqual(self.client.get('/health').status_code, 503)
            self.assertEqual(self.client.post('/perfumes', json=self.body).status_code, 503)

    def test_database_search_parameterized(self):
        conn=MagicMock()
        conn.execute.return_value.fetchall.return_value=[]
        with patch.object(db,'connection') as context:
            context.return_value.__enter__.return_value=conn
            needle="%' OR 1=1 --"
            db.list_perfumes(query=needle)
            statement,params=conn.execute.call_args.args
            self.assertNotIn(needle,statement.as_string())
            self.assertEqual(params,[needle])

    def test_favorites_use_authenticated_identity(self):
        self.assertEqual(self.client.get('/auth/favorites').status_code, 401)
        self.assertEqual(self.client.put('/auth/favorites/1').status_code, 401)
        self.assertEqual(self.client.delete('/auth/favorites/1').status_code, 401)
        owner = '3058b2c2-2183-4cb4-851c-62597517c2ab'
        app.dependency_overrides[current_user] = lambda: {'id': owner, 'role': 'user'}
        with patch.object(db, 'favorites', return_value=[]) as operation:
            self.assertEqual(self.client.get('/auth/favorites').json(), {'perfumes': []})
            operation.assert_called_with(owner)
            self.assertEqual(self.client.put('/auth/favorites/1').status_code, 204)
            operation.assert_called_with(owner, 1, 'PUT')
            self.assertEqual(self.client.delete('/auth/favorites/1').status_code, 204)
            operation.assert_called_with(owner, 1, 'DELETE')

    def test_cors(self):
        response=self.client.options('/perfumes',headers={'Origin':'https://unconfigured.example','Access-Control-Request-Method':'POST'})
        self.assertNotIn('access-control-allow-origin',response.headers)


if __name__=='__main__':
    unittest.main(verbosity=2)
