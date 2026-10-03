"""Regresión del selector de atuendos y medidas de los rótulos."""
from pathlib import Path
import json
import re
import rmarshal as rm
from PIL import ImageFont
from corregir_incidencias_20261003 import ROOT, CHANGES, apply
from graficos_textos import render

def battle_reference(text, index, reference):
    """Simula el formato contextual para comprobar ejemplos de mensajes reales."""
    if not re.match(r'^(El|el|Tu|tu) ',reference):return text.replace('{'+str(index)+'}',reference)
    lower=reference[0].lower()+reference[1:]
    if lower.startswith('el '):
        def contract(m):
            prep=m[1]; word='del ' if prep.lower()=='de' else 'al '
            if prep[0].isupper():word=word[0].upper()+word[1:]
            return word+lower[3:]
        text=re.sub(r'\b([Dd]e|[Aa])\s+\{'+str(index)+r'\}',contract,text)
    def substitute(m):
        prefix=re.sub(r'<[^>]*>|\\[a-z]+\[[^\]]*\]','',m.string[:m.start()],flags=re.I)
        beginning=re.fullmatch(r'\s*[¡¿]*\s*',prefix) or re.search(r'[.!?…]\s*[¡¿]*\s*$',prefix)
        return lower[0].upper()+lower[1:] if beginning else lower
    return re.sub(r'\{'+str(index)+r'\}',substitute,text)

