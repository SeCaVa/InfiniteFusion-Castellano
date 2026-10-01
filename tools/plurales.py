"""Plurales de objetos (bd/objetos_plural.json) a partir del singular castellano.

- Reglas propias para los casos regulares (MT/MO, Balls, Bayas, sustantivo + complemento).
- Un TSV externo (propuesta de otro modelo: "plural inglés<TAB>plural español") se
  acepta solo si concuerda con el singular; si no, se informa para revisión a mano.
- Aplica solo a claves vacías o iguales al singular (lo que copió la base), y nunca
  a las de traduccion/bd/_plurales_manuales.json.

Uso: PYTHONIOENCODING=utf-8 python tools/plurales.py [propuesta.tsv]
"""
import json
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(__file__))
import rmarshal as rm
from extraer import REPOS, TRAD, cargar_json, guardar_json

INVARIABLES = {'Miel', 'Restos', 'Gafas', 'Tijeras', 'Pokédex', 'Revivir', 'Restaurar',
               'Más', 'Repartir', 'Carbón', 'Arena', 'Agua', 'Leche', 'Polvo', 'Hielo'}


def sin_tilde(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')


def pluralizar_palabra(p):
    if p in INVARIABLES or not re.search(r'[a-záéíóúñ]', p):
        return p
    if re.search(r'[aeiouáéó]$', p):
        return p + 's'
    if p.endswith('í') or p.endswith('ú'):
        return p + 's'
    if p.endswith('z'):
        return p[:-1] + 'ces'
    if p.endswith('s') or p.endswith('x'):
        return p
    # agudas con tilde en la última sílaba pierden la tilde: Poción -> Pociones
    base = p
    m = re.search(r'([áéíóú])([^aeiouáéíóú]*)$', p)
    if m and re.search(r'[aeiouáéíóú]', p[:m.start()]) is not None and p[-1] in 'nsl' + 'r':
        base = p[:m.start()] + sin_tilde(m.group(1)) + m.group(2)
    return base + 'es'


ADJ = re.compile(r'^(?:[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:o|a|e|l|z|r))$')
COLORES_FEM = {'Roja', 'Negra', 'Blanca', 'Amarilla', 'Azul', 'Verde', 'Rosa'}


def regla(es):
    """Plural por regla o None si no es un caso claro."""
    if re.fullmatch(r'(?:MT|MO|DT)\d+', es):
        return es
    if es.endswith(' Ball') or es.startswith('Ball '):
        return es.replace('Ball', 'Balls', 1)
    if es.startswith('Baya '):
        return 'Bayas ' + es[5:]
    partes = es.split(' ')
    if len(partes) == 1:
        return pluralizar_palabra(es)
    return None


def main(propuesta=None):
    sing = cargar_json('bd/objetos')
    plur = cargar_json('bd/objetos_plural')
    manuales = cargar_json('bd/_plurales_manuales')
    # singular inglés <-> plural inglés
    par = {}
    for g in ('kanto', 'hoenn'):
        m = rm.load_messages(os.path.join(REPOS, g, 'Data', 'messages.dat'))
        for i, en in enumerate(m[7]):
            if en and i < len(m[8]) and m[8][i]:
                par.setdefault(m[8][i], en)
    prop = {}
    if propuesta:
        for linea in open(propuesta, encoding='utf-8'):
            if '\t' in linea:
                a, b = linea.rstrip('\n').split('\t', 1)
                prop[a] = b.strip()
    revisar = []
    aplicadas = 0
    for en_pl, actual in plur.items():
        if en_pl in manuales:
            plur[en_pl] = manuales[en_pl]
            continue
        en_sg = par.get(en_pl)
        es_sg = sing.get(en_sg or '', '')
        if not es_sg or (actual and actual != es_sg):
            continue
        r = regla(es_sg)
        p = prop.get(en_pl, '')
        marcada = p.endswith('*')
        p = p.rstrip('*').strip()
        # la propuesta debe empezar por la primera palabra del singular en plural (o igual)
        primera = es_sg.split(' ')[0]
        coherente = p and (p.split(' ')[0] in (primera, pluralizar_palabra(primera))
                           or p == es_sg)
        if r and p and r != p:
            revisar.append(f'{en_pl}: singular "{es_sg}" | regla "{r}" | propuesta "{p}"')
            elegido = r
        elif r:
            elegido = r
        elif coherente and not marcada:
            elegido = p
        else:
            revisar.append(f'{en_pl}: singular "{es_sg}" | propuesta "{p}" (no concuerda)')
            continue
        if elegido != actual:
            plur[en_pl] = elegido
            aplicadas += 1
    guardar_json('bd/objetos_plural', plur)
    with open(os.path.join(TRAD, '_informes', 'plurales_revisar.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(revisar) + '\n')
    print(f'{aplicadas} plurales aplicados; {len(revisar)} para revisar (traduccion/_informes/plurales_revisar.txt)')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else None)
