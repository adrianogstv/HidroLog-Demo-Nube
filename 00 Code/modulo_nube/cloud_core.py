"""Módulo de publicación cifrada. DEMO: solo paquetes ficticios permitidos."""
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import uuid

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'herramientas'))
from publicador_pc import summarize, ROOT
from github_api import repo_request

ITERATIONS=600_000
VIEWER='https://adrianogstv.github.io/HidroLog-Demo-Nube/protegido/'


def now():return datetime.now(timezone.utc).isoformat(timespec='seconds')
def encode(value):return base64.b64encode(value).decode('ascii')
def decode(value):return base64.b64decode(value,validate=True)
def pack(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False).encode('utf-8')
def aad(envelope):return ('hidrolog-nube-v1:'+envelope['client']+':'+envelope['operation_id']).encode('utf-8')


def encrypt(summary,password):
    if not isinstance(password,str) or len(password)<6 or len(password)>256:
        raise ValueError('La contraseña de demo debe tener entre 6 y 256 caracteres; recomendamos una frase larga.')
    envelope={'format':'hidrolog-demo-encrypted','version':1,'client':summary['client'],
              'operation_id':str(uuid.uuid4()),'iterations':ITERATIONS,'salt':encode(os.urandom(16)),
              'iv':encode(os.urandom(12))}
    key=hashlib.pbkdf2_hmac('sha256',password.encode('utf-8'),decode(envelope['salt']),ITERATIONS,32)
    payload={'version':1,'synthetic_only':True,'published_at':now(),'project':summary}
    envelope['ciphertext']=encode(AESGCM(key).encrypt(decode(envelope['iv']),pack(payload),aad(envelope)))
    return envelope


def validate(envelope):
    expected={'format','version','client','operation_id','iterations','salt','iv','ciphertext'}
    if not isinstance(envelope,dict) or set(envelope)!=expected:
        raise ValueError('Sobre cifrado inválido.')
    if envelope['format']!='hidrolog-demo-encrypted' or envelope['version']!=1 or envelope['client'] not in ('a','b') or envelope['iterations']!=ITERATIONS:
        raise ValueError('Formato no permitido.')
    if str(uuid.UUID(envelope['operation_id']))!=envelope['operation_id']:
        raise ValueError('Identificador inválido.')
    if len(decode(envelope['salt']))!=16 or len(decode(envelope['iv']))!=12 or not 16<=len(decode(envelope['ciphertext']))<=1_000_000:
        raise ValueError('Tamaño cifrado inválido.')


def decrypt(envelope,password):
    validate(envelope)
    key=hashlib.pbkdf2_hmac('sha256',password.encode('utf-8'),decode(envelope['salt']),ITERATIONS,32)
    return json.loads(AESGCM(key).decrypt(decode(envelope['iv']),decode(envelope['ciphertext']),aad(envelope)))


def receipt_path(path):return path.with_name(path.stem+'.receipt.json')


def enqueue(path,password,folder=None):
    # Validar antes de cifrar o contactar con el servicio: solo datos ficticios.
    envelope=encrypt(summarize(path),password)
    folder=Path(folder) if folder else ROOT/'03 Output'/'Cola_Cifrada'
    folder.mkdir(parents=True,exist_ok=True)
    target=folder/(envelope['operation_id']+'.json')
    # Solo se guarda el sobre cifrado; ni contraseña ni ruta de origen.
    with target.open('xb') as file:
        file.write(pack(envelope));file.flush();os.fsync(file.fileno())
    return target


def send(path,api=repo_request):
    path=Path(path);envelope=json.loads(path.read_text(encoding='utf-8'));validate(envelope)
    receipt=receipt_path(path)
    if receipt.exists():
        previous=json.loads(receipt.read_text(encoding='utf-8'))
        if previous.get('confirmed') is True and previous.get('operation_id')==envelope['operation_id']:
            return previous
        raise ValueError('Acuse local inválido; conservar archivos y revisar.')
    endpoint='/contents/02%20Input/protegido/'+envelope['client']+'.json'
    for _ in range(3):
        status,remote=api('GET',endpoint)
        if status not in (200,404):raise RuntimeError('GitHub no permitió leer el destino. El envío queda pendiente.')
        body={'message':'Actualizar demo cifrada desde boton de escritorio','branch':'main','content':encode(pack(envelope))}
        if status==200:
            old=json.loads(base64.b64decode(remote['content']));validate(old)
            if old['client']!=envelope['client']:raise ValueError('Destino incompatible; no se sobrescribió.')
            if old['operation_id']==envelope['operation_id']:
                commit='acuse recuperado: operación ya presente';break
            body['sha']=remote['sha']
        status,response=api('PUT',endpoint,body)
        if status==409:continue
        if status not in (200,201):raise RuntimeError('No se confirmó la subida. Reintenta los pendientes.')
        commit=response['commit']['sha'];break
    else:raise RuntimeError('El destino cambió durante la subida. La cola se conserva.')
    result={'confirmed':True,'operation_id':envelope['operation_id'],'confirmed_at':now(),'commit':commit,
            'viewer_url':VIEWER+'?cliente='+envelope['client']}
    # Acuse separado. El sobre original se conserva sin modificar ni eliminar.
    with receipt.open('xb') as file:file.write(pack(result));file.flush();os.fsync(file.fileno())
    return result


def publish(path,password,folder=None,api=repo_request):
    job=enqueue(path,password,folder)
    try:
        result=None
        client=json.loads(job.read_text(encoding='utf-8'))['client']
        # En un único PC, enviar primero instantáneas antiguas pendientes del mismo proyecto.
        # Así un envío offline anterior no queda para sobrescribir más tarde la nueva versión.
        for previous in pending(job.parent):
            if json.loads(previous.read_text(encoding='utf-8'))['client']==client:
                result=send(previous,api)
        return {'ok':True,**result}
    except Exception:
        return {'ok':False,'queued':True,'message':'El resumen quedó cifrado y pendiente en este PC. Reintenta cuando haya conexión o revisa la sesión de GitHub.'}


def pending(folder=None):
    folder=Path(folder) if folder else ROOT/'03 Output'/'Cola_Cifrada'
    return sorted((p for p in folder.glob('*.json') if not p.name.endswith('.receipt.json') and not receipt_path(p).exists()),key=lambda p:p.stat().st_mtime_ns)
