"""Botones con texto (rejilla de botones; columna 0 normal, columna 1 seleccionado).

Ejemplo: Battle/cursor_command.png (2 columnas x 10 filas de 130x46).
  - Letras: fuente de 5x9 dibujada al doble. Se saca del texto inglés de los
    botones normales (las letras se cuentan desde la derecha: a la izquierda está
    el icono) y se reduce a 1x; las que faltan se definen a mano en EXTRA.
  - Borrado: solo los píxeles del texto original (letra + sombra o contorno); cada
    hueco se rellena interpolando en horizontal entre los píxeles de fondo vecinos,
    así se conservan degradados y dibujos del botón.
  - Dibujo: botón normal = color del texto + sombra (+1,+1) con los colores del
    original; seleccionado = texto claro + contorno oscuro. Se centra entre el
    icono y el borde; si no cabe, se junta el espacio entre letras.

Uso: python tools/graficos_botones.py
"""
import os
from collections import Counter

from PIL import Image

from graficos_fuente import G

EXTRA = {   # 1x, 9 filas
    'S': ['.###.', '#...#', '#....', '#....', '.###.', '....#', '....#', '#...#', '.###.'],
    'Á': ['.###.', '#...#', '#...#', '#...#', '#####', '#...#', '#...#', '#...#', '#...#'],
}
TILDE = ['...#.', '..#..']   # dos filas por encima de la letra

TRABAJOS = [
    {
        'archivo': 'Pictures/Battle/cursor_command.png',
        'celda': (130, 46),
        'en': ['FIGHT', 'POKéMON', 'BAG', 'RUN', 'CALL', 'BALL', 'ROCK', 'BAIT', 'BALL', 'CANCEL'],
        'es': ['LUCHAR', 'POKéMON', 'MOCHILA', 'HUIR', 'LLAMAR', 'BALL', 'ROCA', 'CEBO', 'BALL', 'ATRÁS'],
        # fin del icono de cada fila (columna x desde la que puede ir el texto)
        'icono': [50, 36, 50, 48, 48, 36, 52, 40, 48, 38],
    },
]
# Versión oscura: el texto de los botones normales es claro
TRABAJOS.append(dict(TRABAJOS[0], archivo='Pictures/Battle/cursor_command_dark.png', claro=True))


def oscuro(p):
    return p[3] > 0 and sum(p[:3]) < 200


def glifos_derecha(cols, n):
    grupos, x = [], len(cols) - 1
    while x >= 0 and len(grupos) < n:
        if cols[x]:
            fin = x
            while x >= 0 and cols[x]:
                x -= 1
            grupos.append((x + 1, fin + 1))
        else:
            x -= 1
    grupos.reverse()
    return grupos


def claro(p):
    return p[3] > 0 and sum(p[:3]) > 600


def fuente_de(im, t):
    """{letra: filas a 1x}, y para cada fila la caja del texto original."""
    cw, ch = t['celda']
    f, cajas = {}, {}
    es_letra = claro if t.get('claro') else oscuro
    for fila, palabra in enumerate(t['en']):
        y0 = fila * ch
        m = [[es_letra(im.getpixel((x, y0 + y))) and 6 <= x < cw - 6 and 6 <= y < ch - 6
              for x in range(cw)] for y in range(ch)]
        cols = [any(m[y][x] for y in range(ch)) for x in range(cw)]
        letras = [c for c in palabra if c != ' ']
        gr = glifos_derecha(cols, len(letras))
        if len(gr) != len(letras):
            continue
        filas_t = [y for y in range(ch) if any(m[y][x] for x in range(gr[0][0], gr[-1][1]))]
        top, bot = filas_t[0], filas_t[-1] + 1
        cajas[fila] = (gr[0][0], top, gr[-1][1], bot)
        for c, (a, b) in zip(letras, gr):
            if c in f:
                continue
            f[c] = [''.join('#' if m[y][x] else '.' for x in range(a, b, 2)) for y in range(top, bot, 2)]
    f.update(EXTRA)
    return f, cajas


