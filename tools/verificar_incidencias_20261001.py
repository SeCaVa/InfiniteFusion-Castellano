"""Comprueba los textos reales de eventos y los archivos generados, sin abrir el juego."""
from pathlib import Path
import re
from PIL import Image, ImageChops, ImageFont
import rmarshal as rm
from extraer import RE_LLAMADA, leer_literal
from corregir_incidencias_20261001 import ROOT, CAMBIOS
from sincronizar_incidencias_20261001 import GRAFICOS

MENU = ["The game's official Discord", "The game's subreddit",
        "The game's Pokecommunity thread", "A Pokémon Infinite Fusion website", "Other"]

def clave_ruby(text):
    # Ruby ^ y $ se refieren a líneas, a diferencia del modo Python por defecto.
    text = re.sub(r'^\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s+$', '', text, flags=re.MULTILINE)
    return re.sub(r'\s{2,}', ' ', text)

def comprobar_menu_real(data, es):
    events = rm.loads((data / 'CommonEvents.rxdata').read_bytes())
    src = '\n'.join(c.attrs['@parameters'][0] for c in events[108].attrs['@list']
                    if c.attrs['@code'] in (355, 655))
    # Tanto el menú con _INTL como el menú antiguo de Hoenn contienen estos literales.
    raw = [leer_literal(src, m.start())[0] for m in re.finditer(r'"(?:The game|A Pokémon Infinite Fusion|Other)', src)]
    assert len(raw) == 5, raw
    uses_intl = 'options=[_INTL(' in src
    current = [es[24].get(clave_ruby(option), option) for option in raw] if uses_intl else raw
    normalized = [re.sub(r'\s+', ' ', option).strip() for option in current]
    assert "The game's official Discord" in normalized, normalized
    result = [es[24].get(clave_ruby(option), option) for option in normalized]
    assert result == [es[24][option] for option in MENU], result
    print(f'{data.parent.name}: menú real, incluidos saltos de línea, traducido por completo')

def main():
    for game in ('kanto', 'hoenn'):
        data = ROOT / 'repos' / game / 'Data'
        eng = rm.load_messages(str(data / 'messages.dat'))
        es = rm.load_messages(str(data / 'spanish.dat'))
        for name in ('Bulbasaur', 'Charmander', 'Squirtle', '\\V[5]'):
            key = f'Do you want to choose {name}?'
            expected = f'¿Quieres elegir a {name}?'
            assert es[0][0].get(key) == expected, (game, key)
            # El respaldo debe funcionar con un mapa sin esa cadena e incluso
            # con un ID no incluido en messages.dat.
            for mid in (0, 77, len(es[0]) + 1):
                own = es[0][mid] if mid < len(es[0]) and isinstance(es[0][mid], dict) else {}
                assert own.get(key, es[0][0].get(key)) == expected, (game, mid, key)
        picture_key = '\\f[\\v[4]]Do you want to choose \\V[5]?'
        assert es[0][0][picture_key] == '\\f[\\v[4]]¿Quieres elegir a \\V[5]?'
        print(f'{game}: confirmaciones de iniciales y códigos de control disponibles como respaldo')
        comprobar_menu_real(data, es)
        for key in MENU + ["Rival's nickname?", 'Blue', 'You put on the hat(s)!\\wtnp[30]']:
            assert es[24][key] and es[24][key] != key, (game, key)
        assert es[24]['Blue'] == 'Azul'
        assert es[24]['You put on the hat(s)!\\wtnp[30]'] == '¡Te pusiste la gorra!\\wtnp[30]'
        for i, name in enumerate(eng[21]):
            if name == 'Messages':
                assert es[21][i] == 'Mensajes', (game, i)
        # El menú real de Kanto usa literales Ruby partidos entre comandos.
        events = rm.loads((data / 'CommonEvents.rxdata').read_bytes())
        event = events[108]
        src = '\n'.join(c.attrs['@parameters'][0] for c in event.attrs['@list']
                        if c.attrs['@code'] in (355, 655))
        for m in RE_LLAMADA.finditer(src):
            literal = leer_literal(src, m.end())
            if literal:
                key = rm.string_to_key(literal[0])
                if 'official' in key or 'subreddit' in key or 'website' in key or 'Pokecommunity' in key:
                    assert es[24].get(key), (game, repr(key))
        for script in ('repos/scripts/DownloadedSettings.rb',
                       f'repos/{game}/Data/Scripts/DownloadedSettings.rb'):
            path = ROOT / script
            if not path.exists():
                continue
            for line in path.read_text(encoding='utf-8').splitlines():
                if 'STARTUP_MESSAGES' in line and 'Pokémon Infinite Fusion 2' in line:
                    literal = leer_literal(line, line.index('"'))
                    assert es[24].get(rm.string_to_key(literal[0])), (game, line)
        destinos = [ROOT / 'publicar' / game]
        if game == 'kanto':
            destinos.append(ROOT / 'installation/InfiniteFusion')
            comprobar_menu_real(ROOT / 'installation/InfiniteFusion/Data', es)
        for dest in destinos:
            for rel in ['Data/spanish.dat', *('Data/Scripts/' + p for p in CAMBIOS)]:
                assert (dest / rel).read_bytes() == (ROOT / 'repos' / game / rel).read_bytes(), dest / rel
        print(f'{game}: traducciones de eventos, aviso de inicio, mapa y copias correctas')
    for text in ('Castaño oscuro', 'Castaño claro'):
        fonts = ROOT / 'repos/kanto/Fonts'
        size = next(size for size in range(29, 24, -1)
                    if ImageFont.truetype(str(fonts / 'power green.ttf'), size).getlength(text) <= 172)
        assert size >= 27, (text, size)
        assert 194 - 92 > 70 and 234 + 92 < 328  # margen del rótulo y de la foto
        print(f'{text}: fuente normal de {size}px, campo de 184px con margen interior')
    for text, limit in [('Objetos de combate', 172)]:
        f = ImageFont.truetype(str(ROOT / 'repos/kanto/Fonts/power green narrow.ttf'), 29 * 3 // 4)
        assert f.getlength(text) <= limit, (text, f.getlength(text), limit)
        print(f'{text}: cabe en {limit}px con la fuente permitida')
    for variant in ('', '_kanto'):
        for rel in GRAFICOS:
            src = ROOT / f'traduccion/graficos/en{variant}' / rel
            dst = ROOT / f'traduccion/graficos/es{variant}' / rel
            if not src.exists():
                continue
            a, b = Image.open(src).convert('RGBA'), Image.open(dst).convert('RGBA')
            assert a.size == b.size
            delta = ImageChops.difference(a, b)
            # getbbox de RGBA puede ocultar cambios RGB si no cambia el alfa.
            box = delta.convert('RGB').getbbox()
            assert box and box[0] >= 30 and box[1] >= 258 and box[2] <= 176 and box[3] <= 284, (rel, box)
            assert a.getchannel('A').tobytes() == b.getchannel('A').tobytes(), rel
    print('Gráficos: mismas dimensiones y transparencia; cambios solo en DELANTE/DETRÁS')

if __name__ == '__main__':
    main()
