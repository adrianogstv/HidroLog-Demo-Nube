/** Botón desacoplado: recibe estado del proyecto e invoke de Tauri por inyección. */
export function crearModuloNube({obtenerEstado,invocar,informar=()=>{}}){
  if(typeof obtenerEstado!=='function'||typeof invocar!=='function')throw Error('Faltan adaptadores del módulo nube');
  let enviando=false;
  const bloque=document.createElement('span');bloque.className='hidrolog-nube';
  const boton=document.createElement('button');boton.type='button';boton.textContent='☁ Subir a la nube';boton.className='toolbtn';
  const estado=document.createElement('span');estado.className='nube-estado';estado.setAttribute('role','status');bloque.append(boton,estado);
  const avisar=(mensaje,tipo='info')=>{estado.textContent=mensaje;informar(mensaje,tipo);};
  async function subir(path,password){
    if(enviando)return null;enviando=true;boton.disabled=true;avisar('Subiendo resumen cifrado…');
    try{
      const result=await invocar('nube_subir_proyecto',{ruta:path,password});
      if(result?.ok){avisar('Subida confirmada','success');return result;}
      avisar(result?.queued?'Sin confirmación: envío cifrado guardado para reintentar.':(result?.message||'No se pudo preparar el envío.'),'warning');return result;
    }catch{avisar('No se pudo completar. Revisa el módulo nativo y la conexión.','error');return {ok:false};}
    finally{password='';enviando=false;boton.disabled=false;}
  }
  boton.addEventListener('click',()=>{
    const proyecto=obtenerEstado();
    if(!proyecto?.abierto||!proyecto?.ruta){avisar('Abre un proyecto ficticio antes de subir.','warning');return;}
    if(proyecto.sinGuardar){avisar('Guarda el proyecto antes de subir; no se publican ediciones sin guardar.','warning');return;}
    const dialog=document.createElement('dialog');dialog.className='hidrolog-nube-dialog';
    const form=document.createElement('form');const title=document.createElement('h2');title.textContent='Subir a la nube';
    const help=document.createElement('p');help.textContent='Se cifrará el resumen del proyecto guardado. Prueba exclusiva con datos ficticios.';
    const label=document.createElement('label');label.textContent='Contraseña del visor compartido';const input=document.createElement('input');input.type='password';input.required=true;input.minLength=6;input.maxLength=256;input.autocomplete='off';label.append(input);
    const repeatLabel=document.createElement('label');repeatLabel.textContent='Repetir contraseña';const repeat=document.createElement('input');repeat.type='password';repeat.required=true;repeat.autocomplete='off';repeatLabel.append(repeat);
    const error=document.createElement('p');error.setAttribute('role','status');const submit=document.createElement('button');submit.type='submit';submit.textContent='Subir a la nube';const cancel=document.createElement('button');cancel.type='button';cancel.textContent='Cancelar';
    const wipe=()=>{input.value='';repeat.value='';dialog.close();dialog.remove();};cancel.addEventListener('click',wipe);dialog.addEventListener('cancel',e=>{e.preventDefault();wipe();});
    form.append(title,help,label,repeatLabel,error,submit,cancel);dialog.append(form);document.body.append(dialog);dialog.showModal();input.focus();
    form.addEventListener('submit',async e=>{
      e.preventDefault();if(input.value!==repeat.value){error.textContent='Las contraseñas no coinciden.';return;}
      let password=input.value;if(password.length<6){error.textContent='La contraseña de demo debe tener al menos 6 caracteres.';return;}
      // Volver a comprobar estado: el proyecto pudo cambiar mientras el diálogo estaba abierto.
      const actual=obtenerEstado();if(!actual?.abierto||actual.ruta!==proyecto.ruta||actual.sinGuardar){error.textContent='El proyecto cambió. Cierra este diálogo, guarda y vuelve a subir.';return;}
      wipe();const result=await subir(proyecto.ruta,password);password='';
      if(result?.ok&&result.viewer_url)avisar('Confirmado. Visor: '+result.viewer_url,'success');
    });
  });
  return {elemento:bloque,subir,actualizar(){boton.disabled=enviando||!obtenerEstado()?.abierto;},desmontar(){bloque.remove();}};
}
