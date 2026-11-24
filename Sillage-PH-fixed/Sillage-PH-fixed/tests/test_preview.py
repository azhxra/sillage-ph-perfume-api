"""Executable HTTP contracts, no database credentials required."""
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import HTTPException
from api.index import app
from api import database as db, auth
from api.models import PerfumeInput
from seed_data import perfumes

class PreviewContracts(unittest.TestCase):
    def setUp(self): self.c=TestClient(app,raise_server_exceptions=False)
    def tearDown(self): app.dependency_overrides.clear(); self.c.close()
    def test_seed(self):
        self.assertEqual(len(perfumes),25)
        for p in perfumes: PerfumeInput.model_validate({k:v for k,v in p.items() if k!='id'})
    def test_pages(self):
        for page in ['catalog','perfume','quiz','compare','schema','login','account','admin','schema.js','schema.css','docs']:
            self.assertEqual(self.c.get('/'+page).status_code,200,page)
        self.assertEqual(self.c.get('/.env').status_code,404)
    def test_preview(self):
        with patch.object(db,'pool',None):
            r=self.c.get('/perfumes'); self.assertEqual(r.json()['count'],25);self.assertEqual(r.headers['X-Sillage-Preview'],'1')
            self.assertEqual(self.c.get('/perfumes/search?q=Chanel').json()['count'],3)
            self.assertEqual([p['id'] for p in self.c.get('/perfumes/compare?ids=2,1').json()['perfumes']],[2,1])
            self.assertEqual(self.c.get('/perfumes/9999').status_code,404)
            self.assertEqual(self.c.get('/health').status_code,503)
    def test_filters(self):
        with patch.object(db,'pool',None):
            items=self.c.get('/perfumes?gender=Women&scent_family=Floral&sort=price_desc').json()['perfumes']
            self.assertTrue(items);self.assertTrue(all(p['gender']=='Women' and p['scent_family']=='Floral' for p in items))
            prices=[p['price_php_min'] for p in items];self.assertEqual(prices,sorted(prices,reverse=True))
    def test_validation(self):
        for path in ['/perfumes/search?q=%20','/perfumes/compare?ids=1,1','/perfumes/compare?ids=1','/perfumes?gender=bad']:
            self.assertEqual(self.c.get(path).status_code,422,path)
    def test_auth_and_admin(self):
        payload={k:v for k,v in perfumes[0].items() if k!='id'}
        self.assertEqual(self.c.post('/perfumes',json=payload).status_code,401)
        self.assertEqual(self.c.get('/auth/favorites').status_code,401)
        app.dependency_overrides[auth.current_user]=lambda:{'id':'test-user','role':'user'}
        self.assertEqual(self.c.post('/perfumes',json=payload).status_code,403)
        app.dependency_overrides[auth.current_user]=lambda:{'id':'test-admin','role':'admin'}
        self.assertEqual(self.c.post('/perfumes',json={}).status_code,422)
        with patch.object(db,'create',return_value=perfumes[0]) as create:
            self.assertEqual(self.c.post('/perfumes',json=payload).status_code,201)
            self.assertEqual(create.call_args.args[1],'test-admin')
    def test_favorites_identity(self):
        app.dependency_overrides[auth.current_user]=lambda:{'id':'owner','role':'user'}
        with patch.object(db,'favorites',return_value=[]) as op:
            self.assertEqual(self.c.get('/auth/favorites').json(),{'perfumes':[]});op.assert_called_with('owner')
            self.assertEqual(self.c.put('/auth/favorites/1').status_code,204);op.assert_called_with('owner',1,'PUT')
            self.assertEqual(self.c.delete('/auth/favorites/1').status_code,204);op.assert_called_with('owner',1,'DELETE')
    def test_outage_recovery(self):
        with patch.object(db,'pool',object()),patch.object(db,'list_perfumes',side_effect=HTTPException(503)):
            self.assertEqual(self.c.get('/perfumes').headers['X-Sillage-Preview'],'1')
        with patch.object(db,'pool',object()),patch.object(db,'list_perfumes',return_value=perfumes[:1]):
            r=self.c.get('/perfumes');self.assertEqual(r.json()['count'],1);self.assertNotIn('X-Sillage-Preview',r.headers)
if __name__=='__main__': unittest.main()
