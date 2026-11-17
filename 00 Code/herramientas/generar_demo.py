"""Genera exclusivamente datos ficticios, sin leer proyectos de WPC."""
import argparse
import hashlib
import json
from pathlib import Path
import uuid
import zipfile
from publicador_pc import PROJECTS, ROOT, dumps, summarize

STAMP='2026-11-17T12:00:00+00:00'


def create_package(client, path, extra=False):
    path=Path(path)
    if path.exists():
        raise FileExistsError('No se sobrescriben paquetes existentes: '+str(path))
    path.parent.mkdir(parents=True,exist_ok=True)
    project_id=str(uuid.uuid5(uuid.NAMESPACE_DNS,'hidrolog-demo-publica-'+client))
    holes=[];turns=[];rows=[]
    for index,(hole_id,(group,code)) in enumerate(PROJECTS.items()):
        if group!=client:continue
        turn_id=str(uuid.uuid5(uuid.NAMESPACE_DNS,hole_id+'turno'))
        common={'creado':STAMP,'modificado':STAMP,'dispositivo':'pc-demo','origen':'pc','extra':{}}
        holes.append({**common,'id':hole_id,'proyecto_id':project_id,'proyecto':'DEMO PÚBLICA '+client.upper(),
                      'codigo':code,'crs':'WGS84_UTM18S','este':0,'norte':0,'cota':0,'azimut':0,'inclinacion':90,
                      'diametro':'HQ (63.5 mm)','diametro_cambios':'','turno_activo':turn_id})
        turns.append({**common,'id':turn_id,'sondaje_id':hole_id,'fecha':'2026-11-17','hora':'07:00','turno':'Dia','geologo':'Operador ficticio'})
        count=(4 if index%2==0 else 3)+(1 if extra and index%2==0 else 0)
        for i in range(count):
            rows.append({**common,'id':str(uuid.uuid5(uuid.NAMESPACE_DNS,hole_id+':'+str(i))),
                         'sondaje_id':hole_id,'turno_id':turn_id,'desde':i*3,'hasta':(i+1)*3,
                         'recup':2.7,'rqd':2.1,'fn':2,'fm':0,'n_lrf':0,'lrf':0,
                         'dureza':'R4','grado_f':'B','grado_a':'A','agua':'seco',
                         'descripcion':'DATOS FICTICIOS PARA PRUEBA PÚBLICA','coment':''})
    data={'sondajes':holes,'turnos':turns,'filas':rows,'estructuras':[],'ensayos':[],
          'eliminados':[],'historial':[],'importaciones':[]}
    raw=dumps(data)
    manifest={'formato':'wpc-intercambio','version':1,'version_esquema':3,
              'app':'hidrolog-demo-sintetica','app_version':'1.0.0','dispositivo':'pc-demo',
              'geologo':'Operador ficticio','fecha_exportacion':STAMP,'proyecto_archivo':True,
              'proyecto':{'uuid':project_id,'nombre':'DEMO PÚBLICA '+client.upper(),
                          'descripcion':'Solo datos ficticios. No usar como proyecto productivo.','crs':'WGS84_UTM18S'},
              'sondajes':[h['id'] for h in holes],
              'conteo':{key:len(data[key]) for key in ['sondajes','turnos','filas','estructuras','ensayos']},
              'archivos':{'datos.json':{'sha256':hashlib.sha256(raw).hexdigest()}}}
    with zipfile.ZipFile(path,'x',compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('manifest.json',dumps(manifest));archive.writestr('datos.json',raw)
    return path


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--folder',type=Path,default=ROOT/'02 Input')
    args=parser.parse_args()
    paths=[create_package(c,args.folder/f'DEMO_{c.upper()}.wpcx') for c in ['a','b']]
    state={'version':1,'synthetic_only':True,'last_received_utc':None,'projects':[summarize(p) for p in paths]}
    output=args.folder/'estado_demo.json'
    with output.open('xb') as f:f.write(dumps(state))
    print('Creados: dos paquetes ficticios y estado inicial; ningún archivo preexistente se modificó.')


if __name__=='__main__':main()
