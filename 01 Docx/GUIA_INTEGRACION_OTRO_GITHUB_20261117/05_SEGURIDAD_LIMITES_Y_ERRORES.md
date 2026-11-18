# Seguridad, límites y diagnóstico

## Qué protege esta prueba

El servidor distribuye ciphertext. La clave común se deriva y utiliza en el navegador, no se envía como contraseña de un formulario a GitHub. Los tokens de escritura permanecen en el PC emisor. La clave web se guarda en el almacén de Windows, bajo un nombre diferente por repo. No se entrega ninguna clave en este kit.

La clave única **no crea cuentas ni permisos por cliente**. Todas las personas que la conocen tienen el mismo alcance. El repo público revela UUID, tamaños y commits. El historial conserva versiones cifradas: cambiar la clave no vuelve inaccesibles copias que otra persona ya conservó con la clave anterior. Para datos productivos sensibles, evaluar identidad, permisos por cliente, auditoría y almacenamiento privado antes de asumir que esta prueba cumple esos requisitos.

## Límites de implementación

- Solo se admiten .wpcx compatibles, no archivos arbitrarios. Límite actual: 10 MB por archivo, 50 MB por entrada descomprimida y 100 MB total descomprimido en el emisor.
- Publicar una copia completa por guardado aumenta tráfico e historia de Git. No es almacenamiento ilimitado ni sincronización de deltas.
- La consulta web es cada 30 s con la pestaña visible y puede sufrir caché. La consulta de listado de proyectos tiene límites de API; compartir enlaces con UUID evita depender del listado para abrir el proyecto.
- Un emisor por proyecto es el alcance probado. Hay protección mediante SHA remoto/reintentos, pero no se ha validado edición simultánea distribuida o conciliación entre varios equipos.
- La clave del PC no se guarda por proyecto. Requiere inicialización local única en cada emisor y acceso Git utilizable en ese equipo.
- Al cerrar/reabrir la app no se conserva la activación de publicación de la sesión. El primer clic vuelve a ser explícito. La recuperación de pendientes ocurre con un nuevo envío; no existe todavía un servicio autónomo de reconexión.
- Android no está integrado. Debe conservar datos locales y adaptar transporte/almacén seguro más adelante, sin copiar la dependencia de Windows Credential Manager.

## Límites y condiciones de GitHub

GitHub documenta 1 GB como tamaño máximo del sitio publicado, 1 GB recomendado para el repo fuente de Pages y 100 GB/mes como límite flexible de transferencia. Hay otras condiciones de uso: Pages no está planteado como alojamiento gratuito de un SaaS comercial ni para transacciones sensibles. Esta implementación debe mantenerse como prueba y revisarse antes de ofrecer un servicio productivo. [Límites oficiales de Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits).

La API Contents cambia el tratamiento de archivos grandes: por encima de 1 MB puede devolver metadatos sin contenido base64. El emisor usa el SHA para actualizar; los casos grandes requieren revisar la recuperación idempotente y el rendimiento con su archivo real. No se hicieron pruebas cercanas al límite de 10 MB. [API Contents y permisos](https://docs.github.com/en/rest/repos/contents?apiVersion=2026-03-10).

## Errores habituales

| Síntoma | Revisar antes de cambiar código |
|---|---|
| La LLM lee pero no puede escribir | Permisos del conector, repo seleccionado y si dispone de herramienta de escritura |
| GitHub 401/403 | Identidad Git del PC, acceso Contents write, políticas de organización y límites; no pegar tokens en logs |
| No se puede crear el workflow | Permiso de Workflows y origen Pages configurado para Actions |
| La web da 404 | Nombre de repo, rama, URL base, deploy success y ruta /protegido/ |
| La plantilla no abre con la clave nueva | Cifrar plantilla y snapshots con la misma clave, usando la misma configuración/credential_target |
| El proyecto aparece en el enlace equivocado | UUID de manifest y configuración owner/repo/viewer_url; no deducir identidad por nombre de archivo |
| No cambia el gráfico al guardar | Primer clic de activación, evento wpc-estado, guardado real, checkbox, pestaña visible y caché |
| No sale un sondaje en 3D | Collar incompleto o CRS incompatible; no colocar coordenadas cero para ocultar el problema |
| No aparecen cruces o terreno | Mallas omitidas de la referencia; incorporar originales completos y comprobar origen/CRS |
| Error cargando _ctypes en el exe | Al compilar con Python de Conda, incluir ffi.dll si corresponde; la herramienta de build lo contempla |
| El programa termina con exit 0 pero no sube | Leer el JSON ok/confirmed/queued; nunca interpretar solo el exit code |
| Repo privado con web pública no lee datos | El raw privado requiere autenticación; sustituir el almacenamiento por un backend autorizado, no incrustar un token |

## Si se cambia la clave

Elegirla en el almacén local, volver a cifrar la plantilla y publicar snapshots nuevos con la nueva clave. Coordinar el cambio en todos los emisores. Las versiones anteriores se conservan; no prometer retirada retroactiva. No ejecutar borrados de historia ni limpiezas automáticas como parte de este paquete.
