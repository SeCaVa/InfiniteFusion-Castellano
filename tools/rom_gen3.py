"""Lectura de textos de la ROM oficial de Pokémon Rojo Fuego en español
(solo como referencia de nombres oficiales; la ROM no se publica ni se sube).

- Codificación de 3.ª generación según referencias/pokefirered/charmap.txt.
- nombres_mapas(): {nombre inglés de pokefirered: nombre oficial español}, emparejados
  por el orden de MAPSEC de region_map_sections.json.

Uso: PYTHONIOENCODING=utf-8 python tools/rom_gen3.py "Pokemon - Edicion Rojo Fuego (Spain).gba"
"""
import json
import os
import re
import struct
import sys

REF = os.path.join(os.path.dirname(__file__), '..', 'referencias', 'pokefirered')
ROM_POR_DEFECTO = os.path.join(os.path.dirname(__file__), '..', 'Pokemon - Edicion Rojo Fuego (Spain).gba')


def cargar_charmap():
    dec = {}
    for linea in open(os.path.join(REF, 'charmap.txt'), encoding='utf-8'):
        m = re.match(r"^'(.)'\s*=\s*([0-9A-Fa-f]{2})\s*$", linea)
        if m and int(m.group(2), 16) not in dec:
            dec[int(m.group(2), 16)] = m.group(1)
    dec[0x00] = ' '
    return dec


DEC = cargar_charmap()
ENC = {v: k for k, v in DEC.items()}


def codificar(s):
    return bytes(ENC[c] for c in s)


def leer(rom, off, maxlen=300):
    out = []
    for b in rom[off:off + maxlen]:
        if b == 0xFF:
            break
        if b == 0xFE:
            out.append('\n')
        else:
            out.append(DEC.get(b, f'[{b:02X}]'))
    return ''.join(out)


def nombres_mapas(rom):
    """Tabla de punteros a los nombres de MAPSEC de Kanto (desde PUEBLO PALETA)."""
    secciones = json.load(open(os.path.join(REF, 'region_map_sections.json'), encoding='utf-8'))['map_sections']
    ini = next(i for i, s in enumerate(secciones) if s['id'] == 'MAPSEC_PALLET_TOWN')
    # La tabla de nombres empieza en PUEBLO PALETA y sigue con CIUDAD VERDE
    # (hay otras tablas que también apuntan a "PUEBLO PALETA").
    tabla = None
    for m in re.finditer(re.escape(codificar('PUEBLO PALETA') + b'\xff'), rom):
        ptr = struct.pack('<I', 0x08000000 + m.start())
        i = rom.find(ptr)
        while i >= 0 and tabla is None:
            sig = struct.unpack('<I', rom[i + 4:i + 8])[0] - 0x08000000
            if 0 <= sig < len(rom) and leer(rom, sig, 20) == 'CIUDAD VERDE':
                tabla = i
            i = rom.find(ptr, i + 4)
    r = {}
    i = 0
    while ini + i < len(secciones):
        p = struct.unpack('<I', rom[tabla + 4 * i:tabla + 4 * i + 4])[0]
        if not 0x08000000 <= p < 0x08000000 + len(rom):
            break
        sec = secciones[ini + i]
        if 'name' in sec:
            r.setdefault(sec['name'], leer(rom, p - 0x08000000))
        i += 1
    return r


MINUSCULAS = {'de', 'del', 'la', 'el', 'al', 'y', 'en', 'a', 'los', 'las'}


def titulo(s):
    """'PUEBLO PALETA' -> 'Pueblo Paleta'; 'POKéMON' -> 'Pokémon'; siglas (S.A., S.S.) intactas."""
    out = []
    for i, p in enumerate(s.split(' ')):
        if i > 0 and p.lower() in MINUSCULAS:
            out.append(p.lower())
        elif p == 'CC':
            out.append('C.C.')
        elif p == 'ARCHI7':
            out.append('Archi7')
        elif re.fullmatch(r'(?:[A-Z]\.)+[A-Z]?\.?', p):
            out.append(p)
        else:
            out.append(p[:1] + p[1:].lower())
    return ' '.join(out)


def guardar_referencia(rom, destino):
    datos = {en: {'rojo_fuego': es, 'titulo': titulo(es)} for en, es in nombres_mapas(rom).items()}
    with open(destino, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)
    return datos


if __name__ == '__main__':
    rom = open(sys.argv[1] if len(sys.argv) > 1 else ROM_POR_DEFECTO, 'rb').read()
    print(rom[0xA0:0xAC], rom[0xAC:0xB0])
    for en, es in nombres_mapas(rom).items():
        print(f'{en:28} {es}')
