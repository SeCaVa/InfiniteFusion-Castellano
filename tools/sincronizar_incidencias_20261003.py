"""Distribuye las correcciones de rótulos y del selector de atuendos."""
from pathlib import Path
import shutil
from corregir_incidencias_20261003 import CHANGES, ROOT
from graficos_instalar import original, igual
GRAPHIC=Path('Titles/intro_pressKey2.png')
def copy(src,dst):
    dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(src,dst)
    assert src.read_bytes()==dst.read_bytes(),dst
def main():
    graphic=ROOT/'traduccion/graficos/es'/GRAPHIC
    baseline=ROOT/'traduccion/graficos/en'/GRAPHIC
    for game in ('kanto','hoenn'):
        source=ROOT/'repos'/game
        targets=[source,ROOT/'publicar'/game]
        if game=='kanto':targets.append(ROOT/'installation/InfiniteFusion')
        for target in targets:
            if target!=source:copy(source/'Data/spanish.dat',target/'Data/spanish.dat')
            for rel in ['001_Technical/003_Intl_Messages.rb',*CHANGES]:
                p=Path('Data/Scripts')/rel
                if target!=source:copy(source/p,target/p)
            base=original(str(source if target==ROOT/'publicar'/game else target),str(GRAPHIC))
            assert base and igual(base,str(baseline)),target
            copy(graphic,target/'Graphics/Localized/es'/GRAPHIC)
    for rel in ['tools/concordancia_objetos.py','tools/graficos_textos.py',
                'tools/corregir_incidencias_20261003.py','tools/sincronizar_incidencias_20261003.py',
                'tools/verificar_incidencias_20261003.py','aplicar.sh','traduccion/script.json']:
        copy(ROOT/rel,ROOT/'publicar'/rel)
    copy(graphic,ROOT/'publicar/traduccion/graficos/es'/GRAPHIC)
    print('Correcciones distribuidas y copias comprobadas.')
if __name__=='__main__':main()
