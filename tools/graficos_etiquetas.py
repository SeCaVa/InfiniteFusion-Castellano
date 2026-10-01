"""Etiquetas de tipo en castellano:
  Graphics/Localized/es/Pictures/types.png          (64x28, más filas de fusiones triples)
  Graphics/Localized/es/Pictures/Pokedex/icon_types.png  (96x32, búsqueda de la Pokédex)

Parte de la imagen inglesa: en cada etiqueta borra el texto (blanco y su sombra)
con el color de fondo y escribe el nombre español con la fuente de píxeles de esa
misma imagen (tools/graficos_fuente.py) al doble y con la misma sombra.
Nombres: las abreviaturas oficiales de Rubí (España), + HADA.

Uso: python tools/graficos_etiquetas.py
"""
import os
from collections import Counter

from PIL import Image

from graficos_fuente import G, ORIGEN, DESTINO, BLANCO, extraer

ACENTO = {'É': 'E', 'Í': 'I', 'Ó': 'O', 'Á': 'A', 'Ú': 'U'}
TIPOS = ['NORMAL', 'LUCHA', 'VOLAD.', 'VENENO', 'TIERRA', 'ROCA', 'BICHO', 'FANT.', 'ACERO', '???',
         'FUEGO', 'AGUA', 'PLANTA', 'ELÉCT.', 'PSÍQ.', 'HIELO', 'DRAGÓN', 'SINIE.', 'HADA']


def vacio(ancho, alto):
    return ['.' * ancho] * alto


TRABAJOS = [
    {   # letra de 4x7 (filas 3-9); acentos en las filas 1-2
        'archivo': 'Pictures/types.png', 'ancho': 64, 'alto': 28, 'filas_tilde': (1, 2), 'margen': 2, 'borde': (2, 3, -4, -3),
        'extra': {
            'V': vacio(4, 3) + ['#..#', '#..#', '#..#', '#..#', '#..#', '.##.', '.##.'] + vacio(4, 4),
            'Q': vacio(4, 3) + ['.##.', '#..#', '#..#', '#..#', '#.##', '#..#', '.###'] + vacio(4, 4),
            '.': ['.'] * 9 + ['#'] + ['.'] * 4,
        },
    },
    {   # letra de 6x9 (filas 3-11); el borde ocupa las filas 0-1: tilde de una fila
        'archivo': 'Pictures/Pokedex/icon_types.png', 'ancho': 96, 'alto': 32, 'filas_tilde': (2,), 'borde': (4, 5, -6, -5),
        'extra': {
            'Q': vacio(6, 3) + ['.####.', '######', '##..##', '##..##', '##..##', '##.###', '##..##',
                                '######', '.#####'] + vacio(6, 4),
            '.': ['..'] * 10 + ['##', '##'] + ['..'] * 4,
        },
    },
]


