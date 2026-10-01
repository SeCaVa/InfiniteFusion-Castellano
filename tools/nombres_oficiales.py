"""Pone los nombres oficiales actuales de España (PokeAPI, idioma 7) en los
diccionarios de nombres: movimientos, objetos, habilidades y tipos.

- Pisa lo que haya (decisión: nombres oficiales más recientes), salvo las
  claves listadas en traduccion/bd/_nombres_manuales.json (ajustes a mano,
  p. ej. por ancho), que se respetan.
- Informe de cambios en traduccion/_informes/nombres_oficiales.txt.

Uso: PYTHONIOENCODING=utf-8 python tools/nombres_oficiales.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import pokeapi as pa
from extraer import TRAD, cargar_json, guardar_json

TABLAS = [('bd/movimientos', 'move'), ('bd/objetos', 'item'),
          ('bd/habilidades', 'ability'), ('bd/tipos', 'type'),
          ('bd/categorias', 'genus')]
# Especies: en España los Pokémon se llaman igual que en inglés; se copian tal
# cual del juego (así "Nidoran" y "Farfetch'd" quedan como los escribe PIF).


def referencia(tipo):
    if tipo != 'genus':
        return pa.nombres(tipo)
    # El juego guarda "Seed"; PokeAPI "Seed Pokémon" / "Pokémon Semilla"
    r = {}
    for d in pa.por_id('species', 'genus').values():
        en, es = d.get('en', ''), d.get('es', '')
        if en and es:
            en = en.replace(' Pokémon', '')
            es = es.replace('Pokémon ', '', 1)
            r.setdefault(pa.norm(en), es)
    return r



def main():
    esp = cargar_json('bd/especies')
    guardar_json('bd/especies', {k: k for k in esp})
    manuales = cargar_json('bd/_nombres_manuales')
    lineas = []
    for archivo, tipo in TABLAS:
        ref = referencia(tipo)
        d = cargar_json(archivo)
        fijos = set(manuales.get(archivo, {}))
        cambios = sin_ref = 0
        for en in d:
            if en in fijos:
                d[en] = manuales[archivo][en]
                continue
            es = ref.get(pa.norm(en))
            if es is None:
                sin_ref += 1
                continue
            if d[en] != es:
                lineas.append(f'{archivo}: {en} | {d[en] or "(vacío)"} → {es}')
                d[en] = es
                cambios += 1
        guardar_json(archivo, d)
        print(f'{archivo:20} {cambios:4} cambiados  {sin_ref:4} sin referencia en PokeAPI')
    with open(os.path.join(TRAD, '_informes', 'nombres_oficiales.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lineas) + '\n')


if __name__ == '__main__':
    main()
