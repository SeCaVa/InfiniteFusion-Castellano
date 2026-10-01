"""Genera un ejecutable independiente usando el runtime del lanzador original.

Solo compila fuentes locales Python 3.12 y reconstruye los archivos PyInstaller.
No ejecuta el juego, no instala dependencias y no modifica el .exe original.
"""
import ast
import hashlib
import importlib.util
import json
import marshal
from pathlib import Path
import struct
import sys
import zlib

ROOT = Path(__file__).resolve().parent
ORIGINAL = ROOT.parent / 'installation/PokemonInfiniteFusion-Launcher_1.1.exe'
OUTPUT = ROOT.parent / 'installation/PokemonInfiniteFusion-Launcher_1.1-Castellano.exe'
MAGIC = b'MEI\x0c\x0b\x0a\x0b\x0e'
COOKIE = struct.Struct('!8sIIII64s')
ENTRY = struct.Struct('!IIIIBc')

def read_archive(raw):
    pos = raw.rfind(MAGIC)
    if pos < 0:
        raise ValueError('No es un ejecutable PyInstaller compatible.')
    magic, length, toc_offset, toc_len, version, library = COOKIE.unpack(raw[pos:pos + COOKIE.size])
    if version != 312 or sys.version_info[:2] != (3, 12):
        raise ValueError('Esta compilación requiere Python 3.12, igual que el original.')
    start = pos + COOKIE.size - length
    cursor = start + toc_offset
    entries = []
    while cursor < start + toc_offset + toc_len:
        size, offset, compressed, plain, flag, typ = ENTRY.unpack(raw[cursor:cursor + ENTRY.size])
        name = raw[cursor + ENTRY.size:cursor + size].split(b'\0')[0].decode('utf-8')
        payload = raw[start + offset:start + offset + compressed]
        entries.append(dict(name=name, payload=payload, plain=plain, flag=flag, typ=typ))
        cursor += size
    return raw[:start], entries, version, library

def write_archive(prefix, entries, version, library):
    data = bytearray()
    toc = bytearray()
    for entry in entries:
        name = entry['name'].encode('utf-8') + b'\0'
        size = (ENTRY.size + len(name) + 15) // 16 * 16
        row = ENTRY.pack(size, len(data), len(entry['payload']), entry['plain'], entry['flag'], entry['typ'])
        toc.extend(row + name + b'\0' * (size - len(row) - len(name)))
        data.extend(entry['payload'])
    cookie = COOKIE.pack(MAGIC, len(data) + len(toc) + COOKIE.size, len(data), len(toc), version, library)
    return prefix + data + toc + cookie

def payload(entry):
    return zlib.decompress(entry['payload']) if entry['flag'] else entry['payload']

def read_pyz(raw):
    if raw[:4] != b'PYZ\0' or raw[4:8] != importlib.util.MAGIC_NUMBER:
        raise ValueError('Versión de bytecode incompatible.')
    toc = marshal.loads(raw[struct.unpack('!I', raw[8:12])[0]:])
    if isinstance(toc, dict):
        toc = list(toc.items())
    return raw[:8], [(name, info[0], raw[info[1]:info[1] + info[2]]) for name, info in toc]

def write_pyz(header, modules):
    raw = bytearray(header + b'\0' * 4)
    toc = []
    for name, typ, code in modules:
        toc.append((name, (typ, len(raw), len(code))))
        raw.extend(code)
    raw[8:12] = struct.pack('!I', len(raw))
    raw.extend(marshal.dumps(toc))
    return bytes(raw)

class Translate(ast.NodeTransformer):
    def __init__(self, translations):
        self.translations = translations
    def visit_Constant(self, node):
        if isinstance(node.value, str) and node.value in self.translations:
            return ast.copy_location(ast.Constant(self.translations[node.value]), node)
        return node

def source_ui():
    src = (ROOT / 'original/installer_ui.py').read_text(encoding='utf-8')
    src = 'from launcher_es import draw_action_button, translate_label\n' + src
    src = ('import sys as _verify_sys\n'
           'if __name__ == "__main__" and "--verificar" in _verify_sys.argv:\n'
           '    _report = _verify_sys.argv[_verify_sys.argv.index("--verificar") + 1]\n'
           '    try:\n'
           '        from launcher_es import verify_startup\n'
           '        verify_startup(_report)\n'
           '    except Exception:\n'
           '        import traceback\n'
           '        from pathlib import Path\n'
           '        Path(_report).write_text(traceback.format_exc(), encoding="utf-8")\n'
           '        raise SystemExit(1)\n'
           '    raise SystemExit(0)\n' + src)
    old = '        if path and os.path.isfile(path):\n'
    new = ('        if path and os.path.isfile(path) and os.path.basename(path).startswith("actionBtn_"):\n'
           '            draw_action_button(self, path, use_sel)\n'
           '            return\n' + old)
    assert src.count(old) == 1
    src = src.replace(old, new)
    src = src.replace('label=item["label"],', 'label=translate_label(item["label"]),')
    return src

def source_installer():
    src = (ROOT / 'original/installer.py').read_text(encoding='utf-8')
    src = 'from launcher_es import download_translation, apply_translation\n' + src
    old = '    # Resolve git, downloading MinGit if necessary\n'
    new = ('    # Verify the language package before the official updater changes files.\n'
           '    try:\n'
           '        translation = download_translation(game_key, log_fn)\n'
           '    except Exception as exc:\n'
           '        done_fn(False, f"No se ha podido descargar la traducción: {exc}")\n'
           '        return\n\n' + old)
    assert src.count(old) == 1
    src = src.replace(old, new)
    old = '        if rc == 0:\n            action = "updated" if was_update else "installed"\n'
    new = ('        if rc == 0:\n'
           '            apply_translation(target, translation, log_fn)\n'
           '            action = "updated" if was_update else "installed"\n')
    assert src.count(old) == 1
    src = src.replace(old, new)
    src = src.replace('            done_fn(True, update_message)',
                      '            done_fn(True, update_message + "\\nTraducción al castellano aplicada.")')
    return src

