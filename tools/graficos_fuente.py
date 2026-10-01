"""Fuentes de píxeles de las etiquetas de tipo, extraídas de las versiones inglesa
y francesa del propio juego: cada letra es un mapa de bits a 1x (el juego la
dibuja al doble, en blanco y con una sombra gris desplazada 2 px).

  extraer(archivo, alto) -> {letra: [filas '#.']} (filas desde el borde superior
  de la etiqueta, a 1x). Las letras que no aparecen se definen en cada script.
"""
import os
from PIL import Image

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
G = os.path.join(RAIZ, 'traduccion', 'graficos')
BLANCO = (248, 248, 248)
# Carpeta de originales y de resultado (por defecto 'en' -> 'es'; para los que en
# Kanto son distintos: GRAFICOS_ORIGEN=en_kanto GRAFICOS_DESTINO=es_kanto)
ORIGEN = os.environ.get('GRAFICOS_ORIGEN', 'en')
DESTINO = os.environ.get('GRAFICOS_DESTINO', 'es')

ETIQUETAS = {
    'en': ['NORMAL', 'FIGHT', 'FLYING', 'POISON', 'GROUND', 'ROCK', 'BUG', 'GHOST', 'STEEL', '???',
           'FIRE', 'WATER', 'GRASS', 'ELECTR', 'PSYCHC', 'ICE', 'DRAGON', 'DARK', 'FAIRY'],
    'fr': ['NORMAL', 'COMBAT', 'VOL', 'POISON', 'SOL', 'ROCHE', 'INSECT', 'SPECTR', 'ACIER', '???',
           'FEU', 'EAU', 'PLANTE', 'ELECTR', 'PSY', 'GLACE', 'DRAGON', 'TENEBR', 'FEE'],
}


def es_letra(p):
    return p[3] > 0 and sum(p[:3]) > 700


def glifos_de(im, y0, alto, margen=4):
    w = im.width
    filas = [[es_letra(im.getpixel((x, y))) and margen <= x < w - margen and y0 + 4 <= y < y0 + alto - 4
              for x in range(0, w, 2)] for y in range(y0, y0 + alto, 2)]
    cols = list(zip(*filas))
    glifos, actual = [], []
    for c in cols:
        if not any(c):
            if actual:
                glifos.append(actual)
                actual = []
        else:
            actual.append(c)
    if actual:
        glifos.append(actual)
    return [[''.join('#' if col[y] else '.' for col in g) for y in range(len(g[0]))] for g in glifos]


def extraer(archivo='Pictures/types.png', alto=28, margen=4):
    fuente = {}
    for lengua, textos in ETIQUETAS.items():
        ruta = os.path.join(G, lengua, archivo)
        if not os.path.exists(ruta):
            continue
        im = Image.open(ruta).convert('RGBA')
        for i, t in enumerate(textos):
            gl = glifos_de(im, i * alto, alto, margen)
            letras = [c for c in t if c != ' ']
            if len(gl) != len(letras):
                continue   # letras pegadas: no se pueden separar con seguridad
            for c, g in zip(letras, gl):
                fuente.setdefault(c, g)
    return fuente


if __name__ == '__main__':
    import sys
    archivo, alto = (sys.argv[1], int(sys.argv[2])) if len(sys.argv) > 2 else ('Pictures/types.png', 28)
    f = extraer(archivo, alto)
    print(''.join(sorted(f)))
    for c in sorted(f):
        print(c, ' '.join(r for r in f[c]))
