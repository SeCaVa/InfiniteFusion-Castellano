"""Busca textos traducidos que pueden no caber en menús y ventanas.

Mide el ancho en píxeles con la fuente del juego (Power Green, 29) y compara
con el inglés:
  - Tablas de nombres (objetos, movimientos, habilidades...): marca las
    traducciones más anchas que el nombre inglés más ancho de la tabla, que es
    el espacio que la interfaz ya reserva.
  - script.json: textos cortos tipo menú (pocas palabras, sin puntuación de
    frase) cuya traducción es bastante más ancha que el inglés.
Informe en traduccion/_informes/anchos.txt
"""
import os
import re
import sys

from PIL import ImageFont

sys.path.insert(0, os.path.dirname(__file__))
from extraer import RAIZ, TRAD, cargar_json

FUENTE = ImageFont.truetype(os.path.join(RAIZ, 'repos', 'kanto', 'Fonts', 'power green.ttf'), 29)
CODIGO = re.compile(r'\\[A-Za-z]+(\[[^\]]*\])?|<[^>]+>|\[\[([^|\]]*)\|([^\]]*)\]\]')

TABLAS = ['bd/objetos', 'bd/objetos_plural', 'bd/movimientos', 'bd/habilidades', 'bd/tipos',
          'bd/clases_entrenador', 'bd/categorias', 'bd/formas', 'bd/cintas',
          'bd/bayas_firmeza', 'lugares/mapas', 'lugares/lugares']


def visible(s, femenino=False):
    """Texto tal como se ve: sin códigos y con la marca de género resuelta."""
    def rep(m):
        if m.group(2) is not None or m.group(3) is not None:
            return m.group(3) if femenino else m.group(2)
        return ''
    return CODIGO.sub(rep, s)


def ancho(s):
    s = max((visible(s), visible(s, True)), key=len)
    return max(FUENTE.getlength(linea) for linea in s.split('\n'))


def es_menu(en):
    return (len(en) <= 24 and len(en.split()) <= 4 and not re.search(r'[.!?,]\s|[.!?]$', en)
            and not CODIGO.search(en))


def main():
    salida = []
    for tabla in TABLAS:
        d = {k: v for k, v in cargar_json(tabla).items() if v and k}
        if not d:
            continue
        tope = max(ancho(k) for k in d)
        largos = sorted(((ancho(v), k, v) for k, v in d.items() if ancho(v) > tope), reverse=True)
        salida.append(f'== {tabla}: inglés más ancho {tope:.0f}px, {len(largos)} traducciones lo superan')
        salida += [f'  {a:4.0f}px  {k} → {v}' for a, k, v in largos]
    d = cargar_json('script')
    filas = []
    for en, es in d.items():
        if not es or not es_menu(en):
            continue
        ae, ai = ancho(en), ancho(es)
        if ai > ae * 1.35 and ai - ae > 30:
            filas.append((ai - ae, ae, ai, en, es))
    filas.sort(reverse=True)
    salida.append(f'== script (textos de menú): {len(filas)} bastante más anchos que el inglés')
    salida += [f'  +{dif:3.0f}px ({ae:.0f}→{ai:.0f})  {en} → {es}' for dif, ae, ai, en, es in filas]
    ruta = os.path.join(TRAD, '_informes', 'anchos.txt')
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write('\n'.join(salida) + '\n')
    for linea in salida:
        if linea.startswith('=='):
            print(linea)
    print('Detalle:', os.path.relpath(ruta, RAIZ))


if __name__ == '__main__':
    main()
