"""Importa la traducción al castellano que trae el repositorio de Hoenn
(referencias/base_es/*.dat, hecha sobre los índices de Kanto) como punto de
partida de los diccionarios.

- Solo rellena entradas vacías: nunca pisa lo ya traducido.
- Omite las que son idénticas al inglés (suelen estar sin traducir).
- Guarda en traduccion/_informes/base_importada.json qué claves vienen de la
  base, para revisarlas después (revisar.py).

Uso: PYTHONIOENCODING=utf-8 python tools/importar_base.py referencias/base_es/archivo.dat
"""
import json
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(__file__))
import rmarshal as rm
from extraer import ARCHIVOS_SECCION, REPOS, TRAD, cargar_json, guardar_json


def main(ruta_base):
    base = rm.load_messages(ruta_base)
    eng = rm.load_messages(os.path.join(REPOS, 'kanto', 'Data', 'messages.dat'))
    propuestas = defaultdict(lambda: defaultdict(Counter))   # archivo -> inglés -> {es: n}

    for sec in range(1, len(base)):
        archivo = ARCHIVOS_SECCION.get(sec)
        b = base[sec]
        if not archivo or not b:
            continue
        if isinstance(b, list):
            en = eng[sec] if isinstance(eng[sec], list) else []
            for i, es in enumerate(b):
                if es and i < len(en) and en[i] and es != en[i]:
                    propuestas[archivo][en[i]][es] += 1
        elif isinstance(b, dict):
            for k, es in b.items():
                if es and es != k:
                    propuestas[archivo][k][es] += 1

    # diálogos: al archivo del mapa si la cadena es propia, si no a comun.json
    for mid, h in enumerate(base[0] or []):
        if not isinstance(h, dict):
            continue
        propio = f'dialogos/kanto/Map{mid:03d}'
        claves_propias = set(cargar_json(propio))
        for k, es in h.items():
            if es and es != k:
                archivo = propio if k in claves_propias else 'dialogos/comun'
                propuestas[archivo][k][es] += 1

    importadas = {}
    resumen = []
    for archivo, props in sorted(propuestas.items()):
        d = cargar_json(archivo)
        if not d:
            continue
        n = conflictos = 0
        claves = []
        for en, votos in props.items():
            if en in d and not d[en]:
                d[en] = votos.most_common(1)[0][0]
                conflictos += len(votos) > 1
                claves.append(en)
                n += 1
        if n:
            guardar_json(archivo, d)
            importadas[archivo] = claves
        if not archivo.startswith('dialogos/kanto/'):
            resumen.append(f'{archivo:28} {n:6} importadas ({conflictos} con varias versiones)')
    mapas = [a for a in importadas if a.startswith('dialogos/kanto/')]
    resumen.append(f'dialogos/kanto (mapas)       {sum(len(importadas[a]) for a in mapas):6} importadas en {len(mapas)} mapas')
    informe = os.path.join(TRAD, '_informes', 'base_importada.json')
    previo = cargar_json(informe)
    for a, ks in importadas.items():
        previo[a] = sorted(set(previo.get(a, [])) | set(ks))
    guardar_json(informe, previo)
    print('\n'.join(resumen))


if __name__ == '__main__':
    main(sys.argv[1])