def colores_texto(im, x0, y0, caja, texto_claro):
    """(color de la letra, color de sombra/contorno) a partir del original."""
    a, top, b, bot = caja
    pix = Counter(im.getpixel((x0 + x, y0 + y)) for y in range(top - 2, bot + 3) for x in range(a - 2, b + 3))
    letra_mask = set()
    for y in range(top, bot):
        for x in range(a, b):
            p = im.getpixel((x0 + x, y0 + y))
            if (sum(p[:3]) > 600) if texto_claro else oscuro(p):
                letra_mask.add((x, y))
    letra = Counter(im.getpixel((x0 + x, y0 + y)) for x, y in letra_mask).most_common(1)[0][0]
    anillo = Counter()
    for x, y in letra_mask:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if (x + dx, y + dy) not in letra_mask:
                    anillo[im.getpixel((x0 + x + dx, y0 + y + dy))] += 1
    segundo = anillo.most_common(1)[0][0]
    return letra, segundo


def borrar(im, x0, y0, caja, colores):
    a, top, b, bot = caja
    for y in range(y0 + top - 2, y0 + bot + 3):
        fila = [im.getpixel((x, y)) for x in range(x0 + a - 3, x0 + b + 4)]
        hueco = [p in colores for p in fila]
        x = 0
        while x < len(fila):
            if hueco[x]:
                ini = x
                while x < len(fila) and hueco[x]:
                    x += 1
                izq = fila[ini - 1] if ini > 0 else fila[x] if x < len(fila) else fila[ini]
                der = fila[x] if x < len(fila) else izq
                n = x - ini + 1
                for k in range(ini, x):
                    t = (k - ini + 1) / n
                    c = tuple(round(izq[i] * (1 - t) + der[i] * t) for i in range(4))
                    im.putpixel((x0 + a - 3 + k, y), c)
            else:
                x += 1


def dibujar(im, x0, y0, texto, f, izq, der, top, letra, segundo, seleccionado):
    for sep in (2, 1, 0):
        total = sum(2 * len(f[c][0]) for c in texto) + sep * (len(texto) - 1)
        if total <= der - izq:
            break
    x = izq + (der - izq - total) // 2
    puntos = []
    for c in texto:
        g = f[c]
        filas = ([r.ljust(len(g[0]), '.')[:len(g[0])] for r in TILDE] if c in 'ÁÉÍÓÚ' else []) + g
        desp = -len(TILDE) if c in 'ÁÉÍÓÚ' else 0
        for fy, r in enumerate(filas):
            for fx, p in enumerate(r):
                if p == '#':
                    for sx in (0, 1):
                        for sy in (0, 1):
                            puntos.append((x0 + x + 2 * fx + sx, y0 + top + 2 * (fy + desp) + sy))
        x += 2 * len(g[0]) + sep
    pset = set(puntos)
    if seleccionado:
        for px, py in puntos:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if (px + dx, py + dy) not in pset:
                        im.putpixel((px + dx, py + dy), segundo)
    else:
        for px, py in puntos:
            if (px + 1, py + 1) not in pset:
                im.putpixel((px + 1, py + 1), segundo)
    for q in puntos:
        im.putpixel(q, letra)


def main():
    previo = None
    for t in TRABAJOS:
        im = Image.open(os.path.join(G, 'en', t['archivo'])).convert('RGBA')
        if t.get('claro'):   # misma fuente y posiciones que la versión clara
            f, cajas = previo
        else:
            f, cajas = previo = fuente_de(im, t)
        faltan = sorted({c for p in t['es'] for c in p if c not in f and c not in 'ÁÉÍÓÚ'})
        if faltan:
            raise SystemExit(f'{t["archivo"]}: faltan letras {faltan}')
        cw, ch = t['celda']
        for fila, es in enumerate(t['es']):
            if es == t['en'][fila]:
                continue
            caja = cajas[fila]
            for col in (0, 1):
                x0, y0 = col * cw, fila * ch
                letra, segundo = colores_texto(im, x0, y0, caja, col == 1 or t.get('claro'))
                borrar(im, x0, y0, caja, {letra, segundo})
                dibujar(im, x0, y0, es, f, t['icono'][fila], cw - 12, caja[1], letra, segundo, col == 1)
        dest = os.path.join(G, 'es', t['archivo'])
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        im.save(dest)
        print('->', dest)


if __name__ == '__main__':
    main()
