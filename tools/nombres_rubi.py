"""Nombres oficiales de los entrenadores de Hoenn a partir de las ROM de Rubí
(USA y España; solo como referencia, no se publican ni se suben).

Las dos ROM guardan la tabla de entrenadores en el mismo orden (registros de 40
bytes; el nombre son 12 bytes a partir del byte 4), así que el entrenador i de
una es el i de la otra. Escribe traduccion/entrenadores/nombres_hoenn.json con
los nombres de entrenador de Hoenn que tienen nombre oficial distinto del inglés
(generar_dat.py los aplica solo al juego de Hoenn). Los personajes con nombre
oficial siguen saliendo de _personajes.json.

Uso: PYTHONIOENCODING=utf-8 python tools/nombres_rubi.py
"""
import os
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
import rmarshal as rm
from extraer import RAIZ, REPOS, cargar_json, guardar_json
from rom_gen3 import codificar, leer

ROM_EN = os.path.join(RAIZ, 'Pokemon - Ruby Version (USA, Europe) (Rev 2).gba')
ROM_ES = os.path.join(RAIZ, 'Pokemon - Edicion Rubi (Spain) (Rev 1).gba')


def tabla(rom, conocido):
    """Lista de nombres de la tabla de entrenadores (se localiza por un nombre conocido)."""
    pat = codificar(conocido) + b'\xff'
    for m in re.finditer(re.escape(pat), rom):
        i = m.start() - 4
        if all(0xFF in rom[i + 4 + k * 40:i + 16 + k * 40] for k in (-1, 1, 2)):
            while rom[i - 40 + 4] != 0xFF and 0xFF in rom[i - 40 + 4:i - 40 + 16]:
                i -= 40
            nombres = []
            while 0xFF in rom[i + 4:i + 16] or rom[i + 4] == 0:
                nombres.append(leer(rom, i + 4, 12))
                i += 40
                if len(nombres) > 900:
                    break
            return nombres
    raise SystemExit(f'No encuentro la tabla de entrenadores ({conocido})')


def titulo(s):
    s = s.replace(' & ', ' y ').replace('&', ' y ')
    return ' '.join(w if w == 'y' else w[:1] + w[1:].lower() for w in s.split())


def main():
    en = tabla(open(ROM_EN, 'rb').read(), 'ROXANNE')
    es = tabla(open(ROM_ES, 'rb').read(), 'PETRA')
    # Tras la tabla vienen otros datos (se leen como nombres basura); zip los empareja
    # igual en las dos ROM y no coinciden con nombres reales.
    opciones = defaultdict(set)
    for a, b in zip(en, es):
        if a.strip() and b.strip():
            opciones[titulo(a).lower()].add(titulo(b))
            # Parejas ("AMY & LIV" / "ALI-LÍA"): cada nombre por separado
            pa, pb = re.split(r' ?& ?| Y ', a), re.split(r' ?[&-] ?| Y ', b)
            if len(pa) == 2 == len(pb):
                for x, y in zip(pa, pb):
                    opciones[titulo(x).lower()].add(titulo(y))
    personajes = cargar_json('_personajes')
    hoenn = rm.load_messages(os.path.join(REPOS, 'hoenn', 'Data', 'messages.dat'))[14]
    nombres = hoenn.keys() if isinstance(hoenn, dict) else [s for s in hoenn if s]
    r, ambiguos = {}, []
    for n in sorted(set(nombres)):
        if n in personajes:
            continue
        o = opciones.get(n.lower().replace(' & ', ' y '))
        if not o:
            continue
        if len(o) > 1:
            ambiguos.append(f'{n}: {sorted(o)}')
            continue
        v = next(iter(o))
        if v != n:
            r[n] = v
    guardar_json('entrenadores/nombres_hoenn', r)
    print(f'{len(en)} entrenadores en Rubí; {len(r)} nombres de Hoenn con nombre oficial distinto')
    if ambiguos:
        print('Ambiguos (no se aplican):', '; '.join(ambiguos))


if __name__ == '__main__':
    main()
