"""Botón de escritorio independiente y entrada JSON por stdin para Tauri."""
import json
import sys
import threading
from pathlib import Path
from cloud_core import ROOT,VIEWER,publish,pending,send


def bridge():
    # No aceptar contraseñas por argumentos ni escribirlas en logs.
    try:
        value=json.loads(sys.stdin.buffer.read(8192))
        if set(value)!={'path','password'}:raise ValueError('Entrada inválida')
        result=publish(value['path'],value['password']);value['password']=''
    except Exception:
        result={'ok':False,'queued':False,'message':'No se pudo preparar el envío. Revisa el proyecto ficticio y los requisitos de la contraseña.'}
    print(json.dumps(result,ensure_ascii=False))


def gui(initial_path=None):
    import tkinter as tk
    from tkinter import ttk,filedialog,messagebox
    import webbrowser
    root=tk.Tk();root.title('HidroLog · Módulo Subir a la nube');root.geometry('850x600');root.configure(bg='#F2F2F2')
    style=ttk.Style();style.configure('Title.TLabel',foreground='#002060',font=('Segoe UI',20,'bold'))
    path=tk.StringVar(value=initial_path or str(ROOT/'02 Input'/'DEMO_A.wpcx'))
    password=tk.StringVar();repeat=tk.StringVar();offline=tk.BooleanVar(value=False);viewer=tk.StringVar(value=VIEWER+'?cliente=a')
    ttk.Label(root,text='WPC | HidroLog · Subir a la nube',style='Title.TLabel').pack(anchor='w',padx=24,pady=18)
    ttk.Label(root,text='Prueba con datos ficticios. El resumen se cifra antes de subirlo a GitHub.',wraplength=790).pack(anchor='w',padx=24)
    frame=ttk.Frame(root);frame.pack(fill='x',padx=24,pady=16)
    ttk.Entry(frame,textvariable=path).pack(side='left',fill='x',expand=True)
    ttk.Button(frame,text='Elegir proyecto guardado',command=lambda:path.set(filedialog.askopenfilename(initialdir=str(ROOT/'02 Input'),filetypes=[('HidroLog','*.wpcx')]) or path.get())).pack(side='right',padx=8)
    form=ttk.Frame(root);form.pack(fill='x',padx=24)
    ttk.Label(form,text='Contraseña del visor de prueba (recomendamos una frase larga)').grid(row=0,column=0,sticky='w',pady=5)
    ttk.Entry(form,textvariable=password,show='•',width=38).grid(row=0,column=1,padx=12)
    ttk.Label(form,text='Repetir contraseña').grid(row=1,column=0,sticky='w',pady=5)
    ttk.Entry(form,textvariable=repeat,show='•',width=38).grid(row=1,column=1,padx=12)
    ttk.Label(root,text='Compártela por un canal separado del enlace. No se guarda en el repositorio ni en la cola local.',wraplength=790).pack(anchor='w',padx=24,pady=12)
    status=tk.StringVar(value='Listo. Selecciona una copia del proyecto ficticio, elige contraseña y pulsa Subir a la nube.')
    ttk.Label(root,textvariable=status,wraplength=790).pack(anchor='w',padx=24,pady=10)
    ttk.Checkbutton(root,text='Simular falta de conexión: cifrar y dejar pendiente',variable=offline).pack(anchor='w',padx=24,pady=10)
    actions=ttk.Frame(root);actions.pack(fill='x',padx=24,pady=12)
    def finish(result):
        upload.configure(state='normal');retry.configure(state='normal')
        if result.get('ok'):
            viewer.set(result['viewer_url']);status.set('Subida confirmada. Abre el visor y comparte su enlace y contraseña. Puede haber demora de caché.')
        else:status.set(result.get('message','No se confirmó el envío. Los pendientes se conservan.'))
    def start(retry_only=False):
        value=password.get()
        if not retry_only and (value!=repeat.get() or not 6<=len(value)<=256):
            messagebox.showwarning('Contraseña','Las contraseñas de demo deben coincidir y tener al menos 6 caracteres.');return
        route=path.get();simulate=offline.get()
        password.set('');repeat.set('');upload.configure(state='disabled');retry.configure(state='disabled');status.set('Preparando envío cifrado…')
        def work(secret):
            try:
                if retry_only:
                    jobs=pending()
                    if not jobs:result={'ok':False,'message':'No hay envíos pendientes.'}
                    elif simulate:result={'ok':False,'message':'Sin conexión simulada: se conservan los pendientes.'}
                    else:
                        result={}
                        for job in jobs:result={'ok':True,**send(job)}
                elif simulate:
                    from cloud_core import enqueue
                    enqueue(route,secret);result={'ok':False,'queued':True,'message':'Guardado cifrado en la cola del PC. Desactiva la simulación y pulsa Reintentar pendientes.'}
                else:result=publish(route,secret)
            except Exception:result={'ok':False,'message':'No se confirmó la operación. Revisa el proyecto ficticio o la conexión. Los archivos existentes se conservan.'}
            finally:secret=''
            root.after(0,lambda r=result:finish(r))
        threading.Thread(target=work,args=(value,),daemon=True).start()
    upload=ttk.Button(actions,text='☁  Subir a la nube',command=start);upload.pack(side='left')
    retry=ttk.Button(actions,text='Reintentar pendientes',command=lambda:start(True));retry.pack(side='left',padx=10)
    ttk.Button(actions,text='Abrir dashboard',command=lambda:webbrowser.open(viewer.get())).pack(side='left')
    ttk.Label(root,text='Enlace del visor').pack(anchor='w',padx=24,pady=(15,4))
    ttk.Entry(root,textvariable=viewer,state='readonly').pack(fill='x',padx=24)
    ttk.Label(root,text='No hay cuentas individuales. Quien tenga la contraseña puede leer el resumen. No usar datos reales en esta demo.',wraplength=790).pack(anchor='w',padx=24,pady=16)
    root.mainloop()


if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='bridge':bridge()
    else:gui(sys.argv[1] if len(sys.argv)>1 else None)
