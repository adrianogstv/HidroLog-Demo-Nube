# Módulo «Subir a la nube» para HidroLog

17/11/2026. Entrega independiente para el desarrollador del escritorio y del dashboard. No reemplaza el software ni modifica sus fórmulas. Solo admite los proyectos ficticios de esta demostración.

## Qué hace

1. Toma la ruta del proyecto .wpcx ABIERTO Y GUARDADO.
2. Lee y valida su contenido y huella SHA-256.
3. Prepara exclusivamente un resumen de logueo de los sondajes ficticios autorizados. No publica el proyecto entero, textos libres, personas, ubicaciones ni ensayos.
4. Cifra el resumen antes de guardarlo en la cola o enviarlo a GitHub.
5. Sube al repositorio usando la sesión Git del PC. El navegador del visitante no recibe esa credencial.
6. El visor compartido pide la contraseña y descifra dentro del navegador. Consulta actualizaciones cada 30 segundos mientras está abierto y visible.

Dirección de prueba del proyecto A: https://adrianogstv.github.io/HidroLog-Demo-Nube/protegido/?cliente=a

El botón publica MANUALMENTE. No hay sincronización automática dentro de HidroLog ni garantía de latencia: GitHub puede introducir caché. Los cambios del resumen no requieren volver a desplegar el visor.

## Prueba inmediata sin recompilar HidroLog

En esta máquina se entrega un acceso local bajo 03 Output/ABRIR_MODULO_NUBE_PC.cmd. Abre la ventana auxiliar con el botón exacto «Subir a la nube».

1. Haz una COPIA de 02 Input/DEMO_A.wpcx en una carpeta exclusiva de pruebas.
2. Abre esa copia con «Abrir proyecto» en HidroLog PC 2.0.4. No la importes en un proyecto real.
3. Modifica una recuperación o añade una corrida contigua dentro de un sondaje ficticio existente. Guarda.
4. En el módulo auxiliar, selecciona ese archivo guardado. Escribe la contraseña compartida y repítela.
5. Pulsa Subir a la nube. Comparte el enlace del visor y la contraseña por canales distintos.
6. La otra persona abre el visor, escribe la contraseña y deja marcada la consulta automática. Solo verá cambios que hayas guardado Y publicado.
7. Para ensayar una caída, activa la simulación de falta de conexión. Se conserva el sobre cifrado en la cola; desactiva la simulación y pulsa Reintentar pendientes. No se guarda la contraseña en la cola.

No se solicita instalar otra versión de HidroLog. Esta ventana auxiliar permite probar el transporte mientras el compañero integra el botón real en su rama.

## Componentes y contratos

| Componente | Responsabilidad |
|---|---|
| 00 Code/modulo_nube/hidrolog_nube.mjs | Botón y diálogo, desacoplados del estado de HidroLog |
| 00 Code/modulo_nube/hidrolog_nube.css | Apariencia WPC del botón y diálogo |
| 00 Code/modulo_nube/tauri_bridge.rs | Comando nativo Tauri para comunicar con Python por stdin |
| 00 Code/modulo_nube/cloud_core.py | Cifrado, cola, acuses y envío |
| 00 Code/modulo_nube/subir_nube.py | Ventana auxiliar y modo bridge JSON |
| 00 Code/herramientas/publicador_pc.py | Lector/proyección numérica, con lista de sondajes ficticios |
| 00 Code/herramientas/github_api.py | Transporte con credencial Git obtenida solo en memoria |
| 00 Code/visor/protegido | Visor web de ejemplo con contraseña y consulta automática |

El compañero puede usar su propio dashboard implementando el protocolo documentado abajo. No está obligado a reemplazarlo por nuestro ejemplo. Los resultados que quiera mostrar deben añadirse a un contrato de resumen revisado; no enviar DBRef completo sin seleccionar campos.

## Integración del botón en Tauri 2

### A. Interfaz: dos callbacks y un lugar para el botón

Copia los archivos .mjs y .css a una subcarpeta propia de la interfaz y carga la hoja de estilo. En el módulo que ya tiene acceso a estadoProyecto e invoke:

```javascript
import {crearModuloNube} from './nube/hidrolog_nube.mjs';

const nube = crearModuloNube({
  obtenerEstado: () => estadoProyecto(),
  invocar: (comando, argumentos) => window.__TAURI__.core.invoke(comando, argumentos),
  informar: (texto, tipo) => { /* conectar al indicador de estado existente */ }
});

// Ejecutar después de construir la barra en cada render de la aplicación:
document.querySelector('.toolstrip').append(nube.elemento);
nube.actualizar();
```

El callback devuelve al menos {abierto, ruta, sinGuardar}. El módulo bloquea la publicación si falta proyecto o hay cambios sin guardar. No guarda silenciosamente ni cambia de proyecto. Reutiliza la misma instancia del módulo al reconstruir la barra; no instanciar un observador o un botón nuevo en cada render.

### B. Comando nativo

Copia tauri_bridge.rs como archivo nuevo de src-tauri/src. Añade, SIN reemplazar otros comandos:

