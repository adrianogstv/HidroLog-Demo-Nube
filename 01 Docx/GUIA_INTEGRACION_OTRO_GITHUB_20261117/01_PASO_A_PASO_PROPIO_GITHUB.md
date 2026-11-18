# Paso a paso con GitHub propio

Ejecutar desde la raíz del kit. El ejemplo usa Windows, Python 3.12+, Node y Git. Instalar GitHub CLI (`gh`) es una opción práctica, no un requisito del protocolo.

## A. Primero: conectar la cuenta a la LLM

1. Elegir la LLM con la que se trabajará y abrir su área de conectores, herramientas o integraciones. El nombre y disponibilidad varían entre productos; no hay un botón universal.
2. Si ofrece GitHub, autorizar **la cuenta del compañero** y seleccionar solo el repositorio previsto. Completar OAuth en la ventana del proveedor; nunca pegar tokens en el chat.
3. Entregar este kit a la LLM y pedirle que indique la identidad/repositorio accesibles y si puede leer y escribir. La lectura de un repo público no demuestra acceso de escritura. Pedir una edición de documentación en una rama propia o PR cuando el conector lo permita.
4. Si el conector solo lee o no existe, clonar el repo en el PC y usar una LLM con acceso local al código. No bloquear todo el trabajo por la ausencia del conector: Git/gh puede realizar las operaciones autorizadas.
5. Confirmar el destino `SU_USUARIO/SU_REPOSITORIO` antes de la primera publicación. No usar enlaces de la demostración de otra cuenta.

**Dos autenticaciones diferentes:** la conexión de la LLM sirve para colaborar sobre el código; el publicador que corre dentro de HidroLog necesita credenciales locales utilizables por Git. Una no garantiza la otra.

## B. Preparar el repo y la autenticación local

Para esta prueba, usar un repositorio dedicado público con contenido cifrado y sin datos de cliente en claro. La web lee los snapshots públicos cifrados. Un repo privado requiere otro mecanismo de acceso al almacenamiento; no poner su token en el navegador para resolverlo.

```powershell
gh auth login --hostname github.com --git-protocol https --web
gh auth setup-git
gh api user --jq .login
```

También puede utilizar Git Credential Manager de Git for Windows. El emisor usa `git credential fill` por debajo, captura la credencial en memoria y no la imprime. **No ejecutar ese comando manualmente en un terminal visible ni enviar su salida a la LLM.**

Si el repositorio aún no existe y el compañero autoriza crearlo, puede usar:

```powershell
gh repo create SU_USUARIO/SU_REPOSITORIO --public --clone
```

Si ya existe, usar en su lugar:

```powershell
gh repo clone SU_USUARIO/SU_REPOSITORIO
```

Copiar el contenido del kit a la raíz de esa copia local, conservando cualquier archivo previo y sin sustituir su carpeta `.git`. Si el repo ya tiene contenido propio, revisar la incorporación en una rama y adaptar rutas en vez de sobrescribirlo. Ejecutar los comandos siguientes desde esa raíz. Comprobar que el remoto corresponde al destino elegido y nunca usar URLs con tokens incrustados.

 Trabajar en una copia local y conservar su aplicación por separado. Si usa una organización, configurar `owner` con la organización y `github_username` con el usuario autenticado.

## C. Configurar el kit

