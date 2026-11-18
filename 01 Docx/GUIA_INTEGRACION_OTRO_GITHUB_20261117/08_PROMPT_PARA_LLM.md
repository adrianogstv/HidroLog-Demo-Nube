# Prompt para copiar a Claude, Codex u otra LLM

Puedes pegar el siguiente texto y adjuntar la carpeta o permitir a la LLM leerla localmente. Cambia solo los campos entre corchetes. No pegues contraseñas o tokens.

---

Necesito incorporar a **mi aplicación desktop existente** un módulo de publicación y conectar **mi dashboard original**. Estoy entregando el paquete «Integración WPC · HidroLog → nube → dashboard». Lee primero README.md, AGENTS.md y 01 Docx/00_LEER_PRIMERO.md, y sigue la guía 01 en orden.

Mis rutas son:
- Aplicación: [RUTA APP]
- Dashboard original: [RUTA HTML O GENERADOR]
- Carpeta del kit: [RUTA KIT]
- Repositorio que quiero utilizar: [URL MI GITHUB]

**Primero ayúdame a conectar mi GitHub a esta LLM o a su entorno local.** No asumas que leer un repo público demuestra permisos para escribir. Comprueba la identidad, el repo y las capacidades disponibles. Si hace falta OAuth, yo lo completaré en el proveedor; no me pidas tokens en el chat. Si el conector no escribe, utiliza Git/gh local autenticado, con el repositorio correcto.

Después verifica por separado que el publicador del PC pueda utilizar las credenciales de Git. Usa mi cuenta y mi repositorio, nunca los históricos de la demostración. Prepara la configuración no secreta y ejecuta primero las pruebas locales del kit; no publiques datos reales para probar.

Trabaja en una copia o rama. No rehagas mi aplicación, no cambies fórmulas ni elimines pantallas. Añade el botón **Subir a la nube** a la interfaz real y adapta obtenerEstado, guardar, invocar y el evento posterior al guardado. La subida debe esperar al archivo guardado y ejecutarse fuera del hilo de UI. No quiero otra ventana Tkinter.

Usa una sola clave para abrir la web. La elegiré en una ventana o entrada local oculta y se almacenará de forma segura en el PC; no va en el código ni se pide al pulsar Subir. Cifra proyecto completo y plantilla antes de publicarlos. No uses tokens en frontend. Mantén el protocolo documentado o migra con una versión explícita y pruebas.

Integra los datos en mi dashboard conservando su formato e importación/exportación. Busca su función real de actualización y crea el adaptador; no asumas que cualquier HTML se conecta sin más. Conserva las unidades y usa mis motores existentes para ensayos. Marca datos incompletos sin inventar resultados, coordenadas o mallas.

Publica en GitHub Pages mediante el workflow de mi repo. La entrada debe ser WPC, con el logo que incluí. Después de la clave solo debe verse el dashboard a pantalla completa. Los cambios guardados y enviados desde la app deben actualizarse al consultar el snapshot, sin desplegar de nuevo el sitio por cada registro.

Verifica con un proyecto sintético 3→6→12 m, compara el archivo remoto por SHA-256, prueba desconexión/reintento, acuse perdido, clave incorrecta y actualización durante el arranque. Si puedes controlar un navegador, revisa visualmente y toma capturas reales. Si no puedes, diferencia las pruebas técnicas del QA visual pendiente.

Documenta cambios, configuración, pasos reproducibles, evidencia y pendientes. No borres ni muevas archivos, no modifiques versiones ajenas ni el segundo cerebro global. Usa 00 Code, 01 Docx, 02 Input y 03 Output. No publiques mi HTML o archivos de cliente en claro ni credenciales. Antes de terminar, dame el enlace, la guía y el estado exacto de verificación.

---
