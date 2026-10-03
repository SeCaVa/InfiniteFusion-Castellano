"""Instala la firma de SeCaVa antes de la cinemática original, sin duplicar llamadas."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path('Data/Scripts/052_InfiniteFusion/Menus/SpanishCreditsIntro.rb')
MAIN = Path('Data/Scripts/999_Main/999_Main.rb')
CALL = '    SpanishCreditsIntro.play\n'
ANCHOR = '    $scene = pbCallTitle\n'

def install(target):
    source = ROOT / 'traduccion/intro'
    for src, rel in ((source / 'SpanishCreditsIntro.rb', SCRIPT),
                     (source / 'logo.png', Path('Graphics/Titles/SeCaVa/logo.png')),
                     (source / 'jingle.wav', Path('Audio/ME/SeCaVa_intro.wav'))):
        dest = target / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
        assert dest.read_bytes() == src.read_bytes()
    main = target / MAIN
    text = main.read_text(encoding='utf-8')
    assert text.count(ANCHOR) == 1, main
    text = text.replace(CALL, '').replace(ANCHOR, CALL + ANCHOR)
    main.write_text(text, encoding='utf-8', newline='\n')

def main():
    for game in ('kanto', 'hoenn'):
        install(ROOT / 'repos' / game)
    # Maintain the shared script extraction used when regenerating the patch.
    for rel in (SCRIPT, MAIN):
        shutil.copyfile(ROOT / 'repos/kanto' / rel, ROOT / 'repos/scripts' / rel.relative_to('Data/Scripts'))
    if (ROOT / 'installation/InfiniteFusion').is_dir():
        install(ROOT / 'installation/InfiniteFusion')
    if (ROOT / 'publicar').is_dir():
        for game in ('kanto', 'hoenn'):
            target = ROOT / 'publicar' / game
            (target / MAIN).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / 'repos' / game / MAIN, target / MAIN)
            install(target)
        for rel in ('tools/instalar_intro.py', 'traduccion/intro/SpanishCreditsIntro.rb',
                    'traduccion/intro/logo.png', 'traduccion/intro/jingle.wav', 'aplicar.sh'):
            dest = ROOT / 'publicar' / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, dest)
    print('Intro instalada en Kanto, Hoenn y las copias locales disponibles.')

if __name__ == '__main__':
    main()
