# Conectar el dashboard del compañero

El HTML incluido es una **referencia integrada**, recuperada del generador Python recibido. No es una orden de reemplazar el dashboard que el compañero esté desarrollando. Si ese HTML ya importa/exporta, conservar esas funciones y conectar el nuevo origen de datos por debajo.

## 1. Encontrar el punto único de actualización

Identificar la función que recibe los datos importados y actualiza filtros, tablas, curvas, perfiles, 3D y selección. Evitar mantener una segunda versión divergente de los cálculos. Si la importación solo existe para Excel, crear un adaptador .wpcx→su contrato o usar su lector real; no reconstruir todo el dashboard con otro diseño.

## 2. Leer y validar el snapshot

`leer_wpcx.mjs` lee el ZIP sin extraer archivos al sistema, admite entradas almacenadas/deflate, limita tamaños y comprueba hashes. `adaptar_hidrolog.mjs` traduce los registros al contrato del dashboard 43. El módulo fuente debe importar el exportador de la aplicación del compañero; la ruta que apunta a la app original es una referencia que debe reemplazarse.

El adaptador usa `armarLibroSondaje` para recuperar K conforme al motor existente, manteniendo unidades m/s. Convierte la inclinación a negativa descendente, REC/RQD a porcentajes y recuperación de agua a fracción. Usa las corridas de los turnos. Los datos incompletos producen avisos: no inventar K, coordenadas, fechas o mallas.

La métrica `drilled` de esta versión se deriva de longitudes registradas por turno; no debe confundirse con avance perforado independiente si la app posee otro campo específico. Acordar esa semántica con el compañero antes de una entrega productiva. Del mismo modo, la longitud mostrada como plan en la referencia procede de los registros disponibles porque faltaba el libro de planificación externo; incorporar su plan real si existe.

## 3. Puente de redibujado

Dentro del cierre original existen `ALL`, `D`, `holeSelect`, `camera` y `controls`. `puente_perfil.js` añade `window.WPC_CLOUD_UPDATE(datos)` y reutiliza el evento de cambio de sondaje, conservando cámara si sigue siendo el mismo. Si el dashboard del compañero tiene otro estado o framework, adaptar ese punto; no asumir que esas variables existen.

El primer snapshot resuelve `WPC_INITIAL_DATA`. Una vez terminada la inicialización y el primer render, emitir:

```js
window.dispatchEvent(new Event('wpc-viewer-ready'));
```

Las actualizaciones tempranas esperan esa señal y se aplican en orden. Probar dos envíos durante el arranque para no reintroducir el fallo encontrado.

## 4. Dependencias y recursos

La referencia incluye Three.js y OrbitControls. Conservar sus avisos de licencia. El HTML entregado inicialmente estaba cortado dentro de una malla base64 y carecía del script final. Se extrajo la plantilla completa desde la constante `HTML` del generador con AST, sin ejecutar sus rutas externas ni modificar las fuentes. Se recuperaron únicamente los scripts íntegros.

Se omitieron explícitamente las mallas de labores, vetas, fallas y topografía. Cuando el compañero tenga recursos completos, validar su geometría/origen/CRS e incorporarlos a la plantilla. No interpretar «sin mallas» como «sin cruces». Mantener avisos hasta disponer de los recursos reales.

## 5. Cifrar y publicar

Colocar su HTML final **ya conectado** en `02 Input/dashboard_base/Dashboard_HidroLog_Conectado.html`, fuera de la carpeta pública. Si usa recursos externos privados, empaquetarlos o implementar su propio cargador cifrado; no dejarlos como URLs públicas inadvertidas. La política del iframe puede requerir ampliar dependencias públicas legítimas, sin dar acceso de red indiscriminado a código importado.

Ejecutar `cifrar_dashboard.py` con la clave propia y publicar únicamente `00 Code/web`. El wrapper conserva la entrada WPC y muestra solo el dashboard a pantalla completa tras desbloquear. No añadir paneles redundantes alrededor.

## 6. Importación/exportación local

La referencia permite importar .wpcx localmente y exportar la copia recibida; no publica por importar. En la web, un envío posterior de nube puede actualizar esa vista. Mantener la importación/exportación propia del compañero si usa formatos distintos. El guardado y la publicación se originan en HidroLog, no en un editor oculto dentro del dashboard.
