# Verificación del módulo Subir a la nube

17/11/2026. Exclusivamente datos ficticios.

- Visor: https://adrianogstv.github.io/HidroLog-Demo-Nube/protegido/?cliente=a
- Despliegue GitHub Actions: 44175001793, finalizado correctamente.
- Publicación real cifrada desde PC: resumen inicial 21 m y nueva versión 24 m. Commit final del envío: bb12c04dcd2f128f8b59e90b17105341c2899aad.
- El sobre remoto se descifró correctamente con la clave suministrada por el usuario mediante entrada oculta. No se guardó esa contraseña en archivos, argumentos de comandos, logs o repositorio.
- Página, JavaScript, estilos y módulo criptográfico publicados responden HTTP 200 y sus SHA-256 coinciden con el código local.
- Pruebas automatizadas: cifrado/descifrado, rechazo de otra contraseña y alteraciones, contexto de proyecto, sal/nonce nuevos, cola sin red, recuperación de acuse sin duplicar, dos proyectos y envío de pendientes anteriores antes de la última instantánea.
- Compatibilidad de descifrado Python → Web Crypto comprobada en Node usando el protocolo que se publica en el navegador.
- Botón desacoplado: controles de proyecto abierto, guardado, diálogo y prevención de doble envío comprobados con DOM mínimo.

No se probó visualmente un navegador ni el instalador HidroLog. El botón está disponible como ventana auxiliar y como módulo fuente para que el compañero lo integre. El adaptador Tauri/Rust no fue compilado; esta máquina no tiene el toolchain identificado. No hay pruebas Android ni una nueva APK/versión instalada de HidroLog.

Protección de la prueba: contraseña compartida y cifrado, sin cuentas ni revocación individual. El almacenamiento sigue siendo un repositorio público de datos ficticios cifrados. No usar con datos reales ni afirmar que ofrece aislamiento productivo por cliente.
