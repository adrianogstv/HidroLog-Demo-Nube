import assert from 'node:assert/strict';
import {crearModuloNube} from '../modulo_nube/hidrolog_nube.mjs';
class Element{
  constructor(tag){this.tag=tag;this.children=[];this.events={};this.value='';this.disabled=false;this.attrs={};}
  append(...nodes){this.children.push(...nodes);}
  setAttribute(k,v){this.attrs[k]=v;}
  addEventListener(k,v){this.events[k]=v;}
  remove(){}close(){}showModal(){}focus(){}
}
globalThis.document={createElement:tag=>new Element(tag),body:new Element('body')};
let state={abierto:false,ruta:'',sinGuardar:false},calls=0,release;
const messages=[];
const module=crearModuloNube({obtenerEstado:()=>state,invocar:async()=>{calls++;return await new Promise(resolve=>{release=resolve;});},informar:(text)=>messages.push(text)});
const button=module.elemento.children[0];assert.ok(button.textContent.includes('Subir a la nube'));
button.events.click();assert.equal(calls,0);assert.ok(messages.at(-1).includes('Abre un proyecto'));
state={abierto:true,ruta:'DEMO_A.wpcx',sinGuardar:true};button.events.click();assert.equal(calls,0);assert.ok(messages.at(-1).includes('Guarda el proyecto'));
const first=module.subir('DEMO_A.wpcx','ficticia-para-test');assert.equal(button.disabled,true);
const second=await module.subir('DEMO_A.wpcx','ficticia-para-test');assert.equal(second,null);assert.equal(calls,1);
release({ok:true,viewer_url:'https://example.test/demo'});await first;assert.equal(button.disabled,false);
state.sinGuardar=false;button.events.click();assert.equal(document.body.children.length,1);
console.log('OK: botón, bloqueo sin proyecto/sin guardar, envío único y diálogo independiente. No es prueba visual ni Tauri compilado.');
