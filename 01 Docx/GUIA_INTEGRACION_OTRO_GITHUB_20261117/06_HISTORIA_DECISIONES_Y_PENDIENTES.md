# Contexto, decisiones y aprendizajes

## Objetivo vigente

Añadir a la aplicación desktop que el compañero ya desarrolla una función reutilizable de subida. La web debe mostrar su dashboard original, con marca WPC, actualizar sus datos y conservar sus capacidades. La primera prueba utiliza el GitHub propio del compañero; no se requiere OpenAI Sites.

## Evolución de esta implementación

1. Se evaluó usar nube para recibir datos de escritorio/campo y ver avances. Se eligió una prueba económica con GitHub, no una arquitectura productiva por cliente.
2. La primera prueba usó datos ficticios. Una interfaz auxiliar Tkinter fue rechazada: el botón debía estar dentro de HidroLog. Se integró en una copia Tauri de la app real y se compilaron los componentes necesarios; no se reemplazó el original.
3. La restricción a UUID ficticios impidió subir sondajes creados por el usuario. Se sustituyó por validación de cualquier proyecto .wpcx compatible. No conservar la antigua lista cerrada de sondajes.
4. Se eliminó la solicitud de clave en cada subida. Quedó una sola clave para abrir la web y un almacén seguro en el emisor para cifrar automáticamente.
5. Se pasó de publicar solo resúmenes a una copia íntegra del .wpcx más su resumen, ambos cifrados.
6. El usuario identificó su HTML de seguimiento. Estaba cortado dentro de la geometría 3D. Se recuperó la plantilla completa del Python y las librerías intactas, omitiendo explícitamente las mallas que faltaban, según autorización del usuario.
7. Se conectó el lector ZIP, adaptador y puente del dashboard. Se añadió importación/exportación .wpcx local, sin convertir la web en editor o emisor oculto.
8. Las pruebas reales revelaron una carrera al llegar datos durante el inicio del visor. Se añadió espera de disponibilidad y una cola secuencial, con timeout.
9. El usuario pidió que solo se viera el dashboard a pantalla completa después del acceso. Se retiraron de la vista los bloques redundantes externos, preservando la actualización.
10. Esta entrega parametriza la integración para otra cuenta, documenta sus puntos de unión y adopta la entrada WPC suministrada por el usuario. No incluye sus credenciales ni utiliza su repositorio como destino predeterminado.

## Correcciones explícitas que deben preservarse

- El software ya existe: integrar, no rehacer.
- Botón dentro de la app desktop original; ninguna interfaz Tkinter aparte.
- Proyectos y sondajes propios, no solo ejemplos autorizados por UUID.
- Una sola clave web; ninguna por proyecto o sondaje ni en el botón.
- Dashboard principal y único después de desbloquear, a pantalla completa.
- Conservar el dashboard original y sus importaciones/exportaciones.
- Marca **WPC / Water Project Consultants**, con el logo provisto.
- El compañero usa su GitHub y la LLM de su preferencia; primero conectar y verificar ese acceso.
- Documentación, código y resultados separados; no borrar ni mover versiones anteriores.

## Hechos frente a interpretaciones

Hechos: hubo confirmación real de commits, comparación binaria del archivo remoto, aplicación de 3→6→12 m en el runtime y recuperación ordenada de cola. Se conservó la fuente original de HidroLog, verificada mediante hashes de 109 archivos. La validación de UI fue técnica, no una inspección visual interactiva completa.

Interpretación: este flujo es una base útil para validar el recorrido con el equipo. No demuestra que GitHub sea el almacenamiento adecuado para una operación comercial, varios emisores o todos los clientes.

## Pendientes

Probar la cuenta nueva, integrar los cuatro adaptadores a la app real del compañero, validar su dashboard y fórmulas, incorporar recursos/plan completos cuando existan y hacer QA visual. Diseñar reconexión autónoma y concurrencia si se requieren. Android, identidad por cliente y backend productivo están fuera de lo implementado. No ocultar esos límites en la entrega.
