"""Distribuye únicamente diccionario revisado, lector y mensajes de Pokédex."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
READER = Path('Data/Scripts/016_UI/Pokedex/004_UI_Pokedex_Entry.rb')
UI_FILES = (READER, Path('Data/Scripts/001_Technical/003_Intl_Messages.rb'),
            Path('Data/Scripts/016_UI/007_UI_Bag.rb'))
PUBLIC_FILES = ('traduccion/pokedex/fusiones.json', 'tools/pokedex_fusiones.py',
                'tools/aplicar_pokedex_fusiones.py', 'tools/sincronizar_pokedex.py',
                'tools/verificar_pokedex.py', 'tools/generar_dat.py', 'aplicar.sh', 'glosario.md',
                'tools/concordancia_objetos.py', 'tools/ajustar_descripciones_mochila.py',
                'tools/verificar_concordancia.py', 'traduccion/script.json',
                'traduccion/dialogos/comun.json', 'traduccion/entrenadores/frases.json')

def copy(src, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)
    assert src.read_bytes() == dest.read_bytes(), dest

def main():
    for game in ('kanto', 'hoenn'):
        source = ROOT / 'repos' / game
        targets = [ROOT / 'publicar' / game]
        if game == 'kanto':
            targets.append(ROOT / 'installation/InfiniteFusion')
        for target in targets:
            for rel in (Path('Data/spanish.dat'), *UI_FILES):
                copy(source / rel, target / rel)
            print(f'Pokédex actualizada: {target.relative_to(ROOT)}')
    for rel in PUBLIC_FILES:
        copy(ROOT / rel, ROOT / 'publicar' / rel)
    for game in ('kanto', 'hoenn'):
        for path in (ROOT / 'traduccion/dialogos' / game).glob('Map[0-9]*.json'):
            copy(path, ROOT / 'publicar' / path.relative_to(ROOT))

if __name__ == '__main__':
    main()
