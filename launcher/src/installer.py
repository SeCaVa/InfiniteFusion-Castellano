from launcher_es import download_translation, apply_translation
'\ninstaller.py — game download logic with portable-git fallback.\n\nPortable Git (Windows-only) is downloaded on demand from the official\nGitHub release and extracted into  <script_dir>/vendor/git/  so the\nuser never has to install anything manually.\n'
import os
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path
from remote_config import fetch_games
MINGIT_URL = 'https://github.com/git-for-windows/git/releases/download/v2.45.2.windows.1/MinGit-2.45.2-64-bit.zip'
MINGIT_SHA256 = '7ed2a3ce5bbbf8eea976488de5416894ca3e6a0347cee195a7d768ac146d5290'
_SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
_VENDOR_DIR = _SCRIPT_DIR / 'vendor'
_GIT_DIR = _VENDOR_DIR / 'git'
_GIT_EXE = _GIT_DIR / 'cmd' / 'git.exe'
_GIT_INSTALL_URL = 'https://git-scm.com/install/'
ALLOWED_REPO_PREFIX = 'https://github.com/infinitefusion/'

def _load_games() -> dict:
    games = fetch_games()
    for key, game in games.items():
        if not game.get('repo', '').startswith(ALLOWED_REPO_PREFIX):
            print(f"Repositorio no válido para {key}: {game['repo']}")
            return _fallback_games()
    return games

def _fallback_games():
    return {'kanto': {'label': 'Pokémon Infinite Fusion 1', 'subtitle': 'Kanto', 'repo': 'https://github.com/infinitefusion/infinitefusion-e18.git', 'branch': 'releases', 'folder': 'InfiniteFusion', 'exe': 'Game.exe'}, 'hoenn': {'label': 'Pokémon Infinite Fusion 2', 'subtitle': 'Hoenn', 'repo': 'https://github.com/infinitefusion/infinitefusion-hoenn-public.git', 'branch': 'releases', 'folder': 'InfiniteFusion2', 'exe': 'InfiniteFusion2.exe'}}
GAMES = _load_games()

def _system_git() -> str | None:
    """Return the path to a system-installed git, or None."""
    return shutil.which('git')

def _bundled_git() -> str | None:
    """Return the path to the bundled MinGit executable, or None if not extracted."""
    if _GIT_EXE.is_file():
        return str(_GIT_EXE)
    return None

def git_available() -> bool:
    """True if any git (system or bundled) is usable right now."""
    return bool(_system_git() or _bundled_git())

