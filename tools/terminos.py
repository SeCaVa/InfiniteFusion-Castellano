"""Coherencia de términos: si el inglés de un diálogo o texto nombra un objeto,
movimiento, habilidad o lugar, la traducción debería llevar su nombre oficial
(o su plural). Informe en traduccion/_informes/terminos.txt, agrupado por término.

Uso: PYTHONIOENCODING=utf-8 python tools/terminos.py [--min 1]
"""
import os
import re
import sys
import unicodedata
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from extraer import TRAD, cargar_json

TABLAS = ['bd/objetos', 'bd/objetos_plural', 'bd/movimientos', 'bd/habilidades', 'lugares/mapas', 'lugares/lugares',
          '_personajes']   # _personajes: nombres de España verificados en WikiDex
# términos inglés demasiado comunes para comprobarlos
IGNORAR = {'Surf', 'Normal', 'Protect', 'Rest', 'Return', 'Present', 'Thing', 'Gate', 'House', 'Map',
           'Hotel', 'Elevator', 'Harbour', 'Underground', 'Lighthouse', 'Intro', 'Messages', 'Kanto',
           'Johto', 'Hoenn', 'Unova', 'Sevii', 'Credits', 'Blank', 'new', 'Game Corner', 'Soaring', 'Letter',
           'Letters', 'Coffee', 'Pizza', 'Beer', 'Stick', 'Sticks', 'Upgrade', 'Magnet', 'Bricks', 'Diamond',
           'Emerald', 'Ruby', 'Sapphire', 'Explosion', 'Rage', 'Swift', 'Flash', 'Strength', 'Fly', 'Cut',
           'Pay Day', 'Growl', 'Bide', 'Guard', 'Memento', 'Pickup', 'Simple', 'Honey', 'Pearl',
           'Will', 'Elite 1', 'Elite 2', 'Elite 3', 'Elite 4', 'Champion', 'Routes', 'Cities', 'Dungeons', 'Area 1',
           'Area 2', 'Area 3', 'Area 4', 'Area 5', 'Gates', 'Hotel 2nd Floor', 'Assist'}   # nombres de mapas internos   # Will: también es verbo ("Will you...")


def plano(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn')


def main():
    minimo = int(sys.argv[sys.argv.index('--min') + 1]) if '--min' in sys.argv else 1
    terminos = {}
    for t in TABLAS:
        for en, es in cargar_json(t).items():
            if es and en != es and len(en) >= 4 and en not in IGNORAR and not re.fullmatch(r'(Route|Ruta) \d+|[BT]?M?\d+F?|HM\d+|TM\d+', en):
                terminos.setdefault(en, set()).add(es)
    # plurales del singular: añadir también la forma plural como válida
    sing = cargar_json('bd/objetos')
    plur = cargar_json('bd/objetos_plural')
    patrones = sorted(terminos, key=len, reverse=True)
    rx = re.compile(r'(?<![\w])(' + '|'.join(re.escape(p) for p in patrones) + r')(?![\w])')
    fallos = defaultdict(list)
    for dp, _, fs in os.walk(TRAD):
        if any(x in dp for x in ('_informes', '_revision')):
            continue
        for fn in fs:
            if not fn.endswith('.json') or fn.startswith('_'):
                continue
            arch = os.path.relpath(os.path.join(dp, fn), TRAD).replace('\\', '/')[:-5]
            if arch in TABLAS or arch.startswith('bd/'):
                continue
            for en, es in cargar_json(arch).items():
                if not es:
                    continue
                vistos = set()
                for m in rx.finditer(en):
                    t = m.group(1)
                    if t in vistos:
                        continue
                    vistos.add(t)
                    validos = set(terminos[t])
                    for s_en, s_es in sing.items():
                        pass
                    if not any(plano(v) in plano(es) for v in validos):
                        fallos[t].append((arch, en, es))
    lineas = []
    for t, lst in sorted(fallos.items(), key=lambda x: -len(x[1])):
        if len(lst) < minimo:
            continue
        lineas.append(f'## {t} → {" / ".join(sorted(terminos[t]))}  ({len(lst)})')
        for arch, en, es in lst[:6]:
            lineas.append(f'  [{arch}] EN: {en[:110]}\n      ES: {es[:110]}')
    with open(os.path.join(TRAD, '_informes', 'terminos.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lineas) + '\n')
    print(f'{sum(len(v) for v in fallos.values())} cadenas sin el término oficial, {len(fallos)} términos '
          '(traduccion/_informes/terminos.txt)')
    for t, lst in sorted(fallos.items(), key=lambda x: -len(x[1]))[:25]:
        print(f'  {len(lst):4}  {t} → {" / ".join(sorted(terminos[t]))}')


if __name__ == '__main__':
    main()
