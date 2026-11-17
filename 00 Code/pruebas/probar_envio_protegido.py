"""Prueba real autorizada. La clave se recibe oculta; nunca se guarda ni imprime."""
import base64
import getpass
import json
from pathlib import Path
import sys
import uuid
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'modulo_nube'))
import cloud_core as cloud
from generar_demo import create_package
from github_api import repo_request


def main():
    print('Prueba de envío cifrado. Introduce la clave por la entrada oculta.',flush=True)
    password=getpass.getpass('Clave (no se muestra): ')
    folder=cloud.ROOT/'03 Output'/('QA_PROT_'+uuid.uuid4().hex[:8]);folder.mkdir(parents=True)
    first=cloud.publish(cloud.ROOT/'02 Input'/'DEMO_A.wpcx',password,folder/'cola')
    assert first['ok'],'No se confirmó la primera publicación'
    modified=create_package('a',folder/'A_actualizado.wpcx',extra=True)
    second=cloud.publish(modified,password,folder/'cola');assert second['ok'],'No se confirmó la actualización'
    status,remote=repo_request('GET','/contents/02%20Input/protegido/a.json?ref=main');assert status==200
    envelope=json.loads(base64.b64decode(remote['content']));payload=cloud.decrypt(envelope,password)
    meters=sum(h['logged_m'] for h in payload['project']['holes']);assert meters==24
    report={'encrypted_upload':True,'initial_logged_m':21,'updated_logged_m':meters,
            'commit':second['commit'],'viewer_url':second['viewer_url'],
            'password_saved':False,'source_gui_tested':False,'tauri_compiled':False,'android_tested':False}
    (folder/'RESULTADO.json').write_bytes(cloud.pack(report))
    password=''
    print(json.dumps(report,ensure_ascii=False),flush=True)


if __name__=='__main__':main()
