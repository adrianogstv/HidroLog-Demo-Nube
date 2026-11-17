"""Prueba PC → GitHub. Solo permite resúmenes de los sondajes ficticios incluidos."""
import argparse
import base64
import hashlib
import json
import math
from pathlib import Path
import threading
import uuid
import zipfile
from datetime import datetime, timezone

from github_api import OWNER, REPO, repo_request

ROOT = Path(__file__).resolve().parents[2]
REMOTE = '/contents/02%20Input/estado_demo.json'
PROJECTS = {
    '11111111-1111-4111-8111-111111111111': ('a', 'DEMO-A-01'),
    '11111111-1111-4111-8111-111111111112': ('a', 'DEMO-A-02'),
    '22222222-2222-4222-8222-222222222221': ('b', 'DEMO-B-01'),
    '22222222-2222-4222-8222-222222222222': ('b', 'DEMO-B-02'),
}


def utc():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def dumps(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False).encode('utf-8')


def number(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'{name}: número inválido')
    if not 0 <= value <= 1000:
        raise ValueError(f'{name}: fuera del rango de la demo')
    return round(float(value), 4)


def summarize(path):
    path = Path(path)
    if path.stat().st_size > 2_000_000:
        raise ValueError('La demo solo admite paquetes de hasta 2 MB.')
    with zipfile.ZipFile(path) as archive:
        for name in ('manifest.json', 'datos.json'):
            if archive.namelist().count(name) != 1 or archive.getinfo(name).file_size > 1_000_000:
                raise ValueError('Paquete inválido o demasiado grande.')
        manifest = json.loads(archive.read('manifest.json'))
        raw = archive.read('datos.json')
    if manifest.get('formato') != 'wpc-intercambio' or manifest.get('version') != 1:
        raise ValueError('No es un paquete .wpcx compatible.')
    if manifest.get('archivos', {}).get('datos.json', {}).get('sha256') != digest(raw):
        raise ValueError('El SHA-256 del paquete no coincide.')
    data = json.loads(raw)
    holes = data.get('sondajes', [])
    if not holes or any(h.get('id') not in PROJECTS for h in holes):
        raise ValueError('Rechazado: contiene sondajes que no son de los ficticios autorizados.')
    if len({h['id'] for h in holes}) != len(holes):
        raise ValueError('Sondajes duplicados.')
    clients = {PROJECTS[h['id']][0] for h in holes}
    if len(clients) != 1:
        raise ValueError('Cada paquete debe pertenecer a un único cliente ficticio.')
    client = clients.pop()
    rows = data.get('filas', [])
    if len(rows) > 1000:
        raise ValueError('Demasiadas corridas para la demo.')
    if len({r.get('id') for r in rows}) != len(rows) or any(not isinstance(r.get('id'), str) for r in rows):
        raise ValueError('Identificadores de corrida inválidos o duplicados.')
    hole_ids = {h['id'] for h in holes}
    if any(r.get('sondaje_id') not in hole_ids for r in rows):
        raise ValueError('Hay corridas sin sondaje autorizado.')
    result = []
    for h in holes:
        intervals = []
        for row in rows:
            if row.get('sondaje_id') != h['id']:
                continue
            start = number(row.get('desde'), 'Desde')
            end = number(row.get('hasta'), 'Hasta')
            recovery = number(row.get('recup'), 'Recuperación')
            if end <= start or recovery > end - start + 1e-8:
                raise ValueError('Longitud o recuperación no válida.')
            intervals.append((start, end, recovery))
        intervals.sort()
        if any(a[1] > b[0] + 1e-8 for a, b in zip(intervals, intervals[1:])):
            raise ValueError('La demo no admite corridas superpuestas.')
        # Solo números y etiquetas constantes: no publicar textos del archivo de origen.
        result.append({'id': h['id'], 'code': PROJECTS[h['id']][1], 'logged_m': round(sum(b-a for a,b,c in intervals), 4),
                       'max_depth_m': max((b for a,b,c in intervals), default=0),
                       'recovered_m': round(sum(c for a,b,c in intervals), 4), 'runs': len(intervals),
                       'intervals': [[a,b] for a,b,c in intervals]})
    clean = {'client': client, 'label': f'Cliente ficticio {client.upper()}', 'holes': sorted(result, key=lambda x:x['id'])}
    clean['snapshot_hash'] = digest(dumps(clean))
    return clean


