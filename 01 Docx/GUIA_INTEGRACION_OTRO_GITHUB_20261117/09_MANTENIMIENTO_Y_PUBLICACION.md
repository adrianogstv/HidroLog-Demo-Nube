# Mantener la integración

## Cambios de datos

Guardar y enviar desde la app. El snapshot cifrado se actualiza en el repo y la web lo consulta. No reconstruir el HTML, recifrar la plantilla o lanzar Pages por cada corrida. La publicación automática al guardar se activa después del primer envío correcto del proyecto en esa sesión.

## Cambios de diseño, fórmulas o geometría

Actualizar el dashboard base con su generador/adaptador, conservar la señal de disponibilidad, validar las pruebas y ejecutar `cifrar_dashboard.py`. Publicar la plantilla cifrada y el código del visor en el workflow. Las fórmulas deben provenir del motor de la app del compañero; documentar cualquier cambio de versión y repetir comparaciones.

## Cambios de repo o cuenta

Actualizar configuración, ejecutar `configurar.py`, configurar una clave nueva bajo un credential_target específico, recifrar la plantilla y recompilar o redistribuir la configuración no secreta del publicador. Comprobar el remoto local y los permisos; volver a publicar snapshots sintéticos. El navegador y el emisor deben apuntar al mismo owner/repo/rama/data_dir. No copiar el archivo de credenciales de otro equipo.

## Cambios de proveedor

El flujo está separado en UI, persistencia, cifrado, transporte y renderer. Sustituir el transporte y el origen de lectura por un backend/almacenamiento privado cuando corresponda, preservando los contratos y la lógica del dashboard. No agregar un token persistente al navegador como atajo. Si se necesitan usuarios por cliente, la capa de identidad y autorización debe ser del servidor.

## Cómo actualizar esta memoria

Actualizar README y estado/contexto, registrar decisión y corrección del usuario, añadir evidencia y pendientes. Conservar versiones históricas, sin borrados. Si una prueba no se ejecutó, indicarlo. Revisar enlaces, rutas, credenciales y pesos antes de compartir otro ZIP.

## Licencias y marca

El logo WPC fue suministrado para esta integración. Conservar sus proporciones y no sustituirlo por una marca inventada. La entrada reproduce la composición azul/columna de acceso de la referencia y adapta a pantalla pequeña; el dashboard conserva su estilo interno. El logo original se presenta en versión monocroma mediante CSS, sin alterar el archivo recibido.

El HTML base contiene Three.js/OrbitControls y sus avisos MIT. Mantener los avisos al redistribuir. No se empaquetan fuentes ni licencias completas del software del compañero: él conserva y revisa las que correspondan a su aplicación.
