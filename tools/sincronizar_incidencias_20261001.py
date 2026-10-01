"""Copia únicamente las correcciones de esta tanda a publicar/ y a la instalación."""
from pathlib import Path
import shutil
from corregir_incidencias_20261001 import CAMBIOS, ROOT
from graficos_instalar import original, igual

GRAFICOS = [f'Pictures/Outfits/hatLayer_selected{i}{dark}.png'
            for dark in ('', '_dark') for i in (1, 2)]

def copiar(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    assert src.read_bytes() == dst.read_bytes(), dst

def sincronizar():
    for game in ('kanto', 'hoenn'):
        repo = ROOT / 'repos' / game
        destinos = [ROOT / 'publicar' / game]
        if game == 'kanto':
            destinos.append(ROOT / 'installation' / 'InfiniteFusion')
        for dest in destinos:
            for rel in ['Data/spanish.dat', *('Data/Scripts/' + p for p in CAMBIOS)]:
                copiar(repo / rel, dest / rel)
            for rel in GRAFICOS:
                src = ROOT / 'traduccion' / 'graficos' / 'es' / rel
                base = ROOT / 'traduccion' / 'graficos' / 'en' / rel
                if game == 'kanto' and (ROOT / 'traduccion/graficos/es_kanto' / rel).exists():
                    src = ROOT / 'traduccion/graficos/es_kanto' / rel
                    base = ROOT / 'traduccion/graficos/en_kanto' / rel
                # No se aplica un gráfico a una variante con otro original.
                target_orig = original(str(repo if dest == ROOT / 'publicar' / game else dest), rel)
                if not target_orig:
                    print(f'{game}: no usa {rel}; se omite')
                    continue
                if not igual(target_orig, str(base)):
                    raise ValueError(f'Original gráfico distinto: {dest}/{rel}')
                copiar(src, dest / 'Graphics' / 'Localized' / 'es' / rel)
                copiar(src, repo / 'Graphics' / 'Localized' / 'es' / rel)
            print(f'Actualizado y comparado: {dest.relative_to(ROOT)}')
    for rel in ('traduccion/script.json', 'traduccion/lugares/mapas.json',
                'tools/generar_dat.py', 'tools/verificar_incidencias_20261001.py',
                'traduccion/lugares/_manuales.json', 'tools/graficos_textos.py',
                'tools/corregir_incidencias_20261001.py',
                'tools/sincronizar_incidencias_20261001.py', 'aplicar.sh'):
        copiar(ROOT / rel, ROOT / 'publicar' / rel)
    for variant in ('es', 'es_kanto'):
        for rel in GRAFICOS:
            src = ROOT / 'traduccion/graficos' / variant / rel
            if src.exists():
                copiar(src, ROOT / 'publicar/traduccion/graficos' / variant / rel)

if __name__ == '__main__':
    sincronizar()
