"""Sustituciones globales de términos en las traducciones (nombres de la base que
no son los oficiales de España). Reglas en traduccion/_sustituciones.json:
  {"en": regex que debe aparecer en el inglés, "es": regex a buscar en la traducción, "por": texto nuevo}
Solo se aplican a diálogos, textos del código, frases de entrenadores, teléfono y ropa (no a bd/,
lugares/ ni entrenadores/nombres, que solo usa _personajes.json).
Informe en traduccion/_informes/sustituciones.txt.

Uso: PYTHONIOENCODING=utf-8 python tools/sustituir.py
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from extraer import TRAD, cargar_json, guardar_json


def main():
    reglas = [(re.compile(r['en']), re.compile(r['es']), r['por'])
              for r in json.load(open(os.path.join(TRAD, '_sustituciones.json'), encoding='utf-8'))]
    lineas = []
    for dp, _, fs in os.walk(TRAD):
        rel = os.path.relpath(dp, TRAD)
        if rel.split(os.sep)[0].startswith('_') or any(x in dp for x in (os.sep + 'bd', os.sep + 'lugares')):
            continue
        for fn in sorted(fs):
            if not fn.endswith('.json') or fn.startswith('_'):
                continue
            arch = os.path.relpath(os.path.join(dp, fn), TRAD).replace('\\', '/')[:-5]
            if arch.startswith('entrenadores/nombres'):   # nombres: solo personajes (_personajes.json)
                continue
            d = cargar_json(arch)
            cambio = False
            for en, es in d.items():
                if not es:
                    continue
                nuevo = es
                for rx_en, rx_es, por in reglas:
                    if rx_en.search(en):
                        nuevo = rx_es.sub(por, nuevo)
                if nuevo != es:
                    d[en] = nuevo
                    cambio = True
                    lineas.append(f'{arch}\n  ANTES: {es}\n  AHORA: {nuevo}')
            if cambio:
                guardar_json(arch, d)
    with open(os.path.join(TRAD, '_informes', 'sustituciones.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lineas) + '\n')
    print(f'{len(lineas)} cadenas cambiadas (traduccion/_informes/sustituciones.txt)')


if __name__ == '__main__':
    main()
