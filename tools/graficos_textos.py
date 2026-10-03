"""Textos sueltos dentro de imágenes (botones, avisos...) en castellano, con las
fuentes de píxeles del juego (Fonts/*.ttf, sin suavizado).

Para cada trabajo: imagen(es), región donde está el texto inglés, texto inglés y
texto nuevo. En la región:
  - letra = el color más claro con presencia (o el más oscuro, con 'oscuro');
    sombra = el color más frecuente justo abajo a la derecha de la letra;
  - el tamaño de la fuente se elige para que el texto inglés mida lo mismo que en
    la imagen (así el castellano sale con el mismo tamaño de letra);
  - se borran letra y sombra rellenando cada píxel con el del fondo más cercano
    de la misma fila (sin mezclar colores) y se escribe el texto nuevo centrado
    en el hueco que ocupaba el inglés (o en 'centro_x');
  - algunas fuentes dejan píxeles sueltos bajo la línea base: se quitan.

Uso: python tools/graficos_textos.py [patrón]
"""
import os
import sys
from collections import Counter

from PIL import Image, ImageDraw, ImageFont

from graficos_fuente import G, ORIGEN, DESTINO, RAIZ

FUENTES = os.path.join(RAIZ, 'repos', 'kanto', 'Fonts')

FORM = ['Pictures/trainer_application_form.png']
RIVAL = ['Pictures/trainer_application_form_rival.png']   # otra disposición: Name, Skin, Hair
TRABAJOS = [
    dict(archivos=FORM, region=(22, 72, 118, 100), en='Name', es='Nombre', fuente='power green.ttf', tam=12, izq=True, escala=2),
    dict(archivos=FORM, region=(22, 122, 148, 150), en='Gender', es='Género', fuente='power green.ttf', tam=12, izq=True, escala=2),
    dict(archivos=FORM, region=(22, 172, 170, 200), en='Age', es='Edad', fuente='power green.ttf', tam=12, izq=True, escala=2),
    dict(archivos=FORM, region=(22, 222, 148, 250), en='Skin', es='Piel', fuente='power green.ttf', tam=12, izq=True, escala=2),
    dict(archivos=FORM, region=(22, 272, 118, 300), en='Hair', es='Pelo', fuente='power green.ttf', tam=12, izq=True, escala=2),
    dict(archivos=FORM + RIVAL, region=(328, 78, 430, 102), en='Photo ID', es='Foto', fuente='power green.ttf',
         tam=12, escala=2),
    dict(archivos=FORM + RIVAL, region=(70, 18, 436, 50), en='TRAINER APPLICATION FORM', es='SOLICITUD DE ENTRENADOR',
         fuente='power clear bold.ttf', interpolar=True),
    dict(archivos=RIVAL, region=(22, 72, 118, 100), en='Name', es='Nombre', fuente='power green.ttf', tam=12, izq=True, escala=2),
    dict(archivos=RIVAL, region=(22, 122, 148, 150), en='Skin', es='Piel', fuente='power green.ttf', tam=12, izq=True, escala=2),
    dict(archivos=RIVAL, region=(22, 172, 170, 200), en='Hair', es='Pelo', fuente='power green.ttf', tam=12, izq=True, escala=2),
    dict(archivos=['Pictures/Outfits/hatLayer_selected1.png', 'Pictures/Outfits/hatLayer_selected2.png'],
         region=(30, 258, 102, 284), en='FRONT', es='DELANTE', fuente='power green narrow.ttf', tam=12, escala=2, oscuro=True, sombra=False),
    dict(archivos=['Pictures/Outfits/hatLayer_selected1.png', 'Pictures/Outfits/hatLayer_selected2.png'],
         region=(104, 258, 176, 284), en='BEHIND', es='DETRÁS', fuente='power green narrow.ttf', tam=12, escala=2, oscuro=True, sombra=False),
    dict(archivos=['Pictures/Outfits/hatLayer_selected1_dark.png', 'Pictures/Outfits/hatLayer_selected2_dark.png'],
         region=(30, 258, 102, 284), en='FRONT', es='DELANTE', fuente='power green narrow.ttf', tam=12, escala=2, sombra=False),
    dict(archivos=['Pictures/Outfits/hatLayer_selected1_dark.png', 'Pictures/Outfits/hatLayer_selected2_dark.png'],
         region=(104, 258, 176, 284), en='BEHIND', es='DETRÁS', fuente='power green narrow.ttf', tam=12, escala=2, sombra=False),
    dict(archivos=['Titles/intro_pressKey.png'], region=(40, 4, 234, 22),
         en='PRESS ANY KEY', es='PULSA CUALQUIER TECLA', fuente='power clear bold.ttf', interpolar='v'),
    dict(archivos=['Titles/intro_pressKey2.png'], region=(20, 4, 254, 22),
         en='PRESS ANY KEY TO CONTINUE', es='PULSA UNA TECLA PARA CONTINUAR', fuente='power clear bold.ttf',
         interpolar='v', compact_l=True),
    dict(archivos=['Pictures/Fusion/previewScreen_Cancel.png'], region=(70, 12, 180, 44),
         en='CANCEL', es='CANCELAR', fuente='power clear bold.ttf', oscuro=True, interpolar=True),
    dict(archivos=['Pictures/pokegearbg.png', 'Pictures/pokegearbgf.png'], region=(436, 4, 508, 24),
         en='BACK', es='ATRÁS', fuente='power clear bold.ttf'),
]


