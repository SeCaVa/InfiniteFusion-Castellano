"""Nombres de mapas y lugares (lugares/mapas.json y lugares/lugares.json).

Fuentes, por prioridad:
  1. traduccion/lugares/_manuales.json      ajustes a mano
  2. referencias/lugares_wikidex.json       WikiDex (nombres actuales de España)
  3. PokeAPI (location_names, idioma 7)
  4. referencias/lugares_rojo_fuego.json    ROM oficial de Rojo Fuego (Islas Sete…)
Después, reglas para nombres compuestos: "Route 5" → "Ruta 5",
"Cerulean City Gym" → "Gimnasio de Ciudad Celeste", "2F" → "P2", "\\PN's House" → "Casa de \\PN"…

Solo rellena entradas vacías (o todas con --forzar). Lo que no se resuelve queda
listado en traduccion/_informes/lugares_pendientes.txt.

Uso: PYTHONIOENCODING=utf-8 python tools/lugares.py [--forzar]
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import pokeapi as pa
from extraer import TRAD, cargar_json, guardar_json

REF = os.path.join(os.path.dirname(__file__), '..', 'referencias')


def clave(s):
    """Normaliza para comparar: sin tildes ni signos y sin letras dobles (Vermillion/Vermilion)."""
    s = pa.norm(s.replace('’', "'"))
    return re.sub(r'([a-z])\1', r'\1', s)


def tabla_oficial():
    t = {}
    rf = json.load(open(os.path.join(REF, 'lugares_rojo_fuego.json'), encoding='utf-8'))
    for en, d in rf.items():
        t[clave(en)] = d['titulo']
    for en, es in pa.nombres('location').items():
        t[re.sub(r'([a-z])\1', r'\1', en)] = es
    wd = json.load(open(os.path.join(REF, 'lugares_wikidex.json'), encoding='utf-8'))
    for en, es in wd.items():
        if not en.startswith('_'):
            t[clave(en)] = es
    man = cargar_json('lugares/_manuales')
    for en, es in man.items():
        t[clave(en)] = es
    return t


def plantas(s):
    m = re.fullmatch(r'B(\d+)F?', s)
    if m:
        return f'S{m.group(1)}'
    m = re.fullmatch(r'(\d+)F', s)
    if m:
        return f'P{m.group(1)}'
    return None


def traducir(en, t, prof=0):
    if not en.strip():
        return en
    k = clave(en)
    if k in t:
        return t[k]
    if prof > 3:
        return None
    p = plantas(en)
    if p:
        return p
    m = re.fullmatch(r'Route (\d+)', en)
    if m:
        return f'Ruta {m.group(1)}'
    # "X B1F", "X 2F": lugar + planta
    m = re.fullmatch(r'(.+?)\s+(B\d+F?|\d+F)', en)
    if m and plantas(m.group(2)):
        base = traducir(m.group(1), t, prof + 1)
        return f'{base} {plantas(m.group(2))}' if base else None
    m = re.fullmatch(r"\\PN's (House|Room|Home)", en)
    if m:
        return {'House': 'Casa de \\PN', 'Home': 'Casa de \\PN', 'Room': 'Habitación de \\PN'}[m.group(1)]
    # "Cerulean City Gym" / "Viridian Gym"
    m = re.fullmatch(r'(.+?) (Gym|Pokémon Center|Pokemon Center|PokéMart|Poké Mart|Pokemart|Gate|House|Museum)', en)
    if m:
        base = traducir(m.group(1), t, prof + 1)
        if not base and m.group(2) not in ('Gate', 'House', 'Museum'):
            # "Viridian" → "Ciudad Verde" si existe "Viridian City"/"Viridian Town"/"Viridian Island"
            for suf in (' City', ' Town', ' Island'):
                base = t.get(clave(m.group(1) + suf))
                if base:
                    break
        if base:
            tipo = {'Gym': 'Gimnasio', 'Pokémon Center': 'Centro Pokémon', 'Pokemon Center': 'Centro Pokémon',
                    'PokéMart': 'Tienda Pokémon', 'Poké Mart': 'Tienda Pokémon', 'Pokemart': 'Tienda Pokémon',
                    'Gate': 'Acceso', 'House': 'Casa', 'Museum': 'Museo'}[m.group(2)]
            return f'{tipo} de {base}'
    return None


def main():
    forzar = '--forzar' in sys.argv
    t = tabla_oficial()
    pendientes = []
    for archivo in ('lugares/mapas', 'lugares/lugares', 'lugares/regiones'):
        d = cargar_json(archivo)
        n = 0
        for en in d:
            if d[en] and not forzar:
                continue
            es = traducir(en, t)
            if es:
                d[en] = es
                n += 1
            else:
                if forzar:
                    d[en] = ''
                pendientes.append(f'{archivo}: {en}')
        guardar_json(archivo, d)
        print(f'{archivo:18} {n:4} rellenados')
    with open(os.path.join(TRAD, '_informes', 'lugares_pendientes.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(pendientes) + '\n')
    print(f'{len(pendientes)} pendientes (traduccion/_informes/lugares_pendientes.txt)')


if __name__ == '__main__':
    main()