def compile_translated(src, name, translations):
    tree = Translate(translations).visit(ast.parse(src, filename=name))
    ast.fix_missing_locations(tree)
    source = ast.unparse(tree) + '\n'
    (ROOT / 'src' / name).write_text(source, encoding='utf-8')
    return marshal.dumps(compile(tree, name, 'exec'))

def main():
    (ROOT / 'src').mkdir(exist_ok=True)
    translations = json.loads((ROOT / 'es.json').read_text(encoding='utf-8'))
    original = ORIGINAL.read_bytes()
    original_hash = hashlib.sha256(original).hexdigest()
    prefix, entries, version, library = read_archive(original)
    ui = compile_translated(source_ui(), 'installer_ui.py', translations)
    installer = compile_translated(source_installer(), 'installer.py', translations)
    helper = (ROOT / 'launcher_es.py').read_text(encoding='utf-8')
    helper += '\nLABELS = ' + repr(translations) + '\ndef translate_label(label):\n    return LABELS.get(label, label)\n'
    (ROOT / 'src/launcher_es.py').write_text(helper, encoding='utf-8')
    helper_code = marshal.dumps(compile(helper, 'launcher_es.py', 'exec'))
    # Font rasterization needs Pillow's FreeType extension, omitted by the
    # original launcher. Keep Python and native Pillow components at one version.
    import PIL
    pillow_dir = Path(PIL.__file__).parent
    pillow_modules = {}
    for path in pillow_dir.glob('*.py'):
        name = 'PIL' if path.stem == '__init__' else 'PIL.' + path.stem
        code = compile(path.read_text(encoding='utf-8'), 'PIL/' + path.name, 'exec')
        pillow_modules[name] = (1 if name == 'PIL' else 0, zlib.compress(marshal.dumps(code), 9))
    for entry in entries:
        if entry['name'] == 'installer_ui':
            entry.update(payload=zlib.compress(ui, 9), plain=len(ui), flag=1)
        elif entry['name'] == 'PYZ.pyz':
            header, modules = read_pyz(payload(entry))
            assert any(name == 'installer' for name, _, _ in modules)
            modules = [(name, typ, zlib.compress(installer, 9) if name == 'installer' else code)
                       for name, typ, code in modules]
            modules.append(('launcher_es', 0, zlib.compress(helper_code, 9)))
            modules.append(('installer_ui', 0, zlib.compress(ui, 9)))
            modules = [(name, *pillow_modules.pop(name)) if name in pillow_modules else (name, typ, code)
                       for name, typ, code in modules]
            modules.extend((name, typ, code) for name, (typ, code) in pillow_modules.items())
            # The original launcher used font tuples only; our fitted Tk labels
            # also need tkinter.font, which its dependency archive omitted.
            if not any(name == 'tkinter.font' for name, _, _ in modules):
                import tkinter.font
                font_source = Path(tkinter.font.__file__).read_text(encoding='utf-8')
                font_code = compile(font_source, 'tkinter/font.py', 'exec')
                modules.append(('tkinter.font', 0, zlib.compress(marshal.dumps(font_code), 9)))
            pyz = write_pyz(header, modules)
            entry.update(payload=pyz, plain=len(pyz), flag=0)
    replacements = {e['name']: e for e in entries}
    for path in (*pillow_dir.glob('*.pyd'), *pillow_dir.glob('*.dll')):
        name = 'PIL\\' + path.name
        raw = path.read_bytes()
        if name in replacements:
            replacements[name].update(payload=zlib.compress(raw, 9), plain=len(raw), flag=1)
        else:
            entries.append(dict(name=name, payload=zlib.compress(raw, 9), plain=len(raw), flag=1, typ=b'b'))
    result = write_archive(prefix, entries, version, library)
    # Verify all packed streams and modified Python modules before delivery.
    check_prefix, check_entries, _, _ = read_archive(result)
    assert check_prefix == prefix
    for entry in check_entries:
        raw = payload(entry)
        assert len(raw) == entry['plain'], entry['name']
        if entry['name'] == 'installer_ui':
            assert marshal.loads(raw).co_filename == 'installer_ui.py'
        elif entry['name'] == 'PYZ.pyz':
            _, modules = read_pyz(raw)
            for name, _, code in modules:
                marshal.loads(zlib.decompress(code))
    OUTPUT.write_bytes(result)
    assert hashlib.sha256(ORIGINAL.read_bytes()).hexdigest() == original_hash
    report = {'original_sha256': original_hash, 'output_sha256': hashlib.sha256(result).hexdigest(),
              'output': OUTPUT.name, 'source': 'https://github.com/infinitefusion/PIFInstallerGUI',
              'translation_repo': 'https://github.com/SeCaVa/InfiniteFusion-Castellano',
              'translation_branch': 'traduccion', 'entries_verified': len(entries),
              'pillow_version': PIL.__version__, 'button_style': 'original sprites + Power Clear labels'}
    (ROOT / 'build-info.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(f'Creado y verificado: {OUTPUT.name} ({len(result) / 1e6:.1f} MB)')

if __name__ == '__main__':
    main()
