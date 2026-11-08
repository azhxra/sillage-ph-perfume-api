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
import psycopg
from api.index import app
from api import database as db
from api.models import PerfumeInput
from seed_data import perfumes


class Contracts(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {'ADMIN_API_KEY':'local-test-only'})
        self.env.start()
        self.client = TestClient(app, raise_server_exceptions=False)
        self.body = {k:v for k,v in copy.deepcopy(perfumes[0]).items() if k != 'id'}
        self.auth = {'X-API-Key':'local-test-only'}

    def tearDown(self):
        self.client.close()
        self.env.stop()

    def test_all_seed_records_valid_and_unique(self):
        self.assertEqual(len(perfumes),25)
        self.assertEqual(len({(p['brand'],p['name']) for p in perfumes}),25)
        for p in perfumes:
            PerfumeInput.model_validate({k:v for k,v in p.items() if k != 'id'})

    def test_frontend_files(self):
        for path in ['/catalog','/perfume','/compare','/quiz','/style.css','/config.js','/app.js','/perfume.js','/compare.js','/quiz.js']:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code,200)
        self.assertEqual(self.client.get('/.env').status_code,404)

    def test_writes_fail_closed(self):
        for method,path in [('post','/perfumes'),('put','/perfumes/1'),('delete','/perfumes/1')]:
            for headers in [{},{'X-API-Key':'wrong'}]:
                self.assertEqual(self.client.request(method,path,headers=headers,json=self.body).status_code,401)
        with patch.dict(os.environ, {'ADMIN_API_KEY':''}):
            self.assertEqual(self.client.post('/perfumes',headers=self.auth,json=self.body).status_code,401)

    def test_invalid_bodies(self):
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
        with patch.object(db,'list_perfumes',return_value=perfumes) as operation:
            self.assertEqual(self.client.get('/perfumes').json(),{'count':25,'perfumes':perfumes})
            self.client.get('/perfumes?gender=Men&scent_family=Fresh&sort=price_desc')
            operation.assert_called_with('Men','Fresh','price_desc')
            self.assertEqual(self.client.get('/perfumes/search?q=Dior').json()['results'],perfumes)
            operation.assert_called_with(query='Dior')
        with patch.object(db,'compare',return_value=perfumes[:2]) as operation:
            self.assertEqual(self.client.get('/perfumes/compare?ids=2,1').status_code,200)
            operation.assert_called_once_with([2,1])

    def test_writes_delegate_validated_data(self):
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
            self.assertEqual(self.client.get('/perfumes').status_code,503)
        for status,detail in [(404,'Perfume not found.'),(409,'Duplicate')]:
            with patch.object(db,'get_perfume',side_effect=HTTPException(status,detail)):
                self.assertEqual(self.client.get('/perfumes/1').status_code,status)
        with patch.object(db,'get_perfume',side_effect=RuntimeError('private database details')):
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

    def test_cors(self):
        response=self.client.options('/perfumes',headers={'Origin':'https://unconfigured.example','Access-Control-Request-Method':'POST'})
        self.assertNotIn('access-control-allow-origin',response.headers)


if __name__=='__main__':
    unittest.main(verbosity=2)