def _resolve_git(log_fn, done_fn) -> str | None:
    """
    Return a usable git path, downloading MinGit first if needed.
    Calls done_fn(False, msg) and returns None on unrecoverable failure.
    Only downloads on Windows; on other platforms we give up if git is missing.
    """
    git = _system_git()
    if git:
        return git
    git = _bundled_git()
    if git:
        log_fn(f'Usando el Git incluido: {git}')
        return git
    if sys.platform != 'win32':
        done_fn(False, 'Git no está instalado. Instálalo y vuelve a intentarlo.')
        return None
    log_fn('Descargando MinGit para preparar la instalación…')
    zip_path = _VENDOR_DIR / 'mingit.zip'
    try:
        _VENDOR_DIR.mkdir(parents=True, exist_ok=True)

        def _reporthook(count, block_size, total_size):
            if total_size > 0:
                pct = min(100, count * block_size * 100 // total_size)
                log_fn(f'  Descargando MinGit… {pct}%', True)
        urllib.request.urlretrieve(MINGIT_URL, zip_path, _reporthook)
        log_fn('  Descarga completada. Comprobando…', False)
        import hashlib
        h = hashlib.sha256(zip_path.read_bytes()).hexdigest()
        if MINGIT_SHA256 and h != MINGIT_SHA256:
            done_fn(False, f'La comprobación de MinGit ha fallado. La descarga puede estar dañada.\n  esperado: {MINGIT_SHA256}\n  obtenido: {h}')
            zip_path.unlink(missing_ok=True)
            return None
        log_fn('  Comprobación correcta. Extrayendo…')
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(_GIT_DIR)
        zip_path.unlink(missing_ok=True)
        git = _bundled_git()
        if not git:
            done_fn(False, 'No se encuentra git.exe después de extraer MinGit.')
            return None
        log_fn(f'  MinGit preparado: {git}')
        return git
    except Exception as exc:
        done_fn(False, f'No se ha podido descargar MinGit: {exc}\nPrueba a instalar Git manualmente.\n{_GIT_INSTALL_URL}')
        zip_path.unlink(missing_ok=True)
        return None

def run_install(game_key: str, install_dir: str, log_fn, done_fn):
    game = GAMES[game_key]
    install_path = Path(install_dir)
    if install_path.name == game['folder']:
        target = install_path
    else:
        target = install_path / game['folder']
    try:
        translation = download_translation(game_key, log_fn)
    except Exception as exc:
        done_fn(False, f'No se ha podido descargar la traducción: {exc}')
        return
    git_exe = _resolve_git(log_fn, done_fn)
    if git_exe is None:
        return
    env = os.environ.copy()
    if git_exe == str(_GIT_EXE):
        git_bin = str(_GIT_EXE.parent)
        env['PATH'] = git_bin + os.pathsep + env.get('PATH', '')
        env['GIT_EXEC_PATH'] = str(_GIT_DIR / 'mingw64' / 'libexec' / 'git-core')
        env['GIT_CONFIG_NOSYSTEM'] = '1'
    last_line = ['']

    def run(cmd, cwd=None):
        creationflags = 0
        startupinfo = None
        if sys.platform == 'win32':
            creationflags = subprocess.CREATE_NO_WINDOW
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, env=env, cwd=cwd, creationflags=creationflags, startupinfo=startupinfo)
        last_prefix = None
        for line in proc.stdout:
            line = line.rstrip()
            colon_pos = line.find(':')
            prefix = line[:colon_pos].strip() if colon_pos != -1 else None
            replace = prefix is not None and prefix == last_prefix
            log_fn(line, replace)
            last_prefix = prefix
            if line.strip():
                last_line[0] = line.strip()
        proc.wait()
        return proc.returncode

    def _capture(cmd):
        """Run a command quietly and return (returncode, stdout_text)."""
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
        return (result.returncode, result.stdout.strip())
    try:
        if is_existing_folder(target, game):
            log_fn(f'Instalación encontrada en {target}. Buscando actualizaciones…')
            branch = game['branch'] or 'HEAD'
            _, old_head = _capture([git_exe, '-C', str(target), 'rev-parse', 'HEAD'])
            rc = run([git_exe, '-C', str(target), 'fetch', '--depth=1', '--recurse-submodules', 'origin', branch])
            if rc == 0:
                rc = run([git_exe, '-C', str(target), 'reset', '--hard', f'origin/{branch}'])
            if rc == 0:
                run([git_exe, '-C', str(target), 'submodule', 'update', '--init', '--recursive', '--depth=1'])
            was_update = True
            if rc == 0:
                _, new_head = _capture([git_exe, '-C', str(target), 'rev-parse', 'HEAD'])
                last_line[0] = 'Already up to date.' if old_head and old_head == new_head else 'Updated.'
        else:
            target.mkdir(parents=True, exist_ok=True)
            log_fn(f"Descargando {game['label']} ({game['subtitle']})…")
            cmd = [git_exe, 'clone', '--progress', '-v', '--recurse-submodules', '--depth=1']
            if game['branch']:
                cmd += ['-b', game['branch']]
            cmd += [game['repo'], str(target)]
            rc = run(cmd)
            was_update = False
        if rc == 0:
            apply_translation(target, translation, log_fn)
            action = 'actualizado' if was_update else 'instalado'
            update_message = f'Juego {action}!'
            if last_line[0] == 'Already up to date.':
                update_message = 'El juego ya está actualizado.'
            done_fn(True, update_message + '\nTraducción al castellano aplicada.')
        else:
            action = 'actualización' if was_update else 'instalación'
            done_fn(False, f'No se ha podido completar la operación: {action}.\nConsulta el registro de abajo para ver los detalles.')
    except Exception as exc:
        done_fn(False, f'Error: {exc}')

def verify_game_name(folder_path, game):
    ini_path = folder_path / 'Game.ini'
    if not ini_path.is_file():
        return False
    expected_titles = {'InfiniteFusion': 'infinitefusion', 'InfiniteFusion2': 'infinitefusion-hoenn'}
    expected = expected_titles.get(game['folder'])
    if expected is None:
        return False
    import configparser
    config = configparser.ConfigParser()
    config.read(ini_path, encoding='utf-8')
    return config.get('Game', 'Title', fallback='').strip() == expected

def is_existing_folder(folder_path, game):
    return folder_path.exists() and (folder_path / '.git').exists() and verify_game_name(folder_path, game)
