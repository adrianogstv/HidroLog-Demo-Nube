# Estado de la prueba

17/11/2026. Web: https://adrianogstv.github.io/HidroLog-Demo-Nube/

Repositorio: https://github.com/adrianogstv/HidroLog-Demo-Nube

## Comprobado

- GitHub Actions publicó la web correctamente. Ejecución 44168746633.
- Resumen ficticio enviado realmente desde el PC por API de GitHub; commit d337612fcc87cb42bff9ceba5991588bcb87222c.
- Cliente ficticio A: 21 → 24 m logueados. Cliente ficticio B: conserva 21 m. Repetir el envío confirmado no lo duplica.
- La web, JavaScript, estilos y dos paquetes .wpcx publicados responden HTTP 200 y coinciden por SHA-256 con sus fuentes locales.
- El resumen remoto es legible desde el origen del dashboard y devuelve CORS compatible.
- Ocho pruebas automatizadas del publicador: formato, rechazo de proyecto ajeno, integridad, caída de red, reintento sin duplicados, conflicto de escritura, actualización y conservación de ambos clientes.
- Prueba del JavaScript con DOM mínimo: métricas, filtros, pestañas y conservación de última lectura ante error. No es una prueba visual de navegador.

## Pendiente de prueba interactiva

- Abrir el .wpcx en el instalador HidroLog PC 2.0.4, editar y guardar desde la interfaz real.
- Usar los botones del publicador de escritorio y revisar visualmente la web en distintos tamaños.
- Abrir en otro equipo físico. Se verificó acceso remoto por HTTP, no una segunda computadora manejada por una persona.
- Android no fue probado ni modificado. No se compiló un APK nuevo.

## Límites

Demo pública, sin autenticación ni aislamiento de cliente. Solo datos ficticios. No se ha integrado sincronización automática dentro de HidroLog. No se cargaron datos de cliente ni se contrataron servicios. Los cambios del resumen no disparan un nuevo despliegue y pueden tardar por caché del servicio.

Evidencia detallada y colas bajo 03 Output, excluidas de Git. Código de pruebas bajo 00 Code/pruebas. Instaladores y proyecto original sin cambios.