HECHOS = set()   # imágenes ya tocadas en esta ejecución (varios textos en una imagen)


def luz(p):
    return sum(p[:3]) * (p[3] > 0)


SIN_TILDE = str.maketrans('ÁÉÍÓÚ', 'AEIOU')


def render(texto, fuente, tam, compact_l=False):
    """Texto en mayúsculas a 1x. Las tildes se ponen a mano (dos píxeles en diagonal
    justo encima de la letra): las de estas fuentes salen sueltas y muy altas."""
    f = ImageFont.truetype(os.path.join(FUENTES, fuente), tam)
    base_txt = texto.translate(SIN_TILDE)
    m = Image.new('1', (int(f.getlength(base_txt)) + 20, tam * 2), 0)
    d = ImageDraw.Draw(m)
    d.fontmode = '1'
    d.text((4, 4), base_txt, font=f, fill=1)
    # Remove pixels below the baseline before measuring visible glyphs.
    e = Image.new('1', (tam * 2, tam * 2), 0)
    de = ImageDraw.Draw(e)
    de.fontmode = '1'
    de.text((4, 4), 'E', font=f, fill=1)
    base = e.getbbox()[3]
    for y in range(base, m.height):
        for x in range(m.width):
            m.putpixel((x, y), 0)
    if compact_l:
        spans, start = [], None
        for x in range(m.width):
            ink = any(m.getpixel((x, y)) for y in range(m.height))
            if ink and start is None:
                start = x
            if not ink and start is not None:
                spans.append((start, x))
                start = None
        letters = base_txt.replace(' ', '')
        assert len(spans) == len(letters), (base_txt, spans)
        # Recompose the whole line after trimming: keep one clear column
        # between letters, including LS and LA, and five between words.
        composed = Image.new('1', m.size, 0)
        cursor, glyph_index = 4, 0
        for c in base_txt:
            if c == ' ':
                cursor += 4
                continue
            left, right = spans[glyph_index]
            glyph_index += 1
            if c == 'L':
                right -= max(1, (right - left) // 4)
            glyph = m.crop((left, 0, right, m.height))
            assert cursor + glyph.width <= composed.width
            composed.paste(glyph, (cursor, 0))
            cursor += glyph.width + 1
        m = composed
    tope = m.getbbox()[1] if m.getbbox() else 4
    for i, c in enumerate(texto):
        if c in 'ÁÉÍÓÚ':
            x0 = 4 + int(f.getlength(base_txt[:i]))
            xc = x0 + int(f.getlength(base_txt[i])) // 2
            m.putpixel((xc, tope - 3), 1)
            m.putpixel((xc - 1, tope - 2), 1)
    bb = m.getbbox()
    return m.crop(bb)


def detectar(im, region, oscuro):
    x0, y0, x1, y1 = region
    c = Counter(im.getpixel((x, y)) for y in range(y0, y1) for x in range(x0, x1))
    cand = [p for p, n in c.items() if n >= 10 and p[3] > 0]
    letra = min(cand, key=luz) if oscuro else max(cand, key=luz)
    pts = [(x, y) for y in range(y0, y1) for x in range(x0, x1) if im.getpixel((x, y)) == letra]
    s = Counter(im.getpixel((x + 1, y + 1)) for x, y in pts
                if im.getpixel((x + 1, y + 1)) != letra and x + 1 < x1 and y + 1 < y1)
    sombra = None
    if s:
        p, n = s.most_common(1)[0]
        if n > len(pts) // 6:
            sombra = p
    return letra, sombra, pts


def aplicar(t, archivo):
    if not os.path.exists(os.path.join(G, ORIGEN, archivo)):
        return
    previa = os.path.join(G, DESTINO, archivo)
    origen = previa if archivo in HECHOS else os.path.join(G, ORIGEN, archivo)
    HECHOS.add(archivo)
    im = Image.open(origen).convert('RGBA')
    x0, y0, x1, y1 = t['region']
    letra, sombra, pts = detectar(im, t['region'], t.get('oscuro'))
    # Borrar siempre la sombra original, aunque el texto nuevo no lleve sombra.
    sombra_nueva = sombra if t.get('sombra') is not False else None
    if t.get('izq'):
        # palabra seguida de una línea de puntos del mismo color: la palabra son las
        # columnas con 3 o más píxeles de letra (los puntos solo tienen 1 o 2)
        cuenta = Counter(x for x, _ in pts)
        cols = sorted(x for x, n in cuenta.items() if n >= 3)
        pts = [(x, y) for x, y in pts if cols[0] <= x <= cols[-1]]
    xs, ys = [x for x, _ in pts], [y for _, y in pts]
    ancho_en, alto_en = max(xs) - min(xs) + 1, max(ys) - min(ys) + 1
    e = t.get('escala', 1)   # fuente de 1x dibujada al doble, como en el original
    # tamaño de fuente que reproduce el ancho del texto inglés
    tam = t.get('tam') or min(range(8, 40), key=lambda s: abs(render(t['en'], t['fuente'], s).width * e - ancho_en))

    def hacer(tam):
        m = render(t['es'], t['fuente'], tam, t.get('compact_l', False))
        return m.resize((m.width * e, m.height * e), Image.NEAREST) if e > 1 else m

    m = hacer(tam)
    while m.width > (x1 - x0) - 2 and tam > 8:
        tam -= 1
        m = hacer(tam)
    if t.get('izq'):   # borrar solo la palabra y los puntos que tape la nueva
        x0, x1 = min(xs) - 1, max(max(xs), min(xs) + m.width) + 3
    def parecido(p, q):
        return q is not None and p[3] > 0 and sum(abs(p[i] - q[i]) for i in range(3)) < 60

    def es_texto(p):
        return parecido(p, letra) or parecido(p, sombra)

    if t.get('interpolar'):
        # fondo liso o en degradado y texto suavizado: se rehace toda la caja del texto
        # interpolando cada fila entre el píxel de su izquierda y el de su derecha
        # ('v': entre el píxel de encima y el de debajo, para degradados horizontales)
        bx0, bx1 = max(x0, min(xs) - 2), min(x1, max(xs) + 3)
        by0, by1 = max(y0, min(ys) - 2), min(y1, max(ys) + 3)
        for y in range(by0, by1):
            for x in range(bx0, bx1):
                if t['interpolar'] == 'v':
                    a, b, f = im.getpixel((x, by0 - 1)), im.getpixel((x, by1)), (y - by0 + 1) / (by1 - by0 + 1)
                else:
                    a, b, f = im.getpixel((bx0 - 1, y)), im.getpixel((bx1, y)), (x - bx0 + 1) / (bx1 - bx0 + 1)
                im.putpixel((x, y), tuple(round(a[i] * (1 - f) + b[i] * f) for i in range(4)))
    for y in ([] if t.get('interpolar') else range(y0, y1)):
        fila = [im.getpixel((x, y)) for x in range(x0, x1)]
        libres = [i for i, p in enumerate(fila) if not es_texto(p)]
        for i, p in enumerate(fila):
            if es_texto(p) and libres:
                j = min(libres, key=lambda k: abs(k - i))
                im.putpixel((x0 + i, y), fila[j])
    if t.get('izq'):
        x = min(xs)
    else:
        cx = t.get('centro_x', (min(xs) + max(xs)) // 2)
        x = max(x0, min(cx - m.width // 2, x1 - m.width - 1))
    y = max(ys) - m.height + 1   # misma línea base
    for dx, dy, col in (((1, 1, sombra_nueva),) if sombra_nueva else ()) + ((0, 0, letra),):
        for py in range(m.height):
            for px in range(m.width):
                if m.getpixel((px, py)):
                    im.putpixel((x + px + dx, y + py + dy), col)
    dest = os.path.join(G, DESTINO, archivo)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    im.save(dest)
    print(f'-> {archivo}: {t["fuente"]} {tam}, letra {letra[:3]}, sombra {sombra_nueva and sombra_nueva[:3]}')


def main():
    filtro = sys.argv[1] if len(sys.argv) > 1 else ''
    for t in TRABAJOS:
        for a in t['archivos']:
            if filtro in a:
                aplicar(t, a)


if __name__ == '__main__':
    main()
