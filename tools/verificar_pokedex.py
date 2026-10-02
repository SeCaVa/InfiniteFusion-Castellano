"""Valida las entradas revisadas y su distribución sin ejecutar el juego.

La simulación de páginas usa la fuente incluida; la medida definitiva es la
de Bitmap.text_size en el juego. No sustituye la comprobación visual en partida.
"""
import hashlib
import json
from pathlib import Path
import re
from PIL import ImageFont
import rmarshal as rm
from revisar import codigos
from aplicar_pokedex_fusiones import apply, REL

ROOT = Path(__file__).resolve().parents[1]

def pages(text, measure, width=424):
    lines, current = [], ''
    for word in text.split():
        candidate = word if not current else current + ' ' + word
        if current and measure(candidate) > width:
            lines.append(current)
            current = word
        else:
            current = candidate
        if measure(current) > width:
            fragment = ''
            for char in current:
                if fragment and measure(fragment + char) > width:
                    lines.append(fragment)
                    fragment = char
                else:
                    fragment += char
            current = fragment
    if current:
        lines.append(current)
    return [lines[i:i+3] for i in range(0, len(lines), 3)] or [[]]

def main():
    translations = json.loads((ROOT / 'traduccion/pokedex/fusiones.json').read_text(encoding='utf-8'))
    assert translations
    for en, es in translations.items():
        assert isinstance(es, str) and es.strip() and en != es
        assert codigos(en) == codigos(es), en
        assert en.count('POKENAME') == es.count('POKENAME'), en
        assert not re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', es)
    before = [(ROOT / 'repos' / game / REL).read_bytes() for game in ('kanto', 'hoenn')]
    apply()
    for i, game in enumerate(('kanto', 'hoenn')):
        source = ROOT / 'repos' / game
        assert before[i] == (source / REL).read_bytes(), 'Aplicación no idempotente'
        reader = (source / REL).read_text(encoding='utf-8')
        assert '@entry_author = nil unless reloading' in reader
        assert '@entry_text = nil unless reloading' in reader
        assert 'customEntry, entryAuthor = @entry_text, @entry_author' in reader
        assert reader.count('gsub(/[[:space:]]+/, " ").strip') == 2
        messages = rm.load_messages(str(source / 'Data/spanish.dat'))
        for en, es in translations.items():
            assert messages[24][rm.string_to_key(en)] == es, (game, en)
        targets = [ROOT / 'publicar' / game]
        if game == 'kanto':
            targets.append(ROOT / 'installation/InfiniteFusion')
        for target in targets:
            for rel in (REL, Path('Data/spanish.dat')):
                assert (source / rel).read_bytes() == (target / rel).read_bytes(), target / rel
        snapshots = ROOT / 'traduccion/_pokedex/sources.json'
        if snapshots.exists():
            expected = json.loads(snapshots.read_text(encoding='utf-8'))[game]['sha256']
            assert hashlib.sha256((source / 'Data/pokedex/dex.json').read_bytes()).hexdigest() == expected
        print(f'{game}: {len(translations)} entradas en mensajes; copias idénticas y originales intactos.')
    font = ImageFont.truetype(str(ROOT / 'repos/kanto/Fonts/power green.ttf'), 29)
    max_pages = 0
    for es in [*translations.values(), 'X' * 300, '']:
        text = es.replace('POKENAME', 'Bulbizarrexecutor')
        result = pages(text, font.getlength)
        max_pages = max(max_pages, len(result))
        assert all(len(p) <= 3 for p in result)
        assert all(font.getlength(line) <= 424 for p in result for line in p)
        assert ''.join(text.split()) == ''.join(line.replace(' ', '') for p in result for line in p)
        n = len(result)
        assert [(i + 1) % n for i in range(n)] == list(range(1, n)) + [0]
    print(f'Simulación Power Green 29: contenido íntegro, anchuras válidas, ciclo de hasta {max_pages} páginas.')
    print('Pendiente: sintaxis Ruby y comprobación visual dentro del juego.')

if __name__ == '__main__':
    main()
