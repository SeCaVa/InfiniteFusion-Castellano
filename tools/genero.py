"""Pone marcas de género del jugador [[o|a]] en patrones claros de los diálogos.

Solo actúa en cadenas cuyo inglés se dirige al jugador ("you" o \\PN) y en
patrones inequívocos: "estás/estés/eres listo…", "Bienvenido", "¡Tranquilo!",
"¿Listo para…?" ("¡Listo!" = "Done!" se deja).
Informe de cambios en traduccion/_informes/genero.txt para revisarlos.

Uso: PYTHONIOENCODING=utf-8 python tools/genero.py
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from extraer import TRAD, cargar_json, guardar_json

ADJ = r'(list|preparad|cansad|segur|encantad|convencid|obligad|afortunad|agotad|perdid|equivocad|sol)'
REGLAS = [
    (re.compile(r'\b((?:[Ee]stás|[Ee]stés|[Ee]res|[Ss]eas|[Ee]stabas|[Tt]e ves|[Pp]areces|[Qq]uedas|[Qq]uédate)\s+(?:muy\s+|tan\s+|bastante\s+)?)' + ADJ + r'o\b'),
     lambda m: f'{m.group(1)}{m.group(2)}[[o|a]]'),
    (re.compile(r'\b([Bb]ienvenid)o\b'), lambda m: f'{m.group(1)}[[o|a]]'),
    (re.compile(r'([¡¿]\s*)(Preparad|Tranquil|Segur)o\b'), lambda m: f'{m.group(1)}{m.group(2)}[[o|a]]'),
    # "¡Listo!" suele ser "Done!" (neutro): solo "¿Listo para…?"
    (re.compile(r'([¡¿]\s*)Listo(\s+para)\b'), lambda m: f'{m.group(1)}List[[o|a]]{m.group(2)}'),
]
RE_TU = re.compile(r"\byou\b|\byour\b|\\PN", re.I)
# Vocativos neutros en inglés que la base tradujo en masculino: solo si el inglés los usa
VOCATIVOS = [
    (re.compile(r'\bkid\b', re.I), re.compile(r'(?<=[,¡] )chico\b|(?<=,)chico\b|^[¡]?Chico\b'),
     lambda m: m.group(0)[:-1] + '[[o|a]]'),
    (re.compile(r'\bchamp\b', re.I), re.compile(r'\b([Cc])ampeón\b(?=[!.,?…]| *$)'),
     lambda m: m.group(1) + 'ampe[[ón|ona]]'),
]


def main():
    lineas = []
    for dp, _, fs in os.walk(os.path.join(TRAD, 'dialogos')):
        for fn in sorted(fs):
            if not fn.endswith('.json') or fn.startswith('_'):
                continue
            arch = os.path.relpath(os.path.join(dp, fn), TRAD).replace('\\', '/')[:-5]
            d = cargar_json(arch)
            cambio = False
            for en, es in d.items():
                if not es or not RE_TU.search(en):
                    continue
                nuevo = es
                for rx, f in REGLAS:
                    nuevo = rx.sub(f, nuevo)
                for rx_en, rx_es, f in VOCATIVOS:
                    if rx_en.search(en):
                        nuevo = rx_es.sub(f, nuevo)
                if nuevo != es:
                    d[en] = nuevo
                    cambio = True
                    lineas.append(f'{arch}\n  EN: {en}\n  ANTES: {es}\n  AHORA: {nuevo}')
            if cambio:
                guardar_json(arch, d)
    with open(os.path.join(TRAD, '_informes', 'genero.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lineas) + '\n')
    print(f'{len(lineas)} cadenas con marcas de género (traduccion/_informes/genero.txt)')


if __name__ == '__main__':
    main()
