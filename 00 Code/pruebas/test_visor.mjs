// Prueba de comportamiento del visor con DOM mínimo; no sustituye QA visual.
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
class Element{
  constructor(){this.textContent='';this.style={};this.children=[];this.events={};this.disabled=false;this.hidden=false;this.checked=false;this.value='';this.attrs={};this.classes=new Set();this.classList={add:x=>this.classes.add(x),remove:x=>this.classes.delete(x)};}
  append(...nodes){this.children.push(...nodes);}
  replaceChildren(...nodes){this.children=[...nodes];}
  addEventListener(name,cb){this.events[name]=cb;}
  setAttribute(name,value){this.attrs[name]=value;}
}
const html=fs.readFileSync(path.join(root,'00 Code/visor/index.html'),'utf8');
const elements=Object.fromEntries([...html.matchAll(/id="([^"]+)"/g)].map(x=>[x[1],new Element()]));
assert.equal(Object.keys(elements).length,[...html.matchAll(/id="([^"]+)"/g)].length,'IDs duplicados');
elements.client.value='all';elements.auto.checked=true;
const tabs=['dashboard','guide','architecture'].map(id=>{const e=new Element();e.dataset={tab:id};return e;});
const panels=['dashboard','guide','architecture'].map(id=>Object.assign(elements[id],{id}));
const state=JSON.parse(fs.readFileSync(path.join(root,'02 Input/estado_demo.json'),'utf8'));
let fail=false,interval;
const context=vm.createContext({document:{hidden:false,getElementById:id=>{assert.ok(elements[id],id);return elements[id];},createElement:()=>new Element(),querySelectorAll:s=>s==='[data-tab]'?tabs:panels,addEventListener:()=>{}},
  fetch:async()=>{if(fail)throw Error('sin red');return {ok:true,json:async()=>structuredClone(state)};},AbortSignal,Date,Number,Math,Error,setInterval:cb=>{interval=cb;}});
vm.runInContext(fs.readFileSync(path.join(root,'00 Code/visor/app.js'),'utf8'),context);
await new Promise(resolve=>setImmediate(resolve));
const expected=state.projects.flatMap(p=>p.holes).reduce((s,h)=>s+h.logged_m,0);
assert.ok(elements.meters.textContent.includes(String(expected)),elements.meters.textContent);
assert.equal(elements.rows.children.length,4);
elements.client.value='a';elements.client.events.change();assert.equal(elements.rows.children.length,2);
tabs[1].events.click();assert.equal(elements.guide.hidden,false);assert.equal(elements.dashboard.hidden,true);
const previous=elements.meters.textContent;fail=true;await vm.runInContext('refresh()',context);
assert.equal(elements.meters.textContent,previous);assert.ok(elements.status.classes.has('error'));assert.equal(elements.refresh.disabled,false);
assert.ok(elements.status.textContent.includes('última lectura'));
assert.equal(typeof interval,'function');
console.log('OK: lectura inicial, métricas, filtro, pestañas y conservación ante caída de red. Sin prueba visual.');