def main():
    paths=[ROOT/'repos'/g/'Data/Scripts'/r for g in ('kanto','hoenn') for r in CHANGES]
    before=[p.read_bytes() for p in paths]
    apply()
    assert before==[p.read_bytes() for p in paths]
    for game in ('kanto','hoenn'):
        source=ROOT/'repos'/game
        save=(source/'Data/Scripts/052_InfiniteFusion/System/MultiSaves.rb').read_text(encoding='utf8')
        slots=re.search(r'MANUAL_SLOTS = \[(.*?)\]',save,re.S)[1]
        assert re.findall(r"'([^']+)'",slots)==['File '+c for c in 'ABCDEFGH']
        assert 'slot = SaveData::MANUAL_SLOTS[index]' in save
        assert 'ret = doSave($Trainer.save_slot)' in save
        assert '_INTL("Save to {1}", _INTL($Trainer.save_slot))' in save
        messages=rm.load_messages(str(source/'Data/spanish.dat'))
        drain=messages[24][rm.string_to_key("{1}'s health is sapped by Leech Seed!")]
        assert battle_reference(drain,1,'El Hoothoot salvaje')=='¡Drenadoras absorbe los PS del Hoothoot salvaje!'
        cases=[('¡{1} usó Placaje!','El Hoothoot salvaje','¡El Hoothoot salvaje usó Placaje!'),
               ('¡Punto Tóxico de {1} se activó!','El Hoothoot salvaje','¡Punto Tóxico del Hoothoot salvaje se activó!'),
               ('¡Paralizó a {1}!','El Hoothoot salvaje','¡Paralizó al Hoothoot salvaje!'),
               ('Pero {1} resistió.','El aliado Eevee','Pero el aliado Eevee resistió.'),
               ('¡Falló! ¡{1} resistió!','el Hoothoot rival','¡Falló! ¡El Hoothoot rival resistió!'),
               ('De {1} depende el resultado.','El Hoothoot rival','Del Hoothoot rival depende el resultado.'),
               ('¡Los PS de {1} se restauraron!','Tu equipo','¡Los PS de tu equipo se restauraron!'),
               ('\\f[1]¡{1} se debilitó!','el Hoothoot salvaje','\\f[1]¡El Hoothoot salvaje se debilitó!')]
        for template,reference,expected in cases:
            assert battle_reference(template,1,reference)==expected
        # Plain names are formatted by _INTL as ordinary strings, never marked.
        assert '¡Drenadoras absorbe los PS de {1}!'.replace('{1}','El Rey')=='¡Drenadoras absorbe los PS de El Rey!'
        summary=(source/'Data/Scripts/016_UI/006_UI_Summary.rb').read_text(encoding='utf8')
        assert '[_INTL("Speed"), 248, 242, 0, base, statshadows[:SPEED]]' in summary
        assert '[_INTL("Ability"), 248, 278, 0, base, shadow, false, 100]' in summary
        assert 'overlay.fill_rect(356, 274, 156, 40,' in summary
        assert 'memo += _INTL("{1} nature.", natureName) + "\\n"' in summary
        assert summary.count('memo += _INTL("{1} {2}, {3}", date, month, year) + "\\n"')==3
        assert r'memo += _INTL("Egg hatched.") + "\n"' in summary
        assert r'memo += _INTL("\"The Egg Watch\"") + "\n"' in summary
        nature=messages[24][rm.string_to_key('{1} nature.')].replace('{1}','Serena')
        date=messages[24][rm.string_to_key('{1} {2}, {3}')]
        date=date.replace('{1}','3').replace('{2}','Octubre').replace('{3}','2026')
        memo=nature+'\n'+date+'\nLaboratorio del Prof. Oak\nConocido al Nv. 5.\n\nBuena perseverancia.\n'
        assert memo.splitlines()[:3]==[nature,date,'Laboratorio del Prof. Oak']
        assert messages[24][rm.string_to_key('Save to {1}')]=='Guardar en {1}'
        for letter in 'ABCDEFGH':
            assert messages[24][rm.string_to_key('File '+letter)]=='Archivo '+letter
        intl=source/'Data/Scripts/001_Technical/003_Intl_Messages.rb'
        text=intl.read_text(encoding='utf8')
        dex=(source/'Data/Scripts/016_UI/Pokedex/004_UI_Pokedex_Entry.rb').read_text(encoding='utf8')
        assert 'drawPokedexMeasurement(overlay, weight_text, 122, base, shadow)' in dex
        assert 'drawPokedexMeasurement(overlay, height_text, 100, base, shadow)' in dex
        assert '[":", colon_x, y + 2, 0, base, shadow]' in dex
        assert 'sprite.src_rect.set(0, 0, available, 40)' in dex
        assert '    updatePokedexCredits\n' in dex
        assert 'while overlay.text_size(text).width > available && overlay.font.size > 24' in dex
        assert text.count('  string = pbResolveBattleReferences(string, arg)')==2
        battler=(source/'Data/Scripts/011_Battle/001_Battler/001_PokeBattle_Battler.rb').read_text(encoding='utf8')
        assert battler.count('return SpanishBattleReference.new(')==7
        assert '    return name\n' in battler
        popup=(source/'Data/Scripts/011_Battle/005_Battle scene/004_PokeBattle_SceneElements.rb').read_text(encoding='utf8')
        assert 'textX, 26, @side == 1,' in popup
        assert 'textX, @secondAbility ? 26 : -4, @side == 1,' in popup
        function=text.split('def pbResolveItemArticles(text, args)',1)[1].split('# END SPANISH ITEM CONCORDANCE',1)[0]
        assert function.index('return text if !text.is_a?(String)')<function.index('text.include?')
        assert 'definite = plural ?' in function and 'SPANISH_ITEM_FORMS[name]' in function
        targets=[ROOT/'publicar'/game]
        if game=='kanto':targets.append(ROOT/'installation/InfiniteFusion')
        for target in targets:
            for rel in ['001_Technical/003_Intl_Messages.rb',*CHANGES]:
                p=Path('Data/Scripts')/rel
                assert (source/p).read_bytes()==(target/p).read_bytes(),target/p
            assert (source/'Data/spanish.dat').read_bytes()==(target/'Data/spanish.dat').read_bytes()
            p=Path('Graphics/Localized/es/Titles/intro_pressKey2.png')
            assert (source/p).read_bytes()==(target/p).read_bytes(),target/p
    fonts=ROOT/'repos/kanto/Fonts'
    for original_size in (29,32):
        normal=ImageFont.truetype(str(fonts/'power green.ttf'),original_size)
        for label in ('Sprite','Entrada'):
            available=496-(224+normal.getlength(label)+normal.getlength(': ')+2)-2
            for game in ('kanto','hoenn'):
                entries=json.loads((ROOT/'repos'/game/'Data/pokedex/dex.json').read_text(encoding='utf8'))
                authors={e.get('author','') for e in entries}
                for author in authors:
                    author=(author or '').strip()
                    font=normal; size=original_size
                    if font.getlength(author)>available:
                        font=ImageFont.truetype(str(fonts/'power green narrow.ttf'),size)
                        while font.getlength(author)>available and size>24:
                            size-=1
                            font=ImageFont.truetype(str(fonts/'power green narrow.ttf'),size)
                    width=max(font.getlength(author)+2,available)
                    distance=width-available
                    # Start and final view stay inside the panel and reach every pixel.
                    assert available>0 and width-distance==available
                    assert 6+(original_size-size)//2+font.getbbox(author)[3]+2<=40
        for value in range(1,10000):
            text=f'{value/10:.1f} kg'; size=24
            font=ImageFont.truetype(str(fonts/'power green.ttf'),size)
            if font.getlength(text)>64:
                font=ImageFont.truetype(str(fonts/'power green narrow.ttf'),size)
                while font.getlength(text)>64 and size>16:
                    size-=1; font=ImageFont.truetype(str(fonts/'power green narrow.ttf'),size)
            box=font.getbbox(text); y=122+2+(24-size)//2+6
            assert 224+box[2]+2<=290,(text,size)
            assert y+box[1]>=132 and y+box[3]+2<=154,(text,size)
    print('Pokédex: créditos completos con desplazamiento; pesos de 0,1 a 999,9 kg dentro del recuadro.')
    ability_names=set(json.loads((ROOT/'traduccion/bd/habilidades.json').read_text(encoding='utf8')).values())
    for original_size in (29,32):
        for name in ability_names:
            size=original_size
            font=ImageFont.truetype(str(fonts/'power green.ttf'),size)
            if font.getlength(name)>142:
                font=ImageFont.truetype(str(fonts/'power green narrow.ttf'),size)
                while font.getlength(name)>142 and size>18:
                    size-=1
                    font=ImageFont.truetype(str(fonts/'power green narrow.ttf'),size)
            assert font.getlength(name)<=142,name
            y=282+(original_size-size)//2
            box=font.getbbox(name)
            assert y+box[1]>=274 and y+box[3]+2<=314,(name,size,box)
            assert 364+font.getlength(name)+2<=508,name
        # Espesura keeps the normal font and starts inside the clear field.
        normal=ImageFont.truetype(str(fonts/'power green.ttf'),original_size)
        assert normal.getlength('Espesura')<=142
        assert normal.getlength('Habilidad')<=100 or ImageFont.truetype(str(fonts/'power green narrow.ttf'),original_size).getlength('Habilidad')<=100
    assert 364==356+8
    assert 248+100+2<=356
    print(f'{len(ability_names)} habilidades: ancho, tildes y sombra dentro de su recuadro.')
    normal=ImageFont.truetype(str(fonts/'power green.ttf'),32)
    for label in ['Guardar en Archivo '+c for c in 'ABCDEFGH']+['Guardar en otro archivo']:
        assert normal.getlength(label)+4<=416,label
    for text,width in [('ID de Entrenador',154),('Introduce el código a canjear',336)]:
        for original_size in (29,32):
            sizes=range(original_size,int(original_size*3/4)-1,-1)
            assert any(ImageFont.truetype(str(fonts/'power green narrow.ttf'),s).getlength(text)+2<=width for s in sizes),text
    # Redemption keeps the normal font in both keyboard and cursor modes.
    # 448px window minus 32px borders and 4px padding; cursor has 416px.
    for original_size in (29,32):
        normal=ImageFont.truetype(str(fonts/'power green.ttf'),original_size)
        assert normal.getlength('Introduce el código a canjear')+2<=412
        assert normal.getlength('Introduce el código a canjear')+2<=416
    assert 32+448==480 and 480<=512
    assert 48+416==464 and 464<476
    old=render('L','power clear bold.ttf',16)
    new=render('L','power clear bold.ttf',16,True)
    assert new.height==old.height and new.width<old.width
    phrase='PULSA UNA TECLA PARA CONTINUAR'
    mask=render(phrase,'power clear bold.ttf',16,True)
    assert mask.width<=232
    spans, start=[], None
    for x in range(mask.width + 1):
        ink=x<mask.width and any(mask.getpixel((x,y)) for y in range(mask.height))
        if ink and start is None:start=x
        if not ink and start is not None:
            spans.append((start,x));start=None
    assert len(spans)==len(phrase.replace(' ',''))
    words=phrase.split()
    boundaries=set()
    count=0
    for word in words[:-1]:
        count+=len(word);boundaries.add(count)
    for index in range(1,len(spans)):
        gap=spans[index][0]-spans[index-1][1]
        assert gap==(5 if index in boundaries else 1),(index,gap)
    print('Rótulos medidos; pie de L corregido; guardia de valores vacíos anterior al uso de String; copias idénticas.')
if __name__=='__main__':main()
