import {aplicarDashboard,bloquearDashboard} from './dashboard-loader.mjs';
import {decryptEnvelope,importPassword} from './protocol.mjs';
const $=id=>document.getElementById(id);
let material=null,lastOperation=null,busy=false,generation=0,archive=null;
const validClient=x=>/^(?:a|b|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$/.test(x||'');
const requested=new URLSearchParams(location.search).get('cliente');if(validClient(requested)){if(![...$('client').options].some(o=>o.value===requested)){const option=document.createElement('option');option.value=requested;option.textContent='Proyecto compartido';$('client').append(option);}$('client').value=requested;}
const fmt=n=>Number(n).toLocaleString('es-PE',{maximumFractionDigits:2});
const date=s=>new Date(s).toLocaleString('es-PE',{timeZone:'America/Lima'})+' · Lima';
function clear(){
  document.body.classList.remove('dashboard-only');
  bloquearDashboard();
  material=null;archive=null;$('download').disabled=true;lastOperation=null;generation++;busy=false;$('password').value='';$('rows').replaceChildren();
  for(const id of ['meters','runs','recovery','holes','published','read','project-label'])$(id).textContent='—';
  $('viewer').hidden=true;$('lock').hidden=true;$('gate').hidden=false;$('unlock').disabled=false;$('refresh').disabled=false;
}
function render(payload){
  archive=payload.archive||null;$('download').disabled=!archive;
  const p=payload.project,holes=p.holes,meters=holes.reduce((s,h)=>s+h.logged_m,0),recovery=holes.reduce((s,h)=>s+h.recovered_m,0);
  $('project-label').textContent=p.label;const option=[...$('client').options].find(o=>o.value===p.client);if(option)option.textContent=p.label;$('meters').textContent=fmt(meters)+' m';$('runs').textContent=fmt(holes.reduce((s,h)=>s+h.runs,0));$('holes').textContent=String(holes.length);$('recovery').textContent=meters?fmt(100*recovery/meters)+' %':'—';
  $('published').textContent=date(payload.published_at);$('rows').replaceChildren();
  for(const h of holes){const tr=document.createElement('tr');for(const value of [h.code,fmt(h.logged_m),fmt(h.max_depth_m),fmt(h.recovered_m),fmt(h.runs)]){const td=document.createElement('td');td.textContent=value;tr.append(td);}$('rows').append(tr);}
  document.body.classList.add('dashboard-only');
  $('gate').hidden=true;$('viewer').hidden=false;$('lock').hidden=false;
}
async function read(candidate=material,unlock=false){
  if(!candidate||busy)return;busy=true;const version=++generation,client=$('client').value;
  $('unlock').disabled=true;$('refresh').disabled=true;
  try{
    const url='https://raw.githubusercontent.com/adrianogstv/HidroLog-Demo-Nube/main/02%20Input/protegido/'+client+'.json?read='+Date.now();
    const response=await fetch(url,{cache:'no-store',credentials:'omit',signal:AbortSignal.timeout(20000)});
    if(!response.ok){const e=Error('No disponible');e.network=true;e.missing=response.status===404;throw e;}
    const envelope=await response.json();if(version!==generation)return;
    if(envelope.client!==client)throw Error('Proyecto incorrecto');
    if(unlock||envelope.operation_id!==lastOperation){
      let payload;
      try{payload=await decryptEnvelope(envelope,candidate);}catch{const e=Error('No se pudo descifrar');e.unlock=true;throw e;}
      if(version!==generation)return;
      material=candidate;lastOperation=envelope.operation_id;render(payload);aplicarDashboard(payload,candidate);
    }
    $('read').textContent=date(new Date().toISOString());$('status').classList.remove('error');$('status').textContent='Última versión consultada. El remitente actualiza al pulsar Subir a la nube.';
  }catch(e){
    if(version!==generation)return;
    if(unlock||e.unlock){clear();$('login-status').classList.add('error');$('login-status').textContent=e.missing?'Todavía no se ha publicado este proyecto protegido.':e.network?'No se pudo consultar GitHub. Comprueba la conexión.':'No se pudo abrir. Comprueba la contraseña; si cambió, solicita la nueva al remitente.';}
    else{$('status').classList.add('error');$('status').textContent='Sin actualización confirmada. Se conserva la última lectura, que puede estar desactualizada.';}
  }finally{if(version===generation){busy=false;$('unlock').disabled=false;$('refresh').disabled=false;}}
}
$('login').addEventListener('submit',async e=>{e.preventDefault();const password=$('password').value;$('password').value='';$('login-status').classList.remove('error');$('login-status').textContent='Comprobando contraseña…';await read(await importPassword(password),true);});
$('lock').addEventListener('click',()=>{clear();$('login-status').textContent='Visor bloqueado. Introduce la contraseña para volver a abrirlo.';});
$('client').addEventListener('change',()=>{const key=material;clear();if(key){material=key;read(key,true);}else $('login-status').textContent='Introduce la clave única de la web.';});
$('refresh').addEventListener('click',()=>read());setInterval(()=>{if(material&&$('auto').checked&&!document.hidden)read();},30000);
document.addEventListener('visibilitychange',()=>{if(!document.hidden&&material&&$('auto').checked)read();});
window.addEventListener('pagehide',()=>{clear();});

$('download').addEventListener('click',async()=>{
  if(!archive||archive.encoding!=='base64')return;
  const bytes=Uint8Array.from(atob(archive.content),c=>c.charCodeAt(0));
  const hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(v=>v.toString(16).padStart(2,'0')).join('');
  if(hash!==archive.sha256){$('status').textContent='No coincide la integridad de la copia. No se descargó.';return;}
  const url=URL.createObjectURL(new Blob([bytes],{type:'application/octet-stream'}));
  const a=document.createElement('a');a.href=url;a.download=String(archive.name||'Proyecto.wpcx').split(/[\\/]/).pop();a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
});
(async()=>{try{
  const response=await fetch('https://api.github.com/repos/adrianogstv/HidroLog-Demo-Nube/contents/02%20Input/protegido',{credentials:'omit'});
  if(!response.ok)return;const files=await response.json();
  for(const file of files){const id=String(file.name).replace(/\.json$/,'');if(!validClient(id)||[...$('client').options].some(o=>o.value===id))continue;const o=document.createElement('option');o.value=id;o.textContent='Proyecto '+id.slice(0,8);$('client').append(o);}
}catch{}})();
