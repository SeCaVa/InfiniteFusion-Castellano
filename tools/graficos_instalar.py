"""Copia los gráficos en castellano (traduccion/graficos/es) a Graphics/Localized/es
de cada juego (el juego los usa solos cuando el idioma es español; ver
pbLocalizedBitmapFilename en LanguageUtils.rb) y de la instalación.

Antes comprueba que el original inglés de cada juego es el mismo del que se partió
(traduccion/graficos/en, sacado de Hoenn; en_kanto/es_kanto para los que en Kanto
son distintos); si no coincide, no lo copia a ese juego y avisa.

Uso: python tools/graficos_instalar.py [--comprobar]
"""
import os
import shutil
import sys

from PIL import Image, ImageChops

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ES = os.path.join(RAIZ, 'traduccion', 'graficos', 'es')
EN = os.path.join(RAIZ, 'traduccion', 'graficos', 'en')
# Los que en Kanto son distintos se hacen aparte desde su propio original
ES_KANTO = os.path.join(RAIZ, 'traduccion', 'graficos', 'es_kanto')
EN_KANTO = os.path.join(RAIZ, 'traduccion', 'graficos', 'en_kanto')
DESTINOS = {
    'kanto': os.path.join(RAIZ, 'repos', 'kanto'),
    'hoenn': os.path.join(RAIZ, 'repos', 'hoenn'),
    'instalación (kanto)': os.path.join(RAIZ, 'installation', 'InfiniteFusion'),
}


def original(juego_dir, rel):
    """Ruta del original del juego (el nombre puede cambiar de mayúsculas)."""
    d = os.path.join(juego_dir, 'Graphics', os.path.dirname(rel))
    if not os.path.isdir(d):
        return None
    for x in os.listdir(d):
        if x.lower() == os.path.basename(rel).lower():
            return os.path.join(d, x)
    return None


def igual(a, b):
    ia, ib = Image.open(a).convert('RGBA'), Image.open(b).convert('RGBA')
    return ia.size == ib.size and ImageChops.difference(ia, ib).getbbox() is None


def main():
    comprobar = '--comprobar' in sys.argv
    for raiz, _, fs in os.walk(ES):
        for fn in fs:
            rel = os.path.relpath(os.path.join(raiz, fn), ES).replace(os.sep, '/')
            for nombre, juego_dir in DESTINOS.items():
                es_f, en_f = os.path.join(raiz, fn), os.path.join(EN, rel)
                if 'kanto' in nombre and os.path.exists(os.path.join(ES_KANTO, rel)):
                    es_f, en_f = os.path.join(ES_KANTO, rel), os.path.join(EN_KANTO, rel)
                orig = original(juego_dir, rel)
                if orig is None:
                    print(f'{nombre}: no tiene {rel}')
                    continue
                if not igual(orig, en_f):
                    print(f'{nombre}: {rel} es distinto del original usado; no se copia')
                    continue
                if comprobar:
                    continue
                # mismo nombre de archivo que el original del juego
                dest = os.path.join(juego_dir, 'Graphics', 'Localized', 'es', os.path.dirname(rel),
                                    os.path.basename(orig))
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copyfile(es_f, dest)
    print('hecho')


if __name__ == '__main__':
    main()
