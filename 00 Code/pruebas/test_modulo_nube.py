"""Cifrado, cola e idempotencia. Sin red ni credenciales reales."""
import base64
import copy
import json
from pathlib import Path
import secrets
import subprocess
import sys
import unittest
import uuid

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'00 Code'/'modulo_nube'))
import cloud_core as cloud
from publicador_pc import summarize


class API:
    def __init__(self):self.files={};self.writes=0;self.offline=False
    def __call__(self,method,path,body=None):
        if self.offline:raise ConnectionError('offline')
        if method=='GET':
            if path not in self.files:return 404,{}
            return 200,{'sha':str(self.writes),'content':self.files[path]}
        self.files[path]=body['content'];self.writes+=1
        return 201,{'commit':{'sha':'demo-commit-'+str(self.writes)}}


class CloudTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.work=ROOT/'03 Output'/('QA_C_'+uuid.uuid4().hex[:8]);cls.work.mkdir(parents=True)
    def setUp(self):
        self.password=secrets.token_urlsafe(20)
        self.summary=summarize(ROOT/'02 Input'/'DEMO_A.wpcx')
        self.folder=self.work/uuid.uuid4().hex[:6];self.folder.mkdir()
    def test_roundtrip_and_no_plaintext(self):
        e=cloud.encrypt(self.summary,self.password)
        self.assertEqual(cloud.decrypt(e,self.password)['project'],self.summary)
        self.assertNotIn(self.password,cloud.pack(e).decode())
        self.assertNotIn(self.summary['label'],cloud.pack(e).decode())
    def test_wrong_password(self):
        with self.assertRaises(Exception):cloud.decrypt(cloud.encrypt(self.summary,self.password),'incorrect-password')
    def test_tamper_and_context(self):
        e=cloud.encrypt(self.summary,self.password)
        changed=copy.deepcopy(e);data=bytearray(cloud.decode(changed['ciphertext']));data[0]^=1;changed['ciphertext']=cloud.encode(data)
        with self.assertRaises(Exception):cloud.decrypt(changed,self.password)
        changed=copy.deepcopy(e);changed['client']='b'
        with self.assertRaises(Exception):cloud.decrypt(changed,self.password)
    def test_fresh_salt_and_iv(self):
        a=cloud.encrypt(self.summary,self.password);b=cloud.encrypt(self.summary,self.password)
        self.assertNotEqual(a['salt'],b['salt']);self.assertNotEqual(a['iv'],b['iv'])
    def test_offline_queue_and_repeat(self):
        p=cloud.enqueue(ROOT/'02 Input'/'DEMO_A.wpcx',self.password,self.folder);api=API();api.offline=True
        with self.assertRaises(ConnectionError):cloud.send(p,api)
        self.assertTrue(p.exists());self.assertFalse(cloud.receipt_path(p).exists())
        self.assertNotIn(self.password,p.read_text());api.offline=False
        cloud.send(p,api);cloud.send(p,api);self.assertEqual(api.writes,1)
        # Simular pérdida de acuse sin borrar nada: misma operación en otro archivo de QA.
        replay=self.folder/'replay.json';replay.write_bytes(p.read_bytes());cloud.send(replay,api)
        self.assertEqual(api.writes,1)
    def test_two_projects_and_two_passwords(self):
        api=API();a=cloud.enqueue(ROOT/'02 Input'/'DEMO_A.wpcx',self.password,self.folder)
        other=secrets.token_urlsafe(20);b=cloud.enqueue(ROOT/'02 Input'/'DEMO_B.wpcx',other,self.folder)
        cloud.send(a,api);cloud.send(b,api);self.assertEqual(len(api.files),2)
        for raw in api.files.values():
            e=json.loads(base64.b64decode(raw));expected=self.password if e['client']=='a' else other
            self.assertEqual(cloud.decrypt(e,expected)['project']['client'],e['client'])
    def test_browser_webcrypto_interoperability(self):
        envelope=cloud.encrypt(self.summary,self.password)
        module=(ROOT/'00 Code'/'visor'/'protegido'/'protocol.mjs').as_uri()
        js='''import {webcrypto} from 'node:crypto';
if(!globalThis.crypto)Object.defineProperty(globalThis,'crypto',{value:webcrypto});
const chunks=[];for await (const c of process.stdin)chunks.push(c);
const input=JSON.parse(Buffer.concat(chunks).toString());
const {importPassword,decryptEnvelope}=await import(input.module);
const payload=await decryptEnvelope(input.envelope,await importPassword(input.password));
let rejected=false;try{await decryptEnvelope(input.envelope,await importPassword('not-the-password'));}catch{rejected=true;}
if(payload.project.client!=='a'||!rejected)process.exit(1);
console.log('OK Web Crypto: compatibilidad Python y rechazo de contraseña incorrecta');'''
        result=subprocess.run(['node','--input-type=module','-e',js],input=json.dumps({'envelope':envelope,'password':self.password,'module':module}),text=True,capture_output=True)
        self.assertEqual(result.returncode,0,'Falló compatibilidad Web Crypto (detalles no impresos por seguridad)')
    def test_invalid_source_never_queued(self):
        with self.assertRaises(Exception):cloud.enqueue(ROOT/'README.md',self.password,self.folder)
        self.assertEqual(len(list(self.folder.glob('*.json'))),0)


if __name__=='__main__':unittest.main(verbosity=2)
