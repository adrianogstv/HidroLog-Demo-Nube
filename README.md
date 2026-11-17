# HidroLog · Prueba de escritorio y GitHub

Demo PÚBLICA, con datos ficticios generados desde cero. No incluye datos, instaladores, fórmulas ni documentos de clientes. No es una versión productiva de HidroLog.

Web: https://adrianogstv.github.io/HidroLog-Demo-Nube/

## Probar desde el PC

1. Descarga o clona este repositorio. Se requiere Python 3.9+ para el publicador.
2. Copia 02 Input/DEMO_A.wpcx a una carpeta de pruebas. En HidroLog PC 2.0.4 utiliza Abrir proyecto sobre esa copia; NO importar en un proyecto real.
3. Modifica una recuperación dentro de su longitud o agrega una corrida contigua; guarda el proyecto. Las capturas ficticias son parciales y no validan fórmulas.
4. Ejecuta `python -B "00 Code/herramientas/publicador_pc.py"`.
5. Selecciona el archivo guardado. Pulsa «Validar y guardar en cola».
6. Prueba «Simular sin internet» y «Enviar pendientes». Se conservará la cola. Desactiva la simulación y envía otra vez.
7. Cuando GitHub confirme, revisa el dashboard desde otro navegador/equipo. Lee el resumen cada 30 s, sujeto a caché y disponibilidad.

El publicador necesita Git instalado y una sesión de Git Credential Manager con permiso de escritura en ESTE repositorio. No se comparten tokens con visitantes. El dueño puede probar el envío sin conceder permisos de repositorio a los clientes.

Guía completa: [01 Docx/PRUEBA_PC.md](01%20Docx/PRUEBA_PC.md).

## Estructura

- 00 Code/visor: web estática y pública.
- 00 Code/herramientas: generador y publicador auxiliar de PC.
- 00 Code/pruebas: comprobaciones de formato y envío.
- 01 Docx: instrucciones y límites.
- 02 Input: dos paquetes .wpcx sintéticos y resumen público.
- 03 Output: cola, verificaciones y salidas locales; excluida de Git.

GitHub Pages publica el visor. El publicador actualiza 02 Input/estado_demo.json mediante la API de GitHub; el visor lo lee desde raw.githubusercontent.com. Cambiar ese resumen NO dispara un nuevo despliegue de Pages. La lectura cada 30 s no garantiza recepción inmediata.

## Límites intencionales

- NO hay login, protección por cliente ni sincronización Android. Las vistas A/B son filtros de una demo pública.
- NO se publica el .wpcx seleccionado: solo números de logueo y etiquetas fijas de sondajes permitidos.
- NO se ha integrado una sincronización automática en HidroLog. El envío es manual desde una herramienta separada.
- Probar con un único PC publicador; no resuelve conflictos de varios escritores ni reemplaza una base de datos.
- Los pendientes y confirmaciones permanecen en disco. No hay borrado automático.
- Para producción se requiere API, base central, autenticación y autorización por proyecto. No ampliar este repositorio con datos reales.
