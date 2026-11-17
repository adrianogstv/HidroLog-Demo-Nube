# Prueba de manejo PC → GitHub → dashboard

17/11/2026. Usar datos ficticios. No modifica el instalador actual ni contrata servicios.

## Dos recorridos

**Publicador solamente:** abrir el publicador con Python, seleccionar uno de los paquetes incluidos, encolar y enviar. Permite comprobar el transporte real sin instalar HidroLog.

**Con HidroLog escritorio:** abrir una COPIA de DEMO_A.wpcx como proyecto independiente en HidroLog PC 2.0.4. Nunca combinarlo con un proyecto de trabajo. Ajustar una recuperación entre cero y la longitud de corrida o crear una corrida continua. Guardar y seleccionar esa copia en el publicador. Solo reconoce los cuatro sondajes ficticios del generador; no cambiar sus identificadores ni añadir sondajes reales.

El generador define coordenadas cero ficticias; no representan ubicaciones. Registros parciales pueden producir avisos de faltantes en HidroLog. Esta prueba se limita a metros logueados y recuperación, no a fórmulas RMR o ensayos de permeabilidad. No atribuir metros logueados a avance de perforación sin acordar ese indicador.

## Ejecutar la herramienta

En la raíz de este repositorio, con Python 3.9+ y Tkinter:

```powershell
python -B "00 Code/herramientas/publicador_pc.py"
```

En esta máquina de desarrollo también se puede usar el Python disponible del proyecto WPC. No hace falta instalar librerías de Python adicionales. La variante de comandos es:

```powershell
python -B "00 Code/herramientas/publicador_pc.py" check "02 Input/DEMO_A.wpcx"
python -B "00 Code/herramientas/publicador_pc.py" enqueue "02 Input/DEMO_A.wpcx"
python -B "00 Code/herramientas/publicador_pc.py" publish "03 Output/Cola_PC/ARCHIVO_PENDIENTE.json"
```

Sustituir ARCHIVO_PENDIENTE por el nombre real que devuelve enqueue. El publicador conserva el pendiente si falla la red o la autorización. Después del éxito guarda el estado confirmado; no elimina archivos. El mismo resumen no produce otro commit. Si se pierde el acuse local, el reintento compara su hash con el resumen remoto.

Antes de enviar, iniciar sesión en Git desde el PC y contar con permiso de escritura en adrianogstv/HidroLog-Demo-Nube. Git Credential Manager entrega la credencial solo al proceso local. Nunca pegar tokens en el HTML ni subirlos a Git. Si no hay sesión, se muestra error y la cola se conserva.

## Alcance del envío

Se publica por cliente ficticio la lista de sondajes, metros logueados, profundidad máxima, recuperación, intervalos numéricos y cantidad de corridas. No se envían nombres del proyecto del paquete, nombres de personas, coordenadas, comentarios, litología, ensayos, fotografías ni el archivo ZIP completo. Las etiquetas visibles son constantes del generador.

El repositorio y el JSON son PÚBLICOS. La lista de IDs reduce cargas accidentales, no es una barrera de seguridad frente a un operador que altere deliberadamente el programa. No usar datos de cliente, ni siquiera para editar un paquete que conserve IDs de demo.

## Qué comprobar

1. Cerrar y reabrir el publicador: conserva la cola pendiente.
2. Activar simulación sin conexión: no intenta enviar.
3. Recuperar conexión y pulsar enviar: acuse y resumen presentes en GitHub.
4. Abrir dashboard en otra computadora: debe leer el mismo resumen. Cachés pueden demorar la lectura.
5. Reenviar el mismo paquete: no duplica corridas ni genera cambios innecesarios.
6. Seleccionar un paquete que no sea demo: debe rechazarse antes de hacer llamadas a GitHub.

Los ensayos automatizados de CLI no sustituyen la revisión visual del instalador. Registrar por separado si se probó realmente HidroLog PC, la interfaz auxiliar y otro equipo. No declarar pruebas Android.

## Siguiente etapa

Integrar outbox transaccional y sincronización en el software de escritorio, primero con backend de prueba y usuarios ficticios. Después probar Android en equipo real. Para datos sensibles: repositorios privados de código, base de datos con permisos y archivos privados; no convertir esta demo pública en el sistema final.
