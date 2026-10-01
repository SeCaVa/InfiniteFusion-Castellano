"""Lotes de cadenas SIN traducir para que un modelo proponga una traducción.

  python tools/traducir_ia.py lotes DICCIONARIO [N]
      Crea traduccion/_traduccion_ia/<dicc>/NNN.json con listas {id, en, terminos}
      de las cadenas vacías del diccionario (p. ej. entrenadores/frases).
      Si DICCIONARIO es una carpeta (p. ej. dialogos/hoenn), junta sus archivos
      en orden sin partir un mapa entre lotes salvo que no quepa; cada elemento
      lleva entonces "dicc" con su archivo.
  python tools/traducir_ia.py importar DICCIONARIO LOTE RESP.jsonl
      Lee las líneas {"id", "es"} ya verificadas y las escribe en el diccionario,
      solo si los códigos de control coinciden con el inglés.

Las propuestas se revisan a mano antes de importarlas.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from extraer import TRAD, cargar_json, guardar_json
from revision_ia import terminos_oficiales
from revisar import codigos


def carpeta(dicc):
    return os.path.join(TRAD, '_traduccion_ia', dicc.replace('/', '_'))


def pendientes_por_archivo(dicc):
    """[(archivo, [cadenas vacías])] del diccionario o de cada archivo de la carpeta."""
    ruta = os.path.join(TRAD, dicc)
    if not os.path.isdir(ruta):
        return [(None, [k for k, v in cargar_json(dicc).items() if not v])]
    res = []
    for f in sorted(os.listdir(ruta)):
        if f.endswith('.json'):
            sub = f'{dicc}/{f[:-5]}'
            vacias = [k for k, v in cargar_json(sub).items() if not v]
            if vacias:
                res.append((sub, vacias))
    return res


def lotes(dicc, n=150):
    grupos = []  # cada lote: [(archivo, cadena)]
    for sub, vacias in pendientes_por_archivo(dicc):
        trozos = [vacias[b:b + n] for b in range(0, len(vacias), n)]
        for t in trozos:
            if grupos and len(grupos[-1]) + len(t) <= n:
                grupos[-1] += [(sub, en) for en in t]
            else:
                grupos.append([(sub, en) for en in t])
    rx, tabla = terminos_oficiales()
    dest = carpeta(dicc)
    os.makedirs(dest, exist_ok=True)
    for f in os.listdir(dest):
        if f.endswith('.json'):
            os.remove(os.path.join(dest, f))
    for b, grupo in enumerate(grupos):
        lote = []
        for i, (sub, en) in enumerate(grupo):
            e = {'id': i, 'en': en}
            if sub:
                e['dicc'] = sub
            t = {m.group(1): tabla[m.group(1)] for m in rx.finditer(en)}
            if t:
                e['terminos'] = t
            lote.append(e)
        with open(os.path.join(dest, f'{b:03d}.json'), 'w', encoding='utf-8') as f:
            json.dump(lote, f, ensure_ascii=False, indent=1)
    total = sum(len(g) for g in grupos)
    print(f'{total} cadenas en {len(grupos)} lotes → {dest}')


def importar(dicc, lote, resp):
    datos = json.load(open(os.path.join(carpeta(dicc), f'{int(lote):03d}.json'), encoding='utf-8'))
    por_id = {e['id']: e['en'] for e in datos}
    destino = {e['id']: e.get('dicc', dicc) for e in datos}
    dics = {}
    ok = mal = 0
    for linea in open(resp, encoding='utf-8'):
        if not linea.strip():
            continue
        p = json.loads(linea)
        en = por_id[p['id']]
        if codigos(en) != codigos(p['es']):
            print('CODIGOS', repr(en), '→', repr(p['es']))
            mal += 1
            continue
        sub = destino[p['id']]
        if sub not in dics:
            dics[sub] = cargar_json(sub)
        dics[sub][en] = p['es']
        ok += 1
    for sub, d in dics.items():
        guardar_json(sub, d)
    print(f'{ok} importadas, {mal} rechazadas por códigos')


if __name__ == '__main__':
    if sys.argv[1] == 'lotes':
        lotes(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 150)
    elif sys.argv[1] == 'importar':
        importar(sys.argv[2], sys.argv[3], sys.argv[4])
