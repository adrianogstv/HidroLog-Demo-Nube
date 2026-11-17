"""Pruebas aisladas: sin red, sin credenciales y sin borrar archivos."""
import base64
import copy
import json
from pathlib import Path
import sys
import unittest
import uuid
import zipfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'00 Code'/'herramientas'))
from generar_demo import create_package
from publicador_pc import dumps,digest,enqueue,publish_job,summarize


class FakeAPI:
    def __init__(self):
        self.state={'version':1,'synthetic_only':True,'last_received_utc':None,'projects':[]}
        self.writes=0;self.offline=False;self.conflict=False
    def __call__(self,method,path,data=None):
        if self.offline:raise ConnectionError('Red no disponible (simulada)')
        if method=='GET':return 200,{'sha':'sha-'+str(self.writes),'content':base64.b64encode(dumps(self.state)).decode()}
        if self.conflict:self.conflict=False;return 409,{}
        self.writes+=1;self.state=json.loads(base64.b64decode(data['content']))
        return 200,{'commit':{'sha':'commit-'+str(self.writes)}}


class PublisherTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.work=ROOT/'03 Output'/('QA_'+uuid.uuid4().hex[:8])
        cls.work.mkdir(parents=True)
    def setUp(self):
        self.folder=self.work/uuid.uuid4().hex[:8];self.folder.mkdir()
        self.a=create_package('a',self.folder/'A.wpcx')
    def test_synthetic_projection(self):
        summary=summarize(self.a)
        self.assertEqual(sum(h['runs'] for h in summary['holes']),7)
        self.assertAlmostEqual(sum(h['logged_m'] for h in summary['holes']),21)
        self.assertNotIn('Operador',dumps(summary).decode())
        self.assertNotIn('coordenadas',dumps(summary).decode())
    def test_invalid_hash(self):
        target=self.folder/'alterado.wpcx'
        with zipfile.ZipFile(self.a) as z:
            manifest=z.read('manifest.json');data=z.read('datos.json')+b' '
        with zipfile.ZipFile(target,'x') as z:z.writestr('manifest.json',manifest);z.writestr('datos.json',data)
        with self.assertRaises(ValueError):summarize(target)
    def test_unknown_hole_rejected(self):
        target=self.folder/'ajeno.wpcx'
        with zipfile.ZipFile(self.a) as z:
            manifest=json.loads(z.read('manifest.json'));data=json.loads(z.read('datos.json'))
        data['sondajes'][0]['id']='otro-proyecto'
        manifest['archivos']['datos.json']['sha256']=digest(dumps(data))
        with zipfile.ZipFile(target,'x') as z:z.writestr('manifest.json',dumps(manifest));z.writestr('datos.json',dumps(data))
        with self.assertRaises(ValueError):summarize(target)
    def test_offline_then_retry_and_deduplicate(self):
        job=enqueue(self.a,self.folder/'cola');api=FakeAPI();api.offline=True
        with self.assertRaises(ConnectionError):publish_job(job,api)
        self.assertEqual(json.loads(job.read_text())['status'],'pendiente')
        api.offline=False;publish_job(job,api);self.assertEqual(api.writes,1)
        publish_job(job,api);self.assertEqual(api.writes,1)
        other=enqueue(self.a,self.folder/'cola');publish_job(other,api);self.assertEqual(api.writes,1)
    def test_two_clients_preserved(self):
        b=create_package('b',self.folder/'B.wpcx');api=FakeAPI()
        for p in [self.a,b]:publish_job(enqueue(p,self.folder/'cola'),api)
        self.assertEqual([p['client'] for p in api.state['projects']],['a','b'])
    def test_conflict_retried(self):
        api=FakeAPI();api.conflict=True;job=enqueue(self.a,self.folder/'cola')
        publish_job(job,api);self.assertEqual(api.writes,1)
    def test_new_snapshot(self):
        changed=create_package('a',self.folder/'A_nuevo.wpcx',extra=True);api=FakeAPI()
        for p in [self.a,changed]:publish_job(enqueue(p,self.folder/'cola'),api)
        self.assertEqual(api.writes,2)
        self.assertEqual(sum(h['logged_m'] for h in api.state['projects'][0]['holes']),24)
    def test_queue_cannot_add_text_fields(self):
        job=enqueue(self.a,self.folder/'cola');data=json.loads(job.read_text())
        data['summary']['holes'][0]['comentario']='No publicar'
        data['summary']['snapshot_hash']=digest(dumps({k:v for k,v in data['summary'].items() if k!='snapshot_hash'}))
        job.write_bytes(dumps(data));api=FakeAPI()
        with self.assertRaises(ValueError):publish_job(job,api)
        self.assertEqual(api.writes,0)


if __name__=='__main__':unittest.main(verbosity=2)
