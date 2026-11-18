# Pruebas que debe repetir el compañero

## Niveles de evidencia

No son equivalentes: (a) sintaxis/importación; (b) pruebas locales con transporte simulado; (c) publicación real confirmada y descargada; (d) redibujado del runtime; (e) clic físico y QA visual en navegador. Registrar el nivel alcanzado, los archivos usados y el commit. No declarar (e) por haber pasado (a–d).

## Prueba local del kit

`python "00 Code/pruebas/probar_kit.py"` crea únicamente entradas sintéticas y salidas en `03 Output`. Usa una configuración temporal de otra cuenta ficticia, no las credenciales del usuario. Comprueba parametrización, cifrado/descifrado, rechazo de clave incorrecta, cola, reintentos, acuses y URL de retorno. No publica en ningún GitHub.

## Prueba real en el GitHub propio

1. Crear un proyecto ficticio con un UUID nuevo, un sondaje con collar completo y un turno/corrida de 0 a 3 m. Guardarlo en la aplicación anfitriona.
2. Pulsar Subir a la nube. Verificar confirmación remota, enlace y nombre del repo. Abrir el enlace con UUID y la clave única.
3. Comprobar 3 m, turno, perfil y posición. Añadir o modificar registros para alcanzar 6 y luego 12 m. Guardar con Actualizar al guardar activo. Verificar las versiones nuevas sin importar manualmente ni desplegar de nuevo la web.
4. Descargar la copia del proyecto y compararla byte a byte y por SHA-256 con el archivo enviado. Incluir un adjunto sintético.
5. Simular fallo del transporte en la prueba, sin desconectar servicios ajenos. Confirmar un archivo cifrado pendiente y ausencia de acuse. Recuperar con un nuevo envío; el último estado debe prevalecer. No afirmar recuperación espontánea de internet si no se implementó.
6. Repetir una operación confirmada y comprobar que no crea otra escritura. Para simular acuse perdido, copiar el sobre a una nueva carpeta sin acuse, sin borrar el original. Recuperar desde remoto sin repetir PUT.
7. Abrir el visor y enviar cambios mientras aún está arrancando. Debe esperar a la señal de disponibilidad y aplicar versiones en orden.
8. Probar contraseña errónea, ZIP truncado y SHA-256 alterado. Rechazar sin aplicar datos parciales.
9. Crear otro proyecto/sondaje. Verificar rutas UUID separadas, misma clave web y que abrir un proyecto distinto no lo publique silenciosamente. El primer envío de ese proyecto es explícito.
10. Probar dos sondajes, otro turno, un ensayo válido, uno incompleto y un collar incompleto. No inventar K o coordenadas. Los incompletos permanecen en el archivo aunque el 3D no pueda mostrarlos.

## QA visual que sí requiere navegador

Ver entrada WPC en escritorio y móvil; URL con UUID debe pedir solo clave. Tras desbloquear, solo el dashboard, sin paneles redundantes ni scroll externo. Revisar selección de sondaje/turno, controles 3D, leyendas, perfiles, importación/exportación y avisos de recursos omitidos. Probar cámara tras actualización, recarga, bloqueo/cierre y desconexión.

La prueba original validó las fases técnicas con 3→6→12 m, cola de 9 m recuperada antes del último envío, cuatro acuses e integridad exacta. No se dispuso de control visual del navegador: el clic físico y la apariencia no se certificaron. El compañero debe completar ese último nivel en su equipo.
