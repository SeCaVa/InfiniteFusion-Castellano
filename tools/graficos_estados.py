"""Iconos de estado en castellano (DOR, ENV, QUE, PAR, CON, DEB).

Imágenes de 44 px de ancho con una etiqueta por cada 16 px de alto; letra blanca
al doble con sombra. Las letras se sacan de las versiones inglesa y francesa del
juego (máscara blanca reducida a 1x); las que faltan van en EXTRA (dibujadas a
mano en el mismo estilo). El texto se borra rellenando con el color de fondo de
cada fila y se vuelve a dibujar centrado con los colores del original.

Uso: python tools/graficos_estados.py [--fuentes]
"""
import os
import sys
from collections import Counter

from PIL import Image

from graficos_fuente import G

ES = {'SLP': 'DOR', 'PSN': 'ENV', 'BRN': 'QUE', 'PAR': 'PAR', 'FRZ': 'CON', 'FNT': 'DEB', 'PKRS': 'PKRS'}
IMAGENES = {
    'Pictures/Battle/icon_statuses.png': (['SLP', 'PSN', 'BRN', 'PAR', 'FRZ', 'PSN'],
                                          ['SOM', 'PSN', 'BRU', 'PAR', 'GEL', 'PSN'], 'bloque'),
    'Pictures/battleStatuses.png': (['SLP', 'PSN', 'BRN', 'PAR', 'FRZ'],
                                    ['SOM', 'PSN', 'BRU', 'PAR', 'GEL'], 'bloque'),
    'Pictures/statuses.PNG': (['SLP', 'PSN', 'BRN', 'PAR', 'FRZ', 'FNT', 'PKRS'],
                              ['SOM', 'PSN', 'BRU', 'PAR', 'GEL', 'KO', 'PKRS'], 'fina'),
}
EXTRA = {
    'bloque': {
        'D': ['####.', '#...#', '#...#', '#...#', '#...#', '#####'],
        'V': ['#...#', '#...#', '#...#', '##.##', '.###.', '..#..'],
        'E': ['#####', '#....', '####.', '#....', '#....', '#####'],
        'Q': ['#####', '#...#', '#...#', '#...#', '#..##', '####.'],
        'C': ['#####', '#....', '#....', '#....', '#....', '#####'],
    },
    'fina': {
        'C': ['.###', '#...', '#...', '#...', '#...', '.###'],
        'D': ['###.', '#..#', '#..#', '#..#', '#..#', '###.'],
        'Q': ['.##.', '#..#', '#..#', '#..#', '#.#.', '.#.#'],
        'V': ['#..#', '#..#', '#..#', '#..#', '.##.', '.##.'],
        'O': ['.##.', '#..#', '#..#', '#..#', '#..#', '.##.'],
    },
}


def color_letra(im, y0, h=16, w=44):
    """El color claro más frecuente del interior (la letra; en TOX no es blanca)."""
    c = Counter(im.getpixel((x, y0 + y)) for y in range(2, h - 2) for x in range(4, w - 4))
    return max((p for p, n in c.items() if n >= 10 and p[3] > 0), key=lambda p: sum(p[:3]))


def glifos(im, y0, h=16, w=44):
    letra = color_letra(im, y0, h, w)
    filas = [[im.getpixel((x, y0 + y)) == letra and 2 <= x < w - 2 and 2 <= y < h - 2
              for x in range(0, w, 2)] for y in range(0, h, 2)]
    cols = [any(r[x] for r in filas) for x in range(len(filas[0]))]
    gr, x = [], 0
    while x < len(cols):
        if cols[x]:
            a = x
            while x < len(cols) and cols[x]:
                x += 1
            gr.append((a, x))
        else:
            x += 1
    ys = [y for y, r in enumerate(filas) if any(r)]
    if not ys:
        return [], 0
    return [[''.join('#' if filas[y][x] else '.' for x in range(a, b)) for y in range(ys[0], ys[-1] + 1)]
            for a, b in gr], ys[0]


def fuentes():
    f = {'bloque': {}, 'fina': {}}
    for archivo, (en, fr, estilo) in IMAGENES.items():
        for lengua, textos in (('en', en), ('fr', fr)):
            ruta = os.path.join(G, lengua, archivo)
            if not os.path.exists(ruta):
                continue
            im = Image.open(ruta).convert('RGBA')
            for i, t in enumerate(textos):
                gl, _ = glifos(im, i * 16)
                if len(gl) == len(t):
                    for c, g in zip(t, gl):
                        f[estilo].setdefault(c, g)
    for estilo in f:
        f[estilo].update(EXTRA[estilo])   # las dibujadas a mano mandan
    return f


def rehacer(im, y0, texto, g_fuente, h=16, w=44):
    _, fila0 = glifos(im, y0)
    caja = [(x, y) for y in range(y0 + 2, y0 + h - 2) for x in range(2, w - 2)]
    fondo = im.getpixel((2, y0 + h // 2))   # junto al borde izquierdo siempre es fondo
    letra = color_letra(im, y0, h, w)
    # sombra: el color que hay 2 px abajo a la derecha de las letras
    letras = {p for p in caja if im.getpixel(p) == letra}
    otros = Counter(im.getpixel((x + 2, y + 2)) for x, y in letras
                    if (x + 2, y + 2) not in letras and (x + 2, y + 2) in set(caja))
    sombra = otros.most_common(1)[0][0] if otros else fondo
    for x, y in caja:
        if im.getpixel((x, y)) in (letra, sombra):
            im.putpixel((x, y), fondo)
    anchos = [len(g_fuente[c][0]) for c in texto]
    total = (sum(anchos) + len(texto) - 1) * 2 + 2
    x = (w - total) // 2
    puntos = []
    for c in texto:
        for fy, r in enumerate(g_fuente[c]):
            for fx, p in enumerate(r):
                if p == '#':
                    for sx in (0, 1):
                        for sy in (0, 1):
                            puntos.append((x + 2 * fx + sx, y0 + 2 * (fila0 + fy) + sy))
        x += (len(g_fuente[c][0]) + 1) * 2
    pset = set(puntos)
    for px, py in puntos:
        for d in ((2, 0), (0, 2), (2, 2)):   # sombra del original
            q = (px + d[0], py + d[1])
            if q not in pset and 0 <= q[0] < w:
                im.putpixel(q, sombra)
    for q in puntos:
        im.putpixel(q, letra)


def main():
    f = fuentes()
    if '--fuentes' in sys.argv:
        for estilo, d in f.items():
            print('==', estilo, ''.join(sorted(d)))
            for c in sorted(d):
                print(c, ' '.join(d[c]))
        return
    for archivo, (en, fr, estilo) in IMAGENES.items():
        im = Image.open(os.path.join(G, 'en', archivo)).convert('RGBA')
        for i, t in enumerate(en):
            if ES[t] != t:
                rehacer(im, i * 16, ES[t], f[estilo])
        dest = os.path.join(G, 'es', archivo)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        im.save(dest)
        print('->', dest)


if __name__ == '__main__':
    main()
