"""Revisión por lotes de la traducción importada de la base, con ayuda de un modelo.

  lotes [N]                 crea traduccion/_revision/lotes/NNN.json (N pares por lote, 80 por defecto)
                            con las cadenas importadas de la base (_informes/base_importada.json)
                            aún no revisadas; cada par lleva en "terminos" los nombres oficiales
                            de lo que menciona el inglés.
  importar LOTE RESP.jsonl  guarda las propuestas del modelo ({"id", "tipo", "motivo", "es"})
                            en traduccion/_revision/propuestas.json, sin aplicarlas.
  aplicar [--todas] [--forzar]  aplica las propuestas (todas o las "ok": true) si conservan
                            los códigos del inglés; --forzar también si la traducción cambió
                            después de generar el lote (p. ej. por sustituir.py).

Las propuestas se revisan a mano antes de aplicarlas: el modelo puede equivocarse.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from extraer import TRAD, cargar_json, guardar_json
from revisar import codigos, RE_GEN

REV = os.path.join(TRAD, '_revision')
LOTES = os.path.join(REV, 'lotes')
PROP = os.path.join(REV, 'propuestas.json')
REVISADAS = os.path.join(REV, 'revisadas.json')      # {archivo|en: lote} ya revisadas


def terminos_oficiales():
    """Patrón y tabla {inglés: castellano} de nombres oficiales para dar pistas al modelo."""
    import re
    from terminos import TABLAS, IGNORAR
    t = {}
    for tabla in TABLAS:
        for en, es in cargar_json(tabla).items():
            if es and en != es and len(en) >= 4 and en not in IGNORAR:
                t.setdefault(en, es)
    rx = re.compile(r'(?<![\w])(' + '|'.join(re.escape(k) for k in sorted(t, key=len, reverse=True)) + r')(?![\w])')
    return rx, t


def lotes(n=80):
    os.makedirs(LOTES, exist_ok=True)
    imp = cargar_json(os.path.join(TRAD, '_informes', 'base_importada.json'))
    hechas = cargar_json(REVISADAS)
    rx, tabla = terminos_oficiales()
    filas = []
    for archivo in sorted(imp):
        # Los nombres y descripciones oficiales (bd/, lugares/) no se revisan con IA:
        # el modelo "corrige" de memoria nombres que ya son oficiales.
        if archivo.startswith(('bd/', 'lugares/')):
            continue
        d = cargar_json(archivo)
        for en in imp[archivo]:
            if d.get(en) and f'{archivo}|{en}' not in hechas:
                fila = {'archivo': archivo, 'en': en, 'es': d[en]}
                pistas = {m.group(1): tabla[m.group(1)] for m in rx.finditer(en)}
                if pistas:
                    fila['terminos'] = pistas
                filas.append(fila)
    num = 0
    for i in range(0, len(filas), n):
        lote = [dict(id=j, **f) for j, f in enumerate(filas[i:i + n])]
        guardar_json(os.path.join(LOTES, f'{num:03d}.json'), lote)
        num += 1
    print(f'{len(filas)} cadenas en {num} lotes ({LOTES})')


def importar(lote, resp):
    filas = {f['id']: f for f in json.load(open(os.path.join(LOTES, f'{int(lote):03d}.json'), encoding='utf-8'))}
    prop = cargar_json(PROP)
    n = 0
    for linea in open(resp, encoding='utf-8'):
        linea = linea.strip()
        if not linea.startswith('{'):
            continue
        p = json.loads(linea)
        f = filas.get(p['id'])
        if not f:
            continue
        clave = f"{f['archivo']}|{f['en']}"
        prop[clave] = {'archivo': f['archivo'], 'en': f['en'], 'actual': f['es'],
                       'propuesta': p['es'], 'tipo': p.get('tipo', ''), 'motivo': p.get('motivo', ''),
                       'lote': int(lote), 'ok': None}
        n += 1
    guardar_json(PROP, prop)
    hechas = cargar_json(REVISADAS)
    for f in filas.values():
        hechas[f"{f['archivo']}|{f['en']}"] = int(lote)
    guardar_json(REVISADAS, hechas)
    print(f'{n} propuestas guardadas del lote {lote}; {len(filas)} cadenas marcadas como revisadas')


def aplicar(todas=False, forzar=False):
    prop = cargar_json(PROP)
    cambios = {}
    n = rech = 0
    for clave, p in prop.items():
        if p.get('aplicada') or not (todas or p.get('ok')):
            continue
        ce = codigos(p['en'])
        cs = codigos(RE_GEN.sub(lambda m: m.group(1), p['propuesta']))
        ce.pop('\n', None)
        cs.pop('\n', None)
        if ce != cs:
            rech += 1
            print('RECHAZADA (códigos):', p['archivo'], p['en'][:60])
            continue
        cambios.setdefault(p['archivo'], []).append(p)
    for archivo, ps in cambios.items():
        d = cargar_json(archivo)
        for p in ps:
            if d.get(p['en']) == p['actual'] or (forzar and p['en'] in d):
                d[p['en']] = p['propuesta']
                p['aplicada'] = True
                n += 1
        guardar_json(archivo, d)
    guardar_json(PROP, prop)
    print(f'{n} aplicadas, {rech} rechazadas por códigos')


if __name__ == '__main__':
    orden = sys.argv[1] if len(sys.argv) > 1 else ''
    if orden == 'lotes':
        lotes(int(sys.argv[2]) if len(sys.argv) > 2 else 80)
    elif orden == 'importar':
        importar(sys.argv[2], sys.argv[3])
    elif orden == 'aplicar':
        aplicar('--todas' in sys.argv, '--forzar' in sys.argv)
    else:
        print(__doc__)
