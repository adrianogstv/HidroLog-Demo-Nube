const $=id=>document.getElementById(id);
const source='https://raw.githubusercontent.com/adrianogstv/HidroLog-Demo-Nube/main/02%20Input/estado_demo.json';
let state=null,busy=false,lastRead=null;
const fmt=(value,decimals=1)=>Number(value).toLocaleString('es-PE',{minimumFractionDigits:decimals,maximumFractionDigits:decimals});
const date=value=>value?new Date(value).toLocaleString('es-PE',{timeZone:'America/Lima'})+' · Lima':'Estado inicial; todavía no hay envío desde PC';
function cell(text){const el=document.createElement('td');el.textContent=text;return el;}
function render(){
  if(!state)return;
  const projects=state.projects.filter(p=>$('client').value==='all'||p.client===$('client').value);
  const holes=projects.flatMap(p=>p.holes.map(h=>({...h,client:p.client,label:p.label})));
  const meters=holes.reduce((s,h)=>s+h.logged_m,0),recovery=holes.reduce((s,h)=>s+h.recovered_m,0);
  $('meters').textContent=fmt(meters)+' m';$('runs').textContent=fmt(holes.reduce((s,h)=>s+h.runs,0),0);
  $('recovery').textContent=meters?fmt(recovery/meters*100)+' %':'—';$('holes').textContent=String(holes.length);
  $('received').textContent=date(state.last_received_utc);$('read').textContent=date(lastRead);
  $('rows').replaceChildren();$('bars').replaceChildren();const max=Math.max(1,...holes.map(h=>h.logged_m));
  for(const h of holes){
    const tr=document.createElement('tr');[h.label,h.code,fmt(h.logged_m),fmt(h.max_depth_m),fmt(h.recovered_m),fmt(h.runs,0)].forEach(t=>tr.append(cell(t)));$('rows').append(tr);
    const row=document.createElement('div');row.className='barrow';const head=document.createElement('div');head.className='barhead';
    const name=document.createElement('span');name.textContent=h.code;const value=document.createElement('strong');value.textContent=fmt(h.logged_m)+' m';head.append(name,value);
    const track=document.createElement('div');track.className='track';const fill=document.createElement('div');fill.className='fill '+h.client;fill.style.width=(h.logged_m/max*100)+'%';track.append(fill);row.append(head,track);$('bars').append(row);
  }
}
async function refresh(){
  if(busy)return;busy=true;$('refresh').disabled=true;$('status').textContent='Consultando el resumen público de GitHub…';
  try{
    const response=await fetch(source+'?read='+Date.now(),{cache:'no-store',credentials:'omit',signal:AbortSignal.timeout(20000)});
    if(!response.ok)throw Error('HTTP '+response.status);
    const next=await response.json();if(next.synthetic_only!==true||next.version!==1||!Array.isArray(next.projects))throw Error('Formato de demo no reconocido');
    for(const p of next.projects){if(!['a','b'].includes(p.client)||!Array.isArray(p.holes))throw Error('Proyecto no válido');for(const h of p.holes){for(const k of ['logged_m','recovered_m','runs','max_depth_m'])if(!Number.isFinite(h[k])||h[k]<0)throw Error('Dato no válido');}}
    state=next;lastRead=new Date().toISOString();render();$('status').classList.remove('error');$('status').textContent='Lectura correcta. Fuente: GitHub. Datos ficticios; este filtro no es un control de acceso.';
  }catch(error){$('status').classList.add('error');$('status').textContent='No se pudo actualizar. '+(state?'Se conserva la última lectura, que puede estar desactualizada. ':'')+'Comprueba internet y pulsa Actualizar ahora.';}
  finally{busy=false;$('refresh').disabled=false;}
}
document.querySelectorAll('[data-tab]').forEach(button=>button.addEventListener('click',()=>{document.querySelectorAll('[data-tab]').forEach(b=>b.setAttribute('aria-selected',String(b===button)));document.querySelectorAll('.panel').forEach(p=>p.hidden=p.id!==button.dataset.tab);}));
$('client').addEventListener('change',render);$('refresh').addEventListener('click',refresh);
setInterval(()=>{if($('auto').checked&&!document.hidden)refresh();},30000);
document.addEventListener('visibilitychange',()=>{if(!document.hidden&&$('auto').checked)refresh();});
refresh();
