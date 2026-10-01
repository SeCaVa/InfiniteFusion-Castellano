"""Descarga y aplica exclusivamente los archivos de idioma del fork del usuario."""
import io
import os
from pathlib import Path, PurePosixPath
import stat
import tempfile
import urllib.request
import zipfile

REPOSITORY = 'https://github.com/SeCaVa/InfiniteFusion-Castellano'
BRANCH = 'traduccion'
ARCHIVE_URL = 'https://codeload.github.com/SeCaVa/InfiniteFusion-Castellano/zip/refs/heads/traduccion'
MAX_DOWNLOAD = 64 * 1024 * 1024
MAX_CONTENT = 128 * 1024 * 1024

def translation_files(raw, game):
    if game not in ('kanto', 'hoenn'):
        raise ValueError('Juego desconocido.')
    files = []
    total = 0
    seen = set()
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        for item in archive.infolist():
            parts = PurePosixPath(item.filename).parts
            if item.is_dir() or len(parts) < 3 or parts[1] != game:
                continue
            if '\\' in item.filename or item.filename.startswith('/') or any(p in ('.', '..') for p in parts):
                raise ValueError('El paquete contiene una ruta no válida.')
            if stat.S_ISLNK(item.external_attr >> 16):
                raise ValueError('El paquete contiene un enlace no válido.')
            rel = PurePosixPath(*parts[2:])
            allowed = (str(rel) == 'Data/spanish.dat' or
                       (rel.parts[:2] == ('Data', 'Scripts') and rel.suffix == '.rb') or
                       (rel.parts[:3] == ('Graphics', 'Localized', 'es') and rel.suffix.lower() == '.png'))
            if not allowed:
                continue
            if str(rel).casefold() in seen:
                raise ValueError('El paquete contiene archivos duplicados.')
            seen.add(str(rel).casefold())
            total += item.file_size
            if total > MAX_CONTENT:
                raise ValueError('El paquete de traducción supera el tamaño permitido.')
            files.append((str(rel), archive.read(item)))
    if not any(rel == 'Data/spanish.dat' for rel, _ in files):
        raise ValueError('No se encuentra spanish.dat en la rama de traducción.')
    return files

def download_translation(game, log_fn):
    log_fn('Descargando la traducción al castellano…')
    req = urllib.request.Request(ARCHIVE_URL, headers={'User-Agent': 'InfiniteFusion-Castellano-Launcher/1.1'})
    with urllib.request.urlopen(req, timeout=60) as response:
        raw = response.read(MAX_DOWNLOAD + 1)
    if len(raw) > MAX_DOWNLOAD:
        raise ValueError('La descarga de la traducción supera el tamaño permitido.')
    files = translation_files(raw, game)
    log_fn(f'Traducción descargada y comprobada: {len(files)} archivos.')
    return files

def _write_atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    name = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.castellano-', delete=False) as out:
            name = out.name
            out.write(data)
        os.replace(name, path)
    finally:
        if name and os.path.exists(name):
            os.unlink(name)

def apply_translation(target, files, log_fn):
    target = Path(target).resolve()
    planned = []
    for rel, data in files:
        dest = (target / rel).resolve()
        if not dest.is_relative_to(target):
            raise ValueError('Un archivo de traducción apunta fuera de la carpeta del juego.')
        planned.append((dest, data))
    backups = []
    try:
        for dest, data in planned:
            old = dest.read_bytes() if dest.exists() else None
            backups.append((dest, old))
            _write_atomic(dest, data)
    except Exception:
        for dest, old in reversed(backups):
            if old is None:
                dest.unlink(missing_ok=True)
            else:
                _write_atomic(dest, old)
        raise
    log_fn('Traducción al castellano aplicada. Elige Español dentro del juego.')

BUTTON_LABELS = {
    'launch': ('JUGAR', 56, (202, 28, 321, 69)),
    'install': ('INSTALAR', 30, (221, 39, 337, 63)),
    'open_folder': ('ABRIR CARPETA', 30, (183, 10, 361, 35)),
    'update': ('ACTUALIZAR', 30, (209, 9, 312, 34)),
    'back': ('VOLVER', 30, (238, 11, 307, 36)),
    'retry': ('REINTENTAR', 30, (230, 10, 372, 35)),
}

