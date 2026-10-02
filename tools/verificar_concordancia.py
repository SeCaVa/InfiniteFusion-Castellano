"""Comprueba concordancias, mensajes y límites de las descripciones de mochila."""
import json
from pathlib import Path
from PIL import ImageFont
import rmarshal as rm
from revisar import codigos
from concordancia_objetos import forms, apply as articles, REL as INTL
from ajustar_descripciones_mochila import apply as bag, REL as BAG
from verificar_pokedex import pages
ROOT=Path(__file__).resolve().parents[1]

def main():
    table=forms()
    for name,expected in {'Punta ADN':1, 'Puntas ADN':3, 'Poké Ball':1,
                          'Restos':2, 'Gafas Elección':3, 'Agua Fresca':5,
                          'MT94':1}.items():
        assert table[name]==expected,(name,table.get(name))
    paths=[ROOT/'repos'/g/r for g in ('kanto','hoenn') for r in (INTL,BAG)]
    before=[p.read_bytes() for p in paths]
    articles(); bag()
    assert before==[p.read_bytes() for p in paths], 'Aplicación no idempotente'
    script=json.loads((ROOT/'traduccion/script.json').read_text(encoding='utf8'))
    for en,es in script.items():
        if '{art:' in es: assert codigos(en)==codigos(es),en
    fontfile=ROOT/'repos/kanto/Fonts/power green.ttf'
    fonts={size:ImageFont.truetype(str(fontfile),size) for size in (29,25)}
    descriptions=json.loads((ROOT/'traduccion/bd/objetos_desc.json').read_text(encoding='utf8'))
    maximum=1
    for text in descriptions.values():
        if not text: continue
        result=pages(text,fonts[29].getlength,width=400)
        size=29
        if len(result)>1:
            size=25; result=pages(text,fonts[25].getlength,width=400)
        maximum=max(maximum,len(result))
        assert ''.join(text.split())==''.join(line.replace(' ','') for p in result for line in p)
        assert all(fonts[size].getlength(line)<=400 for p in result for line in p)
        assert all(len(p)<=3 for p in result)
        lineheight=32 if size==29 else 28
        assert 3*lineheight+2<=100
        if len(result)>1: assert 84+16<=100
    for game in ('kanto','hoenn'):
        src=ROOT/'repos'/game
        targets=[ROOT/'publicar'/game]
        if game=='kanto':targets.append(ROOT/'installation/InfiniteFusion')
        for target in targets:
            for rel in (INTL,BAG,Path('Data/spanish.dat')):
                assert (src/rel).read_bytes()==(target/rel).read_bytes(),target/rel
        messages=rm.load_messages(str(src/'Data/spanish.dat'))
        for path in (ROOT/'traduccion/dialogos'/game).glob('Map[0-9]*.json'):
            mid=int(path.stem[3:])
            data=json.loads(path.read_text(encoding='utf8'))
            if mid>=len(messages[0]) or not isinstance(messages[0][mid],dict):continue
            for en,es in data.items():
                key=rm.string_to_key(en)
                if key in messages[0][mid]: assert messages[0][mid][key]==es,(game,mid,en)
    print(f'{len(table)} formas verificadas; {len(descriptions)} descripciones íntegras, hasta {maximum} páginas; copias idénticas.')

if __name__=='__main__':main()
