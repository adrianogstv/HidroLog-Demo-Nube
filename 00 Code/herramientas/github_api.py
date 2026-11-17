"""GitHub de la demo. La credencial existente solo se utiliza en memoria del PC."""
import json
import os
import shutil
import subprocess
import urllib.error
import urllib.request

OWNER = 'adrianogstv'
REPO = 'HidroLog-Demo-Nube'
API = 'https://api.github.com'


def request(method, path, data=None):
    if not path.startswith('/') or '://' in path:
        raise ValueError('Ruta de API no permitida')
    git = shutil.which('git') or 'C:/Program Files/Git/cmd/git.exe'
    env = dict(os.environ, GIT_TERMINAL_PROMPT='0', GCM_INTERACTIVE='never')
    result = subprocess.run(
        [git, 'credential', 'fill'],
        input=f'protocol=https\nhost=github.com\nusername={OWNER}\n\n',
        text=True, capture_output=True, env=env, timeout=25,
    )
    credential = dict(line.split('=', 1) for line in result.stdout.splitlines() if '=' in line)
    token = credential.get('password')
    if result.returncode or not token:
        raise RuntimeError('No hay sesión GitHub utilizable en Git Credential Manager. Inicia sesión en Git desde este PC.')
    req = urllib.request.Request(
        API + path, method=method,
        data=json.dumps(data).encode('utf-8') if data is not None else None,
        headers={'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json',
                 'X-GitHub-Api-Version': '2026-03-10', 'User-Agent': 'WPC-HidroLog-Demo'},
    )
    try:
        with urllib.request.urlopen(req, timeout=40) as response:
            body = response.read()
            return response.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as error:
        # Devolver solo el mensaje del servicio, nunca cabeceras ni credenciales.
        try:
            body = json.loads(error.read())
        except Exception:
            body = {}
        return error.code, {'message': body.get('message', 'Error de GitHub')}


def repo_request(method, path, data=None):
    return request(method, f'/repos/{OWNER}/{REPO}' + path, data)