def enqueue(path, folder=None):
    summary = summarize(path)
    folder = Path(folder) if folder else ROOT/'03 Output'/'Cola_PC'
    folder.mkdir(parents=True, exist_ok=True)
    job = {'job_id': str(uuid.uuid4()), 'queued_at': utc(), 'status': 'pendiente', 'summary': summary}
    target = folder/(datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_') + job['job_id'] + '.json')
    target.write_bytes(dumps(job))
    return target


def publish_job(path, api=repo_request):
    path = Path(path)
    job = json.loads(path.read_text(encoding='utf-8'))
    if job.get('status') == 'confirmado':
        return 'Ya estaba confirmado; no se repite el envío.'
    summary = job['summary']
    # Revalidar estructura de cola y no aceptar payloads arbitrarios como archivos o claves.
    allowed = {'client','label','holes','snapshot_hash'}
    if set(summary) != allowed or summary['client'] not in {'a','b'}:
        raise ValueError('Cola inválida.')
    if summary['snapshot_hash'] != digest(dumps({k:v for k,v in summary.items() if k!='snapshot_hash'})):
        raise ValueError('El resumen local fue alterado.')
    if summary['label'] != f"Cliente ficticio {summary['client'].upper()}" or not isinstance(summary['holes'],list):
        raise ValueError('Etiqueta o sondajes no válidos.')
    for hole in summary['holes']:
        if set(hole) != {'id','code','logged_m','max_depth_m','recovered_m','runs','intervals'}:
            raise ValueError('El resumen contiene campos no permitidos.')
        if hole['id'] not in PROJECTS or PROJECTS[hole['id']] != (summary['client'],hole['code']):
            raise ValueError('Sondaje no permitido en la cola.')
        for field in ['logged_m','max_depth_m','recovered_m','runs']:
            number(hole[field],field)
        if not isinstance(hole['intervals'],list) or len(hole['intervals'])>1000:
            raise ValueError('Intervalos inválidos.')
        for interval in hole['intervals']:
            if not isinstance(interval,list) or len(interval)!=2:
                raise ValueError('Intervalo inválido.')
            number(interval[0],'Desde');number(interval[1],'Hasta')
    for _ in range(3):
        status, remote = api('GET', REMOTE)
        if status != 200:
            raise RuntimeError(f'GitHub HTTP {status}: no se pudo leer el estado. La cola se conserva.')
        current = json.loads(base64.b64decode(remote['content']))
        if current.get('synthetic_only') is not True:
            raise ValueError('El destino no está identificado como demo ficticia.')
        known = next((p for p in current['projects'] if p['client']==summary['client']), None)
        if not known or known['snapshot_hash'] != summary['snapshot_hash']:
            current['projects'] = [p for p in current['projects'] if p['client']!=summary['client']] + [summary]
            current['projects'].sort(key=lambda p:p['client'])
            current['last_received_utc'] = utc()
            body = {'message':'Actualizar resumen ficticio desde PC', 'branch':'main', 'sha':remote['sha'],
                    'content':base64.b64encode(dumps(current)).decode('ascii')}
            status, response = api('PUT', REMOTE, body)
            if status in (409,422):
                continue
            if status not in (200,201):
                raise RuntimeError(f'GitHub HTTP {status}: envío no confirmado; pendiente conservado.')
            commit = response['commit']['sha']
        else:
            commit = 'resumen ya presente; no se generó otro commit'
        # Acuse solo después del éxito remoto. Si esto falla, el reintento compara snapshot_hash.
        job.update(status='confirmado', confirmed_at=utc(), commit=commit)
        path.write_bytes(dumps(job))
        return 'Confirmado en GitHub: ' + commit
    raise RuntimeError('El estado cambió durante el envío. Reintenta; la cola se conserva.')


def gui():
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    root=tk.Tk();root.title('HidroLog · Publicador de prueba PC → GitHub');root.geometry('850x540')
    root.configure(bg='#F2F2F2');path=tk.StringVar();offline=tk.BooleanVar(value=False)
    ttk.Label(root,text='WPC | HidroLog · Prueba de escritorio',font=('Segoe UI',19,'bold')).pack(anchor='w',padx=24,pady=18)
    ttk.Label(root,text='DEMO PÚBLICA. Solo admite los sondajes ficticios incluidos. No cargar proyectos de cliente.',wraplength=790).pack(anchor='w',padx=24)
    frame=ttk.Frame(root);frame.pack(fill='x',padx=24,pady=16)
    ttk.Entry(frame,textvariable=path).pack(side='left',fill='x',expand=True)
    ttk.Button(frame,text='Elegir .wpcx',command=lambda:path.set(filedialog.askopenfilename(initialdir=str(ROOT/'02 Input'),filetypes=[('HidroLog','*.wpcx')]) or path.get())).pack(side='right',padx=6)
    info=tk.Text(root,height=10,wrap='word',font=('Segoe UI',11));info.pack(fill='both',expand=True,padx=24,pady=8)
    def log(text):
        info.insert('end',text+'\n');info.see('end')
    def queue():
        try:
            job=enqueue(path.get());summary=json.loads(job.read_text(encoding='utf-8'))['summary']
            log(f"Guardado local: {summary['label']}, {sum(h['runs'] for h in summary['holes'])} corridas. Pendiente: {job.name}")
        except Exception as e:messagebox.showerror('No se encoló',str(e))
    def send():
        if offline.get():log('Sin conexión simulada: la cola permanece local.');return
        button.configure(state='disabled');log('Enviando pendientes; la autenticación permanece en este PC…')
        def work():
            try:
                jobs=sorted((ROOT/'03 Output'/'Cola_PC').glob('*.json'))
                pending=[p for p in jobs if json.loads(p.read_text(encoding='utf-8')).get('status')!='confirmado']
                if not pending:root.after(0,lambda:log('No hay pendientes.'))
                for p in pending:
                    message=publish_job(p);root.after(0,lambda m=message:log(m))
            except Exception as e:root.after(0,lambda m=str(e):log('No confirmado: '+m))
            finally:root.after(0,lambda:button.configure(state='normal'))
        threading.Thread(target=work,daemon=True).start()
    ttk.Checkbutton(root,text='Simular sin internet (conserva pendientes)',variable=offline).pack(anchor='w',padx=24,pady=8)
    actions=ttk.Frame(root);actions.pack(fill='x',padx=24,pady=15)
    ttk.Button(actions,text='1. Validar y guardar en cola',command=queue).pack(side='left')
    button=ttk.Button(actions,text='2. Enviar pendientes a GitHub',command=send);button.pack(side='left',padx=12)
    ttk.Label(root,text='Envío manual. No se instala un monitor ni se modifica HidroLog. El dashboard actualiza su lectura cada 30 s.',wraplength=790).pack(anchor='w',padx=24,pady=10)
    log('Abre DEMO_A.wpcx o DEMO_B.wpcx en HidroLog PC; guarda y selecciona el archivo aquí.\nTambién puedes probar directamente con los paquetes incluidos.\nLa demostración es pública y no ofrece acceso privado por cliente.')
    root.mainloop()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['gui','check','enqueue','publish'],nargs='?',default='gui')
    parser.add_argument('file',nargs='?')
    parser.add_argument('--queue-folder')
    args=parser.parse_args()
    if args.action=='gui':gui()
    elif args.action=='check':print(json.dumps(summarize(args.file),ensure_ascii=False,indent=2))
    elif args.action=='enqueue':print(enqueue(args.file,args.queue_folder))
    elif args.action=='publish':print(publish_job(args.file))


if __name__=='__main__':main()