```rust
mod tauri_bridge;
// Dentro del generate_handler! existente, agregar:
tauri_bridge::nube_subir_proyecto,
```

El puente usa serde_json y Tauri, ya presentes en este proyecto. Ejecuta el trabajo bloqueante fuera del hilo de interfaz. No utiliza cmd /c, no pasa la contraseña por argumentos, no registra solicitudes ni stderr.

### C. Entorno del publicador

Python 3.12 fue el entorno probado, con cryptography 50.0.1. Instalar las dependencias del kit en un entorno propio; no cambiar a ciegas el entorno productivo del compañero:

```powershell
python -m pip install -r "00 Code/modulo_nube/requirements.txt"
```

Conservar la estructura de 00 Code/modulo_nube y 00 Code/herramientas, porque el módulo reutiliza el lector y el transporte. Copiar 02 Input/config_nube.example.json como config_nube.json en una carpeta de configuración propia y completar SOLO las rutas absolutas de python.exe y subir_nube.py. No introducir contraseña ni token en ese archivo.

En tauri.conf.json, agregar el recurso sin sobrescribir los existentes:

```json
{
  "bundle": {
    "resources": {
      "RUTA_RELATIVA_A_TU_CONFIG/config_nube.json": "nube/config_nube.json"
    }
  }
}
```

El ejemplo es un FRAGMENTO para combinar con la configuración actual. El Python y el kit deben seguir disponibles en las rutas configuradas. Para distribuir un instalador autónomo habrá que empaquetar un sidecar o portar el transporte a Rust y volver a probar; este kit no promete funcionar en un PC sin sus requisitos.

### D. Contrato del comando

Entrada Tauri: nube_subir_proyecto({ruta, password}). Por el proceso auxiliar se transmite {path, password} en stdin. Resultado de éxito: {ok:true, confirmed:true, viewer_url, operation_id, commit}. Un fallo de red después de preparar el sobre devuelve {ok:false, queued:true, message}; no marcar como subido ni descartar datos.

Para otra arquitectura, el transporte se inyecta a través de invocar. Es posible reemplazar el puente de GitHub por una API privada manteniendo la interfaz del botón y el esquema de acuse.

## Protocolo del visor

- Un archivo por proyecto ficticio en 02 Input/protegido/a.json o b.json. Es el último sobre CIFRADO, no un dataset legible.
- Sobre: format=hidrolog-demo-encrypted, version=1, client, operation_id, iterations, salt, iv y ciphertext.
- Clave: PBKDF2-HMAC-SHA256, 600.000 iteraciones, sal aleatoria de 16 bytes y clave derivada de 32 bytes.
- Cifrado: AES-256-GCM, nonce aleatorio de 12 bytes y etiqueta de 128 bits incluida al final del ciphertext.
- AAD UTF-8 exacto: hidrolog-nube-v1:CLIENT:OPERATION_ID.
- Payload descifrado: {version:1, synthetic_only:true, published_at, project:resumen}.
- El ejemplo reutilizable del navegador está en protocol.mjs. El visor conserva únicamente material criptográfico en memoria mientras está desbloqueado; no guarda la contraseña en localStorage ni la incorpora a la URL.
- En cada nueva operación se deriva la clave con la nueva sal usando ese material de sesión. Si la contraseña cambió, el visor bloquea los datos y pide la nueva. Una caída de red conserva la última lectura indicando que puede estar desactualizada.

## Alcance de privacidad de esta prueba

El repositorio y la dirección del visor siguen siendo públicos. El contenido de esta ruta está cifrado, pero cualquiera puede descargar el ciphertext e intentar adivinar la contraseña. La clave solicitada por el usuario se utiliza solo para esta prueba; no se escribe aquí.

Es una clave compartida por proyecto: no hay usuarios individuales ni revocación por persona. Cambiarla protege NUEVOS envíos, pero el historial de Git conserva versiones antiguas y quien conoció su clave puede seguir leyéndolas. No es una solución de retirada retroactiva de acceso. Tampoco borra copias descargadas.

La demo anterior con resumen sin contraseña se conserva y contiene únicamente sus datos ficticios. La nueva protección no convierte ese historial público en privado. Para información real hace falta el circuito aprobado de cuentas, API, permisos por cliente y almacenamiento privado.

No se eliminan colas, acuses, archivos originales o históricos. Un único PC publicador es el alcance de este prototipo; no resuelve ediciones concurrentes ni conflictos entre varios escritores.

## Qué se valida y qué falta

Pruebas de cifrado Python/Web Crypto, contraseña incorrecta, alteración, cola sin red, idempotencia y proyectos separados. Prueba real de envío por API de GitHub y lectura del sobre publicado. Ver acta de verificación.

El adaptador Rust se entrega como código de integración: no fue compilado en esta máquina porque no se encontró el toolchain Rust. No se modificó ni recompiló HidroLog. Las pruebas automatizadas del botón no sustituyen la prueba interactiva dentro de la versión del compañero. No hay pruebas Android.

Referencias: https://v2.tauri.app/develop/calling-rust/ y https://cryptography.io/en/latest/hazmat/primitives/aead/ .
