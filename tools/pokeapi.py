"""Acceso a los CSV de PokeAPI guardados en referencias/pokeapi/.

Idiomas: es = 7, en = 9.
  nombres('move')    -> {nombre inglés normalizado: nombre español}
  descripciones('move') -> {id: {version_group: texto es}}
"""
import csv
import os
import re
import unicodedata

CSV = os.path.join(os.path.dirname(__file__), '..', 'referencias', 'pokeapi')
ES, EN = 7, 9

TABLAS = {
    'move': ('move_names.csv', 'move_id', 'name'),
    'item': ('item_names.csv', 'item_id', 'name'),
    'ability': ('ability_names.csv', 'ability_id', 'name'),
    'type': ('type_names.csv', 'type_id', 'name'),
    'species': ('pokemon_species_names.csv', 'pokemon_species_id', 'name'),
    'genus': ('pokemon_species_names.csv', 'pokemon_species_id', 'genus'),
    'location': ('location_names.csv', 'location_id', 'name'),
    'nature': ('nature_names.csv', 'nature_id', 'name'),
    'stat': ('stat_names.csv', 'stat_id', 'name'),
}


def norm(s):
    """Clave para emparejar nombres ingleses con distinta grafía
    ("ViceGrip" / "Vise Grip", "Poké Ball" / "Poke Ball", "X Attack" / "X-Attack")."""
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]', '', s)


def _leer(nombre):
    with open(os.path.join(CSV, nombre), encoding='utf-8') as f:
        return list(csv.DictReader(f))


def por_id(tipo, campo=None):
    """{id: {'en': ..., 'es': ...}}"""
    archivo, col_id, col = TABLAS[tipo]
    col = campo or col
    r = {}
    for fila in _leer(archivo):
        lang = int(fila['local_language_id'])
        if lang in (ES, EN):
            r.setdefault(int(fila[col_id]), {})['es' if lang == ES else 'en'] = fila[col]
    return r


def nombres(tipo, campo=None):
    """{norm(inglés): español}"""
    r = {}
    for d in por_id(tipo, campo).values():
        if d.get('en') and d.get('es'):
            r.setdefault(norm(d['en']), d['es'])
    return r


def descripciones(tipo):
    """{id: {version_group_id o version_id: texto}} en español."""
    archivo = {'move': 'move_flavor_text.csv', 'item': 'item_flavor_text.csv',
               'ability': 'ability_flavor_text.csv',
               'species': 'pokemon_species_flavor_text.csv'}[tipo]
    col_id = {'move': 'move_id', 'item': 'item_id', 'ability': 'ability_id',
              'species': 'species_id'}[tipo]
    col_ver = 'version_id' if tipo == 'species' else 'version_group_id'
    col_txt = 'flavor_text'
    r = {}
    for fila in _leer(archivo):
        lang = fila.get('language_id') or fila.get('local_language_id')
        if int(lang) == ES:
            r.setdefault(int(fila[col_id]), {})[int(fila[col_ver])] = fila[col_txt]
    return r
