import {decryptEnvelope,importPassword} from './protocol.mjs';
const $=id=>document.getElementById(id);
let material=null,lastOperation=null,busy=false,generation=0;
const requested=new URLSearchParams(location.search).get('cliente');if(['a','b'].includes(requested))$('client').value=requested;
const fmt=n=>Number(n).toLocaleString('es-PE',{maximumFractionDigits:2});
const date=s=>new Date(s).toLocaleString('es-PE',{timeZone:'America/Lima'})+' · Lima';
function clear(){
  material=null;lastOperation=null;generation++;busy=false;$('password').value='';$('rows').replaceChildren();
  for(const id of ['meters','runs','recovery','holes','published','read','project-label'])$(id).textContent='—';
  $('viewer').hidden=true;$('lock').hidden=true;$('gate').hidden=false;$('unlock').disabled=false;$('refresh').disabled=false;
}
function render(payload){
  const p=payload.project,holes=p.holes,meters=holes.reduce((s,h)=>s+h.logged_m,0),recovery=holes.reduce((s,h)=>s+h.recovered_m,0);
  $('project-label').textContent=p.label;$('meters').textContent=fmt(meters)+' m';$('runs').textContent=fmt(holes.reduce((s,h)=>s+h.runs,0));$('holes').textContent=String(holes.length);$('recovery').textContent=meters?fmt(100*recovery/meters)+' %':'—';
  $('published').textContent=date(payload.published_at);$('rows').replaceChildren();
  for(const h of holes){const tr=document.createElement('tr');for(const value of [h.code,fmt(h.logged_m),fmt(h.max_depth_m),fmt(h.recovered_m),fmt(h.runs)]){const td=document.createElement('td');td.textContent=value;tr.append(td);}$('rows').append(tr);}
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
      material=candidate;lastOperation=envelope.operation_id;render(payload);
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
$('client').addEventListener('change',()=>{clear();$('login-status').textContent='Introduce la contraseña de este proyecto.';});
$('refresh').addEventListener('click',()=>read());setInterval(()=>{if(material&&$('auto').checked&&!document.hidden)read();},30000);
document.addEventListener('visibilitychange',()=>{if(!document.hidden&&material&&$('auto').checked)read();});
window.addEventListener('pagehide',()=>{clear();});