Crear un entorno Python propio y no alterar los motores de la aplicación:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r "00 Code/emisor/requirements.txt"
```

Editar **solo parámetros no secretos** en `02 Input/configuracion_nube.json`:

```json
{
  "owner": "SU_USUARIO",
  "repo": "SU_REPOSITORIO",
  "branch": "main",
  "github_username": "SU_USUARIO",
  "viewer_url": "https://SU_USUARIO.github.io/SU_REPOSITORIO/protegido/",
  "data_dir": "02 Input/protegido",
  "credential_target": "WPC/HidroLog/Nube/SU_REPOSITORIO"
}
```

`viewer_url` debe terminar en `/protegido/`, sin parámetros. El publicador añade `?cliente=UUID`. Usar `main` en la primera implementación. Si elige otra rama, cambiar también el filtro de `.github/workflows/publicar-pages.yml`.

```powershell
.\.venv\Scripts\python.exe "00 Code/herramientas/configurar.py"
.\.venv\Scripts\python.exe "00 Code/pruebas/probar_kit.py"
```

La primera herramienta prepara `config-public.json`, que contiene destino/rama/ruta, sin token ni clave. La segunda prueba es local: no publica ni lee la clave real.

## D. Elegir una sola clave web

```powershell
.\.venv\Scripts\python.exe "00 Code/herramientas/configurar_clave_web.py"
.\.venv\Scripts\python.exe "00 Code/herramientas/cifrar_dashboard.py"
```

La contraseña se introduce en una entrada oculta y se guarda en el almacén de Windows con el nombre configurado. No existe una clave por sondaje o proyecto, ni se pide al pulsar Subir. La web solicita esa clave común para descifrar localmente.

## E. Probar el envío antes del botón

Preparar un .wpcx **sintético** válido con su app y guardarlo. Luego:

```powershell
.\.venv\Scripts\python.exe "00 Code/herramientas/publicar_proyecto.py" "RUTA_AL_PROYECTO_FICTICIO.wpcx"
```

Ese comando sí hace una publicación real en el destino configurado. Verificar `ok=true`, el commit, el UUID y el enlace devueltos. No confundir un proceso terminado con una publicación confirmada. Si falla, revisar guía 05 antes de tocar la app.

Integrar ahora el botón según `00 Code/integracion/ENLACES_APP.md`. Para distribuir sin Python instalado en el emisor:

```powershell
.\.venv\Scripts\python.exe "00 Code/herramientas/compilar_publicador.py"
```

Copiar el ejecutable y su configuración no secreta como recursos de Tauri. Recompilar **la aplicación real** sin perder funciones, y probar su botón. No sustituirla por otra interfaz.

## F. Publicar el dashboard

El kit ya incluye un HTML base con el contrato de integración. Para el dashboard propio, leer guía 03 antes de sustituirlo. El cifrado de la fase D debe repetirse después de cambiar su HTML.

En GitHub, configurar el origen de Pages como **GitHub Actions**. Con la rama preparada y el destino comprobado, añadir únicamente la web, workflow e instrucciones:

```powershell
git add -- "00 Code/web" ".github/workflows/publicar-pages.yml" "README.md" "AGENTS.md" "CLAUDE.md" "01 Docx"
git commit -m "Publicar visor WPC conectado a HidroLog"
git push origin main
```

No usar `git add .` sin revisar antes el inventario. No añadir `02 Input/dashboard_base`, .wpcx, .venv, binarios, claves ni resultados. Revisar el origen remoto antes del push.

Esperar el estado **success** del workflow y abrir la URL de Pages. Si Git rechaza crear workflows por permisos, el usuario debe autorizar ese permiso en su sesión (`gh auth refresh -s workflow`, si aplica); no compartir su token con la LLM.

## G. Aceptación

Abrir el enlace con UUID devuelto por el emisor, introducir la clave web y comprobar que solo aparece el dashboard a pantalla completa. Repetir con 3, 6 y 12 m; la web consulta cada 30 s mientras está visible. Completar la guía 04 antes de entregar.

Fuentes oficiales consultadas: [autenticación de GitHub CLI](https://cli.github.com/manual/gh_auth_login), [configurar Git con gh](https://cli.github.com/manual/gh_auth_setup-git), [credenciales locales](https://docs.github.com/en/get-started/git-basics/caching-your-github-credentials-in-git), [publicación por workflows de Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages). Las pantallas de las LLM varían; estas instrucciones no suponen un conector específico.
