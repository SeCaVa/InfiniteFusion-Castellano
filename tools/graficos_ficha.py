"""Cabecera de la Ficha de Entrenador ("TRAINER CARD" -> "FICHA DE ENTRENADOR").

La cabecera es una letra gruesa de 1x (unos 7x10) dibujada al doble, blanca con
sombra desplazada (2,2). Las letras se sacan del propio "TRAINER CARD"; F, H y O
se dibujan a mano en el mismo estilo. Se borra el texto inglés y el icono de la
derecha (el texto español es más largo) rellenando con el fondo más cercano de la
misma fila, y se escribe el nuevo a partir de la misma x.

Uso: python tools/graficos_ficha.py
"""
import os
from collections import Counter

from PIL import Image

from graficos_fuente import G

ARCHIVOS = ['Pictures/Trainer Card/card.PNG', 'Pictures/Trainer Card/card_f.PNG',
            'Pictures/Trainer Card/card_postgame.PNG', 'Pictures/Trainer Card/card_f_postgame.PNG',
            'Pictures/Trainer Card/overlay.png', 'Pictures/Trainer Card/overlay_postgame.png']
TEXTO = 'FICHA DE ENTRENADOR'
BLANCO = (248, 248, 248, 255)
X0, Y0, X1, Y1 = 58, 34, 272, 58     # texto inglés + icono derecho (en píxeles de la imagen)
EXTRA = {
    'F': ['######', '######', '##....', '##....', '######', '######', '##....', '##....', '##....', '##....'],
    'H': ['##...##', '##...##', '##...##', '##...##', '#######', '#######', '##...##', '##...##', '##...##', '##...##'],
    'O': ['..###..', '.#####.', '##...##', '##...##', '##...##', '##...##', '##...##', '##...##', '.#####.', '..###..'],
}


def fuente(im):
    rows = [[im.getpixel((x, y)) == BLANCO for x in range(X0, X1, 2)] for y in range(Y0, Y0 + 20, 2)]
    cols = [any(r[i] for r in rows) for i in range(len(rows[0]))]
    segs, i = [], 0
    while i < len(cols):
        if cols[i]:
            a = i
            while i < len(cols) and cols[i]:
                i += 1
            segs.append((a, i))
        else:
            i += 1
    f = {}
    for c, (a, b) in zip('TRAINERCARD', segs):
        f.setdefault(c, [''.join('#' if r[x] else '.' for x in range(a, b)) for r in rows])
    f.update(EXTRA)
    return f, segs


def procesar(archivo, f):
    im = Image.open(os.path.join(G, 'en', archivo)).convert('RGBA')
    # paleta del fondo: filas justo encima y debajo del texto
    ref = Counter(im.getpixel((x, y)) for x in range(X0, X1) for y in list(range(Y0 - 6, Y0 - 2)) + [Y1, Y1 + 1])
    ref.pop(BLANCO, None)
    fondo = {p for p, n in ref.most_common(3)}   # los colores de la trama del fondo
    letra = [(x, y) for y in range(Y0, Y0 + 20) for x in range(X0, X1) if im.getpixel((x, y)) == BLANCO]
    sombra = Counter(im.getpixel((x + 2, y + 2)) for x, y in letra
                     if im.getpixel((x + 2, y + 2)) != BLANCO).most_common(1)[0][0]
    fondo.discard(sombra)
    for y in range(Y0 - 4, Y1):
        fila = [im.getpixel((x, y)) for x in range(X0, X1)]
        libres = [i for i, p in enumerate(fila) if p in fondo]
        for i, p in enumerate(fila):
            if p not in fondo and libres:
                j = min(libres, key=lambda k: abs(k - i))
                im.putpixel((X0 + i, y), fila[j])
    puntos, x = [], X0 + 2
    for c in TEXTO:
        if c == ' ':
            x += 8
            continue
        for fy, r in enumerate(f[c]):
            for fx, p in enumerate(r):
                if p == '#':
                    for sx in (0, 1):
                        for sy in (0, 1):
                            puntos.append((x + 2 * fx + sx, Y0 + 2 * fy + sy))
        x += 2 * len(f[c][0]) + 2
    for px, py in puntos:
        im.putpixel((px + 2, py + 2), sombra)
    for q in puntos:
        im.putpixel(q, BLANCO)
    dest = os.path.join(G, 'es', archivo)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    im.save(dest)
    print(f'-> {archivo} (texto hasta x={x})')


def main():
    f, _ = fuente(Image.open(os.path.join(G, 'en', ARCHIVOS[0])).convert('RGBA'))
    for a in ARCHIVOS:
        procesar(a, f)


if __name__ == '__main__':
    main()