def button_label_layout(path):
    """Capa de texto de la interfaz; el sprite original permanece intacto."""
    from PIL import Image, ImageDraw, ImageFont
    path = Path(path)
    name = path.stem.removeprefix('actionBtn_').removesuffix('_sel')
    text, size, region = BUTTON_LABELS[name]
    font = ImageFont.truetype(str(path.parent.parent / 'fonts/power_clear.ttf'), size)
    left, top, right, bottom = font.getbbox(text)
    layer = Image.new('RGBA', (right - left, bottom - top))
    ImageDraw.Draw(layer).text((-left, -top), text, font=font, fill='#ffffff')
    x = round((region[0] + region[2] - layer.width) / 2)
    y = round((region[1] + region[3] - layer.height) / 2)
    # Recover the same horizontal background stripes behind the old lettering.
    # The sample column lies beyond every label and before the selection corners.
    with Image.open(path) as asset:
        background = asset.convert('RGB')
        bands = []
        for row in range(region[1], region[3]):
            rgb = background.getpixel((450, row))
            color = '#%02x%02x%02x' % rgb
            if bands and bands[-1][2] == color:
                bands[-1] = (bands[-1][0], row + 1, color)
            else:
                bands.append((row, row + 1, color))
    return region, bands, layer, (x, y)

def draw_action_button(button, path, selected):
    """Conserva los sprites y estados originales, con su fuente de píxeles."""
    from PIL import Image, ImageTk
    with Image.open(path) as asset:
        original = asset.convert('RGBA')
    button.configure(width=original.width, height=original.height)
    button._img_ref = ImageTk.PhotoImage(original, master=button)
    button.create_image(0, 0, anchor='nw', image=button._img_ref, tags='original_sprite')
    region, bands, label, (x, y) = button_label_layout(path)
    for top, bottom, color in bands:
        button.create_rectangle(region[0], top, region[2], bottom,
                                fill=color, outline='', width=0, tags='old_label_background')
    button._label_ref = ImageTk.PhotoImage(label, master=button)
    button.create_image(x, y, anchor='nw', image=button._label_ref, tags='spanish_label')

def verify_startup(report_path):
    """Diagnóstico explícito (--verificar): sin red, configuración personal ni juego."""
    import json
    import sys
    import types
    import tkinter as tk
    remote = types.ModuleType('remote_config')
    remote.fetch_games = lambda: {}
    remote.fetch_social_links = lambda: []
    sys.modules['remote_config'] = remote
    config = types.ModuleType('config')
    config.load_config = lambda: {}
    config.save_config = lambda value: None
    sys.modules['config'] = config
    import installer
    assert callable(installer.run_install)
    installer.GAMES = installer._fallback_games()
    base = Path(getattr(sys, '_MEIPASS', Path(__file__).parent))
    assert (base / '_tcl_data/init.tcl').is_file(), f'Falta init.tcl en el runtime: {[p.name for p in base.iterdir() if "tcl" in p.name.lower()]}'
    assert (base / '_tk_data/tk.tcl').is_file(), 'Falta tk.tcl en el runtime'
    root = tk.Tk()
    root.withdraw()
    checked = []
    for name in ('launch', 'install', 'update', 'back', 'retry', 'open_folder'):
        button = tk.Canvas(root)
        path = base / 'resources/buttons' / f'actionBtn_{name}.png'
        for selected in (False, True):
            variant = path.with_name(path.stem + '_sel.png') if selected else path
            button.delete('all')
            draw_action_button(button, variant, selected)
            root.update_idletasks()
            assert button.find_withtag('original_sprite')
            bounds = button.bbox('spanish_label')
            assert 0 <= bounds[0] < bounds[2] <= int(button.cget('width'))
            assert 0 <= bounds[1] < bounds[3] <= int(button.cget('height'))
        checked.append(name)
        button.destroy()
    root.destroy()
    config.load_config = lambda: {f'last_install_path_{game}': str(base / 'diagnostic-game')
                                 for game in ('kanto', 'hoenn')}
    import installer_ui as ui
    # Run callbacks in this test's Tk thread, with no network background work.
    class ImmediateThread:
        def __init__(self, target, **kwargs):
            self.target = target
        def start(self):
            self.target()
    ui.threading.Thread = ImmediateThread
    app = ui.InstallerApp()
    app.withdraw()
    errors = []
    app.report_callback_exception = lambda *args: errors.append(str(args[1]))
    app.geometry('900x720')
    app.update()
    for game in ('kanto', 'hoenn'):
        app._select_game(game)
        app._show_persistent_buttons()
        app.update_idletasks()
        assert app.install_btn.find_all(), 'El botón de instalación está vacío'
        assert app.title().endswith('Castellano')
    # Exercise the update/launch controls on a simulated existing installation.
    installer.is_existing_folder = lambda *args: True
    app._show_persistent_buttons()
    app.update_idletasks()
    for button in (app.launch_btn, app.open_folder_btn, app.update_btn):
        assert button.winfo_manager() == 'place'
        assert button.find_withtag('original_sprite')
        left, top, right, bottom = button.bbox('spanish_label')
        assert left >= 0 and right <= int(button.cget('width'))
    app._show_log_panel()
    app._log('Traducción al castellano aplicada.')
    app._show_main_screen()
    app.update_idletasks()
    app.destroy()
    assert not errors, errors
    Path(report_path).write_text(json.dumps({'runtime': 'ok', 'tk_buttons': checked,
                               'button_style': 'original sprites + Power Clear labels', 'button_states': ['normal', 'selected'],
                               'ui_themes': ['kanto', 'hoenn'], 'ui_states': ['install', 'update', 'log', 'menu'],
                               'translation_repository': REPOSITORY,
                               'branch': BRANCH, 'network_used': False}, indent=2), encoding='utf-8')

