# Antes de empezar

Este paquete resuelve una parte concreta: **guardar un proyecto en la app → pulsar Subir a la nube → publicar la copia cifrada → que el dashboard original lea sus actualizaciones**. El compañero conservará su aplicación, sus archivos y su dashboard. Usará su propia cuenta y repo, con una clave nueva elegida localmente.

## Orden de trabajo y lectura

1. **Conectar el GitHub propio a la LLM** y comprobar qué permisos tiene. Guía 01, fase A.
2. Autenticar Git en el PC emisor y preparar un repo de prueba. Guía 01, fase B.
3. Configurar el kit y probar el emisor sin tocar la app. Guía 01, fases C–D.
4. Incorporar el botón y el comando nativo a su app existente. `00 Code/integracion/ENLACES_APP.md` y guía 02.
5. Conectar su dashboard mediante el contrato, conservando sus vistas. Guía 03.
6. Publicar la web cifrada y comprobar el flujo real. Guía 01, fase F, y guía 04.
7. Consultar errores y mantenimiento. Guías 05 y 09.

Puede entregar la carpeta completa a Claude, Codex u otra LLM y pegar el prompt de la guía 08. El acceso de una LLM a GitHub depende de su producto y sus herramientas; el conector no es indispensable si la LLM puede trabajar con un repositorio local autenticado mediante Git.

## Qué está terminado y qué no

La prueba original usa HidroLog PC 2.0.6, Tauri 2, un publicador empaquetado y GitHub Pages. El archivo .wpcx completo se cifra, junto con un resumen. La plantilla del dashboard se cifra por separado y se carga una vez. Cada proyecto tiene un UUID estable y una ruta propia; los sondajes no tienen contraseñas individuales.

El dashboard base recuperado funciona sin sus mallas incompletas: no incluye labores, vetas, fallas o terreno. No inventar esas geometrías ni interpretar la falta de cruces como ausencia de impacto. El compañero debe usar sus recursos completos si los tiene y repetir QA.

El código del emisor de este kit ya usa configuración, sin el propietario o la clave anteriores. El puente de UI y Rust son puntos de unión: hay que comprobar los nombres del estado/guardado en la aplicación que el compañero esté desarrollando. No es una aplicación nueva lista para instalar ni una migración automática de cualquier HTML.