def fuente(t):
    f = extraer(t['archivo'], t['alto'], t.get('margen', 4))
    f.update(t['extra'])
    for acentuada, base in ACENTO.items():
        if base not in f:
            continue
        g = [list(r) for r in f[base]]
        w = len(g[0])
        x = min(w // 2 + 1, w - 1)   # tilde inclinada hacia la derecha
        filas = t['filas_tilde']
        for k, fy in enumerate(filas):
            for dx in range(max(1, w // 4)):
                g[fy][max(0, min(w - 1, x - k + dx - (len(filas) - 1)))] = '#'
        f[acentuada] = [''.join(r) for r in g]
    return f


def medir(texto, f, sep=1):
    return sum(len(f[c][0]) for c in texto) + sep * (len(texto) - 1)


def escribir(im, texto, x0, y0, f, color, sombra, escala=2, sep=1, desp=2):
    """Dibuja el texto (esquina superior izquierda de la fila 0 de la fuente en x0,y0)."""
    for col, d in ((sombra, desp), (color, 0)):
        x = x0
        for c in texto:
            g = f[c]
            for fy, fila in enumerate(g):
                for fx, p in enumerate(fila):
                    if p == '#':
                        for sy in range(escala):
                            for sx in range(escala):
                                im.putpixel((x + fx * escala + sx + d, y0 + fy * escala + sy + d), col)
            x += (len(g[0]) + sep) * escala


def etiqueta(im, y0, texto, f, w, h, borde):
    # fondo: color más frecuente (no blanco) en los bordes izquierdo y derecho del interior
    bordes = [im.getpixel((x, y)) for y in range(y0 + 6, y0 + h - 6) for x in borde]
    fondo = Counter(p for p in bordes if p[:3] != BLANCO).most_common(1)[0][0]
    letras = [(x, y) for y in range(y0 + 4, y0 + h - 4) for x in range(2, w - 2)
              if im.getpixel((x, y))[:3] == BLANCO]
    xs = [x for x, _ in letras]
    ys = [y for _, y in letras]
    zona = [im.getpixel((x, y)) for y in range(min(ys), max(ys) + 3) for x in range(min(xs), max(xs) + 3)]
    sombra = Counter(p for p in zona if p != fondo and p[:3] != BLANCO).most_common(1)[0][0]
    for y in range(min(ys), max(ys) + 3):
        for x in range(min(xs), max(xs) + 3):
            p = im.getpixel((x, y))
            if p[:3] == BLANCO or p == sombra:
                im.putpixel((x, y), fondo)
    ancho = medir(texto, f) * 2 + 2
    escribir(im, texto, (w - ancho) // 2, y0, f, BLANCO + (255,), sombra)


# Filas con varios tipos (fusiones triples, solo en types.png), letra a 1x: de más larga a más corta
CORTOS = {
    '???': ['???'], 'ICE': ['HIELO', 'HIEL', 'HIE'], 'FIRE': ['FUEGO', 'FUEG', 'FUE'],
    'ELEC': ['ELECT', 'ELEC', 'ELE'], 'WATER': ['AGUA', 'AGU'], 'WAT': ['AGUA', 'AGU'],
    'GROU': ['TIERRA', 'TIER', 'TIE'], 'FLY': ['VOLAD', 'VOLA', 'VOL'], 'GHO': ['FANT', 'FAN'],
    'STEEL': ['ACERO', 'ACER', 'ACE'], 'GRAS': ['PLANTA', 'PLAN', 'PLA'], 'GRASS': ['PLANTA', 'PLAN', 'PLA'],
    'BUG': ['BICHO', 'BICH', 'BIC'], 'PSY': ['PSIQ', 'PSI'], 'ROCK': ['ROCA', 'ROC'],
}
MULTI = [['???', '???'], ['ICE', 'FIRE', 'ELEC'], ['FIRE', 'WATER', 'ELEC'], ['WATER', 'GROU', 'FLY'],
         ['GHO', 'STEEL', 'WAT'], ['FIRE', 'WATER', 'GRAS'], ['GRASS', 'STEEL'], ['BUG', 'STEEL', 'PSY'],
         ['ICE', 'ROCK', 'STEEL']]


def segmentos(im, y, w=64):
    """Tramos [x0, x1) de color de fondo distinto en la fila y."""
    tr, x0 = [], 0
    for x in range(1, w + 1):
        if x == w or im.getpixel((x, y)) != im.getpixel((x - 1, y)):
            if x - x0 >= 6:
                tr.append([x0, x])
            x0 = x
    return tr


def etiqueta_multiple(im, y0, nombres, f, w=64, h=28):
    tr = segmentos(im, y0 + 6)
    if len(tr) != len(nombres):
        tr = [[0, w // 2], [w // 2, w]] if len(nombres) == 2 else tr   # "??? ???": un solo fondo
    if tr:
        tr[0][0], tr[-1][1] = 0, w
    for (a, b), n in zip(tr, nombres):
        fondo = im.getpixel(((a + b) // 2, y0 + 6))
        zona = [im.getpixel((x, y)) for y in range(y0 + 8, y0 + 20) for x in range(a, b)]
        otros = Counter(p for p in zona if p != fondo and p[:3] != BLANCO)
        sombra = otros.most_common(1)[0][0] if otros else (128, 120, 112, 255)
        for y in range(y0 + 6, y0 + h - 5):
            for x in range(a, b):
                p = im.getpixel((x, y))
                if p[:3] == BLANCO or p == sombra:
                    im.putpixel((x, y), fondo)
        ancho_libre = (b - a) - 2
        texto = next((t for t in CORTOS[n] if medir(t, f) + 1 <= ancho_libre), CORTOS[n][-1])
        x0 = a + (b - a - medir(texto, f) - 1) // 2
        escribir(im, texto, x0, y0 + 7, f, BLANCO + (255,), sombra, escala=1, desp=1)


def main():
    for t in TRABAJOS:
        f = fuente(t)
        faltan = sorted({c for p in TIPOS for c in p if c not in f})
        if faltan:
            raise SystemExit(f'{t["archivo"]}: faltan letras {faltan}')
        src = os.path.join(G, ORIGEN, t['archivo'])
        if not os.path.exists(src):
            continue
        im = Image.open(src).convert('RGBA')
        for i, nombre in enumerate(TIPOS):
            w = t['ancho']
            etiqueta(im, i * t['alto'], nombre, f, w, t['alto'], [x if x >= 0 else w + x for x in t['borde']])
        if t['archivo'] == 'Pictures/types.png':
            for k, nombres in enumerate(MULTI):
                etiqueta_multiple(im, (len(TIPOS) + k) * 28, nombres, f)
        dest = os.path.join(G, DESTINO, t['archivo'])
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        im.save(dest)
        print('->', dest)


if __name__ == '__main__':
    main()