LABELS = {'Pokémon Infinite Fusion — Launcher': 'Pokémon Infinite Fusion — Castellano', 'BROWSE': 'EXAMINAR', 'LAUNCH GAME': 'JUGAR', 'Install': 'Instalar', 'Update': 'Actualizar', 'Back to main menu': 'Volver al menú', 'TRY AGAIN': 'REINTENTAR', "OPEN THE GAME'S FOLDER": 'ABRIR CARPETA DEL JUEGO', 'Installing the game...  This may take a few minutes.': 'Instalando el juego… Puede tardar unos minutos.', 'Install location: ': 'Carpeta de instalación: ', 'Select install folder': 'Selecciona la carpeta de instalación', 'Install path set to: ': 'Carpeta de instalación: ', 'No path specified.': 'No has indicado una carpeta.', 'Folder does not exist: ': 'La carpeta no existe: ', 'Could not find ': 'No se encuentra ', ' in the game folder.': ' en la carpeta del juego.', 'Please set an install location.': 'Selecciona una carpeta de instalación.', 'Starting install to: ': 'Iniciando la instalación en: ', 'Installing…  This will probably take a few minutes.\nPlease be patient.': 'Instalando… Puede tardar unos minutos.\nEspera, por favor.', 'Using bundled git: ': 'Usando el Git incluido: ', 'git is not installed. Please install it and try again.': 'Git no está instalado. Instálalo y vuelve a intentarlo.', 'git not found — downloading MinGit (one-time setup)…': 'Descargando MinGit para preparar la instalación…', '  Downloading MinGit… ': '  Descargando MinGit… ', '  Download complete — verifying…': '  Descarga completada. Comprobando…', 'MinGit checksum mismatch — download may be corrupt.\n': 'La comprobación de MinGit ha fallado. La descarga puede estar dañada.\n', 'MinGit checksum mismatch — download may be corrupt.\n  expected: ': 'La comprobación de MinGit ha fallado. La descarga puede estar dañada.\n  esperado: ', '  expected: ': '  esperado: ', '\n  got:      ': '\n  obtenido: ', '  Checksum OK — extracting…': '  Comprobación correcta. Extrayendo…', 'MinGit extraction failed — git.exe not found after unzip.': 'No se encuentra git.exe después de extraer MinGit.', '  MinGit ready: ': '  MinGit preparado: ', 'Failed to download MinGit: ': 'No se ha podido descargar MinGit: ', '\nPlease try downloading installing git manually instead.\n': '\nPrueba a instalar Git manualmente.\n', 'Found existing repo at ': 'Instalación encontrada en ', ' — checking for updates…': '. Buscando actualizaciones…', 'Cloning ': 'Descargando ', 'No new update found.': 'El juego ya está actualizado.', '.\nCheck the logs in the console below for details.': '.\nConsulta el registro de abajo para ver los detalles.', 'Could not finish ': 'No se ha podido completar la operación: ', 'installing': 'instalación', 'updating': 'actualización', 'Successfully ': 'Juego ', 'installed': 'instalado', 'updated': 'actualizado', 'FAQ': 'Preguntas frecuentes', 'Fusion Calculator': 'Calculadora de fusiones', 'Calculator': 'Calculadora', 'Website': 'Web', 'Icon load failed:': 'No se ha podido cargar el icono:', 'Rejected suspicious repo for ': 'Repositorio no válido para '}
def translate_label(label):
    return LABELS.get(label, label)
