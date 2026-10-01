"""Comprobaciones automáticas de los diccionarios de traduccion/.

- CODIGOS: la traducción debe conservar los mismos códigos de control que el
  inglés ({1}, \\PN, \\v[3], \\c[1], <r>, <br>, \\wt[5], \\1, \\n de Ruby…).
- APERTURA: frases con ! o ? sin ¡ o ¿.
- GENERO: marcas [[x|y]] mal formadas.
- INGLES: traducción idéntica al inglés con dos o más palabras (posible sin traducir).

Informe completo en traduccion/_informes/revision.txt; en consola, el resumen.
Uso: PYTHONIOENCODING=utf-8 python tools/revisar.py [--solo CODIGOS,APERTURA,...]
"""
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(__file__))
from extraer import TRAD, cargar_json

RE_COD = re.compile(
    r'\{\d+(?::[^}]*)?\}'                 # {1} {2:s}
    r'|\\[A-Za-z]+\[[^\]]*\]'             # \v[1] \c[2] \wt[5] \sign[...]
    r'|\\(?:PN|pn|G|g|n|r|l|wtnp|wt|ts|pg|pog|b|op|cl|me|se|f|ff|w|\.|\||!|\^|\\)'
    r'|<[/]?[a-zA-Z]+(?:=[^>]*)?>'        # <r> <br> <icon=...> <c2=...>
    r'|\x01|\n')
# Tablas de nombres donde el nombre oficial puede coincidir con el inglés (Poké Ball…)
NOMBRES = ('bd/especies', 'bd/objetos', 'bd/movimientos', 'bd/habilidades', 'lugares/',
           'entrenadores/nombres')
RE_GEN = re.compile(r'\[\[([^\[\]|]*)\|([^\[\]]*)\]\]')


RE_CH = re.compile(r'\\ch\[([^\]]*)\]')


def codigos(s):
    """Códigos de control; en \\ch[a,b,op1,op2…] (menú de opciones) cuentan
    los dos primeros parámetros y el número de opciones, no su texto."""
    def ch(m):
        partes = m.group(1).split(',')
        return f'\\ch[{partes[0].strip()},{partes[1].strip() if len(partes) > 1 else ""},#{len(partes)}]'
    s = RE_CH.sub(ch, s)
    return Counter(RE_COD.findall(s))


def archivos():
    for dirpath, _, files in os.walk(TRAD):
        if any(p.startswith('_') for p in os.path.relpath(dirpath, TRAD).split(os.sep)):
            continue          # _informes, _revision…
        for fn in sorted(files):
            if fn.endswith('.json') and not fn.startswith('_'):
                ruta = os.path.join(dirpath, fn)
                yield os.path.relpath(ruta, TRAD).replace('\\', '/')[:-5]


def main():
    solo = None
    if '--solo' in sys.argv:
        solo = set(sys.argv[sys.argv.index('--solo') + 1].split(','))
    avisos = []
    total = trad = 0
    for arch in archivos():
        d = cargar_json(arch)
        for en, es in d.items():
            total += 1
            if not es:
                continue
            trad += 1
            es_sin_gen = RE_GEN.sub(lambda m: m.group(1), es)
            if '[[' in es_sin_gen:
                avisos.append(('GENERO', arch, en, es))
            ce, cs = codigos(en), codigos(es_sin_gen)
            # \n de Ruby: el número de saltos puede cambiar al redistribuir líneas
            ce.pop('\n', None)
            cs.pop('\n', None)
            if ce != cs:
                falta = ce - cs
                sobra = cs - ce
                det = ' '.join([f'-{k!r}' for k in falta] + [f'+{k!r}' for k in sobra])
                avisos.append(('CODIGOS', arch, en, es + '   ⟵ ' + det))
            limpio = RE_COD.sub(' ', es_sin_gen)
            for frase in re.findall(r'[^.!?¡¿\n]*[!?]', limpio):
                pass
            if ('!' in limpio and '¡' not in limpio) or ('?' in limpio and '¿' not in limpio):
                avisos.append(('APERTURA', arch, en, es))
            if es == en and len(re.findall(r'[A-Za-z]{2,}', en)) >= 2 and not arch.startswith(NOMBRES):
                avisos.append(('INGLES', arch, en, es))
    if solo:
        avisos = [a for a in avisos if a[0] in solo]
    cuenta = Counter(a[0] for a in avisos)
    with open(os.path.join(TRAD, '_informes', 'revision.txt'), 'w', encoding='utf-8') as f:
        for tipo, arch, en, es in sorted(avisos):
            f.write(f'[{tipo}] {arch}\n  EN: {en!r}\n  ES: {es!r}\n')
    print(f'Traducidas {trad}/{total} ({100 * trad / max(total, 1):.1f} %)')
    for t, n in cuenta.most_common():
        print(f'  {t:9} {n}')
    print('Detalle: traduccion/_informes/revision.txt')


if __name__ == '__main__':
    main()
