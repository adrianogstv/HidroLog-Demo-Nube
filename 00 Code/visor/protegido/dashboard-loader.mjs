import {decryptEnvelope} from './protocol.mjs';
let generation=0,ready=false,current=null,htmlLoaded=false;
const frame=()=>document.getElementById('dashboard-frame');
const status=message=>{document.getElementById('dashboard-status').textContent=message;};
function send(){if(ready&&current&&frame()?.contentWindow)frame().contentWindow.postMessage({type:'wpc-cloud-snapshot',archive:current.archive,operation:current.operation},'*');}
window.addEventListener('message',event=>{
 if(event.source!==frame()?.contentWindow)return;
 const message=event.data;
 if(message?.type==='wpc-cloud-ready'){ready=true;send();}
 else if(message?.operation===current?.operation&&message.type==='wpc-cloud-applied')status('Datos de HidroLog actualizados · '+message.holes+' sondaje(s) en 3D'+(message.withoutCollar?' · '+message.withoutCollar+' sin collar completo':'')+'. Mallas de labores, vetas, fallas y terreno pendientes.');
 else if(message?.type==='wpc-cloud-error'&&(message.operation===null||message.operation===current?.operation))status(message.message+' El resumen y la copia descargable siguen disponibles.');
});
export function bloquearDashboard(){generation++;ready=false;current=null;htmlLoaded=false;const f=frame();if(f){f.srcdoc='';f.hidden=true;}status('Visor bloqueado.');}
export async function aplicarDashboard(payload,material){
 const token=++generation;
 if(!payload.archive){status('Esta publicación antigua no incluye la copia completa. Vuelve a subir desde HidroLog actualizado.');return;}
 current={archive:payload.archive,operation:payload.published_at+':'+payload.project.snapshot_hash};
 if(htmlLoaded){send();return;}
 status('Abriendo dashboard de seguimiento…');
 try{
  const response=await fetch(new URL('dashboard-template.enc.json',import.meta.url),{cache:'no-store',credentials:'omit'});
  if(!response.ok)throw Error('No se pudo descargar la plantilla del dashboard.');
  const result=await decryptEnvelope(await response.json(),material);
  if(token!==generation)return;
  if(typeof result.project.html_gzip_base64!=='string')throw Error('Plantilla no compatible.');
  const bytes=Uint8Array.from(atob(result.project.html_gzip_base64),c=>c.charCodeAt(0));
  const html=await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text();
  if(token!==generation)return;
  const f=frame();f.srcdoc=html;f.hidden=false;htmlLoaded=true;
 }catch(error){if(token===generation)status(error.message+' Se conserva el resumen del proyecto.');}
}
