"""Genera repos/<juego>/Data/spanish.dat a partir de los diccionarios de traduccion/.

- Secciones lista (nombres, descripciones…): se busca cada texto inglés en su
  diccionario; también vale una clave "@<id>" para traducir solo ese índice.
- Secciones hash (entrenadores, textos del código, ropa…): se incluyen todas las
  entradas traducidas del diccionario.
- <diccionario>_<juego>.json (si existe) tiene prioridad en ese juego; p. ej.
  entrenadores/nombres_hoenn.json: nombres oficiales de Rubí para Hoenn.
- Diálogos: por mapa, primero dialogos/<juego>/MapNNN.json y después dialogos/comun.json.
- Lo que no está traducido se deja vacío y el juego muestra el inglés.
- Las marcas de género [[masc|fem]] se dejan tal cual: las resuelve el juego
  al buscar el texto (cambio de código en 003_Intl_Messages.rb).

Uso: PYTHONIOENCODING=utf-8 python tools/generar_dat.py [kanto|hoenn ...]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import rmarshal as rm
from extraer import ARCHIVOS_SECCION, REPOS, TRAD, JUEGOS, cargar_json


def dic(archivo, cache={}):
    if archivo not in cache:
        cache[archivo] = {k: v for k, v in cargar_json(archivo).items() if v}
    return cache[archivo]


def ids_tipos_entrenador(juego):
    """Índice de la sección TrainerTypes → ID del tipo (p. ej. 'SWIMMER_F')."""
    raw = open(os.path.join(REPOS, juego, 'Data', 'trainer_types.dat'), 'rb').read()
    try:
        datos = rm.loads(raw)
    except ValueError:
        datos = rm.loads(rm.xor(raw))
    ids = {}
    for v in (datos.values() if isinstance(datos, dict) else datos):
        if isinstance(v, rm.RObj):
            a = {(k.decode() if isinstance(k, bytes) else k): x for k, x in v.attrs.items()}
            i = a.get('@id')
            ids[a.get('@id_number')] = i.decode() if isinstance(i, bytes) else i
    return ids


def generar(juego):
    eng = rm.load_messages(os.path.join(REPOS, juego, 'Data', 'messages.dat'))
    out = [None] * len(eng)
    stats = []

    # diálogos
    comun = dic('dialogos/comun')
    mapas = []
    total = trad = 0
    for mid, oh in enumerate(eng[0] or []):
        if not isinstance(oh, dict):
            mapas.append(None)
            continue
        propio = dic(f'dialogos/{juego}/Map{mid:03d}')
        h = rm.OrderedHash()
        for k in oh:
            v = propio.get(k) or comun.get(k)
            if v:
                h[k] = v
        total += len(oh)
        trad += len(h)
        mapas.append(h)
    # El juego consulta el mapa 0 como respaldo cuando un evento reutilizado
    # muestra el texto desde otro mapa. Incluir todas las cadenas comunes,
    # no solo las que messages.dat enumera originalmente dentro del mapa 0.
    if not mapas:
        mapas.append(rm.OrderedHash())
    if not isinstance(mapas[0], dict):
        mapas[0] = rm.OrderedHash()
    for k, v in comun.items():
        if k not in mapas[0]:
            mapas[0][k] = v
    out[0] = mapas
    stats.append(('dialogos', trad, total))

    for sec in range(1, len(eng)):
        orig = eng[sec]
        archivo = ARCHIVOS_SECCION.get(sec)
        if archivo is None:
            continue          # sección sin textos traducibles: nil
        d = dict(dic(archivo))
        d.update(dic(f'{archivo}_{juego}'))   # ajustes solo para este juego (p. ej. nombres_hoenn)
        nombre = rm.SECCIONES.get(sec, str(sec))
        if isinstance(orig, list):
            lista = []
            n = 0
            # Clases de entrenador: la forma femenina u otras variantes van por
            # ID del tipo en bd/_clases_por_id.json (el inglés no distingue género).
            por_id, ids = {}, {}
            if sec == 13:
                por_id = dic('bd/_clases_por_id')
                ids = ids_tipos_entrenador(juego)
            for i, s in enumerate(orig):
                v = (por_id.get(ids.get(i)) or d.get(f'@{i}')
                     or (d.get(s) if isinstance(s, str) and s else None))
                lista.append(v or None)   # nil = el juego usa el inglés
                n += bool(v)
            while lista and lista[-1] is None:   # sin traducir al final: fuera
                lista.pop()
            out[sec] = lista
            stats.append((nombre, n, sum(1 for s in orig if s)))
        else:
            h = rm.OrderedHash()
            for k, v in d.items():
                if not k.startswith('@'):
                    h[k] = v
            out[sec] = h
            presentes = set(orig.keys()) if isinstance(orig, dict) else set()
            stats.append((nombre, len(presentes & set(h)), len(presentes)))

    destino = os.path.join(REPOS, juego, 'Data', 'spanish.dat')
    rm.dump_messages(out, destino)
    print(f'== {juego}: {destino} ({os.path.getsize(destino) / 1e6:.1f} MB)')
    for nombre, n, t in stats:
        if t:
            print(f'   {nombre:20} {n:6}/{t:<6} {100 * n / t:5.1f} %')


if __name__ == '__main__':
    for j in (sys.argv[1:] or JUEGOS):
        generar(j)
