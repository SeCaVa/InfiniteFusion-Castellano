"""Encaja los rótulos de la ficha y de entrada de texto sin abreviarlos."""
from pathlib import Path
import re
ROOT = Path(__file__).resolve().parents[1]
CHANGES = {
    '011_Battle/003_Battle/002_PokeBattle_Battle.rb': (
        'return _INTL("The opposing {1}",party[idxParty].name) if trainerBattle?',
        'return SpanishBattleReference.new(_INTL("The opposing {1}",party[idxParty].name)) if trainerBattle?'),
    '011_Battle/001_Battler/001_PokeBattle_Battler.rb': (
        'return lowerCase ? _INTL("the opposing {1}", name) : _INTL("The opposing {1}", name)',
        'return SpanishBattleReference.new(lowerCase ? _INTL("the opposing {1}", name) : _INTL("The opposing {1}", name))'),
    '011_Battle/006_Other battle types/002_PokeBattle_SafariZone.rb': (
        'return (lowerCase) ? _INTL("the wild {1}",name) : _INTL("The wild {1}",name)',
        'return SpanishBattleReference.new((lowerCase) ? _INTL("the wild {1}",name) : _INTL("The wild {1}",name))'),
    '011_Battle/005_Battle scene/004_PokeBattle_SceneElements.rb': (
        'textPos.push([_INTL("{1}\'s", @battler.name), textX, -4, @side == 1,',
        'textPos.push([_INTL("{1}\'s", @battler.name), textX, 26, @side == 1,'),
    '016_UI/Pokedex/004_UI_Pokedex_Entry.rb': (
        'textpos.push(["#{weight_text}", 224, 124, 0, base, shadow])',
        'drawPokedexMeasurement(overlay, weight_text, 122, base, shadow)'),
    '016_UI/006_UI_Summary.rb': (
        'memo += _INTL("{1} nature.\\n", natureName)',
        'memo += _INTL("{1} nature.", natureName) + "\\n"'),
    '052_InfiniteFusion/System/MultiSaves.rb': (
        '_INTL("Save to #{$Trainer.save_slot}")',
        '_INTL("Save to {1}", _INTL($Trainer.save_slot))'),
    '007_Objects and windows/012_TextEntry.rb': (
        '      textwidth=bitmap.text_size(@heading).width\n'
        '      pbDrawShadowText(bitmap,x,y, textwidth+4, 32, @heading,@baseColor,@shadowColor)',
        '      pbDrawTextPositions(bitmap, [[@heading, x, y - 6, false,\n'
        '         @baseColor, @shadowColor, false, bitmap.width - 4]])'),
    '016_UI/012_UI_TrainerCard.rb': (
        '[_INTL("Trainer ID"), 352, 28, 0, baseColor, shadowColor]',
        '[_INTL("Trainer ID"), 328, 28, 0, baseColor, shadowColor, false, 154]'),
    '016_UI/024_UI_TextEntry.rb': (
        '[@helptext, 160, 6, false, @text_color_base, @text_color_shadow]',
        '[@helptext, 160, 6, false, @text_color_base, @text_color_shadow, false, Graphics.width - 176]'),
}
BATTLE_HELPER = '''# BEGIN SPANISH BATTLE REFERENCES
# Only generated battler/team references carry this type; nicknames stay untouched.
class SpanishBattleReference < String; end

def pbResolveBattleReferences(text, args)
  return text if !text.is_a?(String)
  for i in 1...args.length
    reference = args[i]
    next if !reference.is_a?(SpanishBattleReference) || reference !~ /\\A(?:[Ee]l|[Tt]u) /
    lower = reference.sub(/\\A./) { |char| char.downcase }
    # Spanish contractions belong to the sentence, never to the nickname.
    if lower.start_with?("el ")
      text.gsub!(/\\b([Dd]e|[Aa])\\s+\\{#{i}\\}/) do
        preposition = $1
        contraction = preposition.downcase == "de" ? "del " : "al "
        contraction = contraction.sub(/\\A./) { |char| char.upcase } if preposition =~ /\\A[A-Z]/
        contraction + lower.sub(/\\Ael /, "")
      end
    end
    text.gsub!(/\\{#{i}\\}/) do
      prefix = $`.gsub(/<[^>]*>/, "").gsub(/\\\\[a-z]+\\[[^\\]]*\\]/i, "")
      beginning = prefix =~ /\\A\\s*[¡¿]*\\s*\\z/ || prefix =~ /[.!?…]\\s*[¡¿]*\\s*\\z/
      beginning ? lower.sub(/\\A./) { |char| char.upcase } : lower
    end
  end
  return text
end
# END SPANISH BATTLE REFERENCES

'''
POKEDEX_CREDITS_OLD = '''    textpos.push([_INTL("Sprite: {1}", sprite_author), 224, 156, 0, base, shadow])
    textpos.push([_INTL("Entry:  {1}", dex_author), 224, 188, 0, base, shadow]) if $Trainer.owned?(@species)'''
POKEDEX_CREDITS_NEW = '''    drawPokedexCredit(overlay, "sprite_credit", "Sprite: {1}", sprite_author, 156, base, shadow)
    drawPokedexCredit(overlay, "entry_credit", "Entry:  {1}", dex_author, 188, base, shadow) if $Trainer.owned?(@species)'''
POKEDEX_HELPERS = '''  # Fit measurements inside the original small panel, including the shadow.
  def drawPokedexMeasurement(overlay, text, y, base, shadow)
    name, size = overlay.font.name, overlay.font.size
    begin
      overlay.font.size = [size, 24].min
      pbFitTextToWidth(overlay, text, 64)
      while overlay.text_size(text).width > 64 && overlay.font.size > 16
        overlay.font.size -= 1
      end
      text_y = y + 2 + (24 - overlay.font.size) / 2
      pbDrawTextPositions(overlay, [[text, 224, text_y, 0, base, shadow]])
    ensure
      overlay.font.name, overlay.font.size = name, size
    end
  end

  # Keep labels stationary. Very long credits scroll at a readable font size.
  def drawPokedexCredit(overlay, key, template, author, y, base, shadow)
    label = _INTL(template, "").sub(/:\\s*$/, "")
    label_width = overlay.text_size(label).width
    colon_x = 224 + label_width
    pbDrawTextPositions(overlay, [[label, 224, y, 0, base, shadow],
      [":", colon_x, y + 2, 0, base, shadow]])
    author_x = colon_x + overlay.text_size(": ").width + 2
    available = 496 - author_x - 2
    text = author.to_s.strip
    name, size = overlay.font.name, overlay.font.size
    begin
      if overlay.text_size(text).width > available
        overlay.font.name = MessageConfig.pbGetNarrowFontName
        while overlay.text_size(text).width > available && overlay.font.size > 24
          overlay.font.size -= 1
        end
      end
      width = [overlay.text_size(text).width + 2, available].max
      @sprites[key].dispose if @sprites[key]
      sprite = BitmapSprite.new(width, 40, @viewport)
      @sprites[key] = sprite
      sprite.x, sprite.y = author_x, y
      sprite.bitmap.font.name, sprite.bitmap.font.size = overlay.font.name, overlay.font.size
      text_y = (size - overlay.font.size) / 2
      pbDrawTextPositions(sprite.bitmap, [[text, 0, text_y, 0, base, shadow]])
      sprite.src_rect.set(0, 0, available, 40)
      @pokedex_credit_scroll ||= {}
      @pokedex_credit_scroll[key] = [width - available, Graphics.frame_count]
    ensure
      overlay.font.name, overlay.font.size = name, size
    end
  end

  def updatePokedexCredits
    return if @page != 1 || !@pokedex_credit_scroll
    @pokedex_credit_scroll.each do |key, data|
      distance, start = data
      next if distance <= 0 || !@sprites[key] || !@sprites[key].visible
      elapsed = (Graphics.frame_count - start).to_f / Graphics.frame_rate
      travel = distance / 30.0
      phase = elapsed % (travel + 4.0)
      offset = [[(phase - 2.0) * 30, 0].max, distance].min.to_i
      @sprites[key].src_rect.x = offset
    end
  end

'''
SAVE_LABELS = [
    ('choices = SaveData::MANUAL_SLOTS\n',
     'choices = SaveData::MANUAL_SLOTS.map { |slot| _INTL(slot) }\n'),
    ('_INTL("Are you sure you want to overwrite the save in {1}?",slot)',
     '_INTL("Are you sure you want to overwrite the save in {1}?", _INTL(slot))'),
    ('commands[cmd_continue = commands.length] = "#{@selected_file}"',
     'commands[cmd_continue = commands.length] = _INTL(@selected_file.to_s)'),
]
ABILITY_LAYOUT = [
    ('[_INTL("Ability"), 224, 278, 0, base, shadow]',
     '[_INTL("Ability"), 248, 278, 0, base, shadow, false, 100]'),
]
ABILITY_NAME = '''    if ability
      # Keep the original value column, with room for accents above it.
      background = @sprites["background"].bitmap
      overlay.fill_rect(356, 274, 156, 40, background.get_pixel(400, 298))
      font_name, font_size = overlay.font.name, overlay.font.size
      begin
        pbFitTextToWidth(overlay, ability.name, 142)
        while overlay.text_size(ability.name).width > 142 && overlay.font.size > 18
          overlay.font.size -= 1
        end
        ability_y = 276 + (font_size - overlay.font.size) / 2
        pbDrawTextPositions(overlay, [[ability.name, 364, ability_y, 0,
          @text_color_base, @text_color_shadow]])
      ensure
        overlay.font.name, overlay.font.size = font_name, font_size
      end
'''
ENTRY_LAYOUT = [
    ('    if USEKEYBOARD\n'
     '      @sprites["entry"]=Window_TextEntry_Keyboard.new(initialText,\n'
     '         0,0,400-112,96,helptext,true)',
     '    if USEKEYBOARD\n'
     '      entry_width = (helptext == _INTL("Enter code to redeem")) ? Graphics.width - 64 : 400 - 112\n'
     '      @sprites["entry"]=Window_TextEntry_Keyboard.new(initialText,\n'
     '         0,0,entry_width,96,helptext,true)'),
    ('    @sprites["entry"].x=(Graphics.width/2)-(@sprites["entry"].width/2)+32',
     '    entry_offset = (helptext == _INTL("Enter code to redeem")) ? 0 : 32\n'
     '    @sprites["entry"].x=(Graphics.width/2)-(@sprites["entry"].width/2)+entry_offset'),
    ('    textPositions = [\n'
     '       [@helptext, 160, 6, false, @text_color_base, @text_color_shadow, false, Graphics.width - 176]\n'
     '    ]',
     '    code_prompt = (@helptext == _INTL("Enter code to redeem"))\n'
     '    heading_x = code_prompt ? 48 : 160\n'
     '    heading_width = code_prompt ? Graphics.width - 96 : Graphics.width - 176\n'
     '    textPositions = [\n'
     '       [@helptext, heading_x, 6, false, @text_color_base, @text_color_shadow, false, heading_width]\n'
     '    ]'),
]
def apply():
    for game in ('kanto', 'hoenn'):
        for rel, (old, new) in CHANGES.items():
            path=ROOT/'repos'/game/'Data/Scripts'/rel
            raw=path.read_bytes()
            newline='\r\n' if b'\r\n' in raw else '\n'
            text=raw.decode('utf8').replace('\r\n','\n')
            already_reflowed = rel=='016_UI/024_UI_TextEntry.rb' and ENTRY_LAYOUT[-1][1] in text
            assert old in text or new in text or already_reflowed,(game,rel)
            text=text.replace(old,new)
            if rel=='011_Battle/001_Battler/001_PokeBattle_Battler.rb':
                for kind in ('wild','ally'):
                    old_ref=f'return lowerCase ? _INTL("the {kind} {{1}}", name) : _INTL("The {kind} {{1}}", name)'
                    text=text.replace(old_ref,'return SpanishBattleReference.new('+old_ref[7:]+')')
                for first,second in [('the opposing team','The opposing team'),('your team','Your team')]:
                    old_ref=f'return lowerCase ? _INTL("{first}") : _INTL("{second}")'
                    text=text.replace(old_ref,'return SpanishBattleReference.new('+old_ref[7:]+')')
            if rel=='011_Battle/003_Battle/002_PokeBattle_Battle.rb':
                for kind in ('wild','ally'):
                    old_ref=f'return _INTL("The {kind} {{1}}",party[idxParty].name)'
                    text=text.replace(old_ref,'return SpanishBattleReference.new('+old_ref[7:]+')')
            if rel=='011_Battle/005_Battle scene/004_PokeBattle_SceneElements.rb':
                text=text.replace('textPos.push([abilityName, textX, 26, @side == 1,',
                                  'textPos.push([abilityName, textX, @secondAbility ? 26 : -4, @side == 1,')
            if rel=='016_UI/Pokedex/004_UI_Pokedex_Entry.rb':
                assert POKEDEX_CREDITS_OLD in text or POKEDEX_CREDITS_NEW in text
                text=text.replace(POKEDEX_CREDITS_OLD,POKEDEX_CREDITS_NEW)
                text=text.replace('textpos.push(["#{height_text}", 224, 102, 0, base, shadow])',
                                  'drawPokedexMeasurement(overlay, height_text, 100, base, shadow)')
                if '  def drawPokedexMeasurement(' in text:
                    text=re.sub(r'  # Fit measurements.*?(?=  def drawEntryText\()',
                                lambda m:POKEDEX_HELPERS,text,flags=re.S)
                else:
                    text=text.replace('  def drawEntryText(overlay, species_data, reloading = false)',
                                      POKEDEX_HELPERS+'  def drawEntryText(overlay, species_data, reloading = false)',1)
                    text=text.replace('    pbUpdateSpriteHash(@sprites)\n',
                                      '    pbUpdateSpriteHash(@sprites)\n    updatePokedexCredits\n',1)
                    text=text.replace('    overlay.clear\n',
                                      '    overlay.clear\n    ["sprite_credit", "entry_credit"].each { |key| @sprites[key].visible = false if @sprites[key] }\n',1)
            if rel=='016_UI/006_UI_Summary.rb':
                # A localized string lookup normalizes trailing whitespace.
                # The memo owns its line breaks, outside the translated text.
                text=re.sub(r'(memo \+= _INTL\("[^"\n]*?)\\n("[^\n]*?\))',
                            lambda m:m[1]+m[2]+' + "\\n"',text)
                text=text.replace(r'memo += _INTL("\"The Egg Watch\"\n")',
                                  r'memo += _INTL("\"The Egg Watch\"") + "\n"')
                text=text.replace('[_INTL("Ability"), 224, 276, 0, base, shadow, false, 88]',
                                  '[_INTL("Ability"), 248, 278, 0, base, shadow, false, 100]')
                for previous, corrected in ABILITY_LAYOUT:
                    assert previous in text or corrected in text,(game,previous)
                    text=text.replace(previous,corrected)
                pattern=r'    if ability\n.*?(?=      drawTextEx\(overlay, 224, 320, 282, 2, ability.description)'
                assert len(re.findall(pattern,text,re.S))==1,game
                text=re.sub(pattern,lambda m:ABILITY_NAME,text,flags=re.S)
            if rel=='052_InfiniteFusion/System/MultiSaves.rb':
                for previous, corrected in SAVE_LABELS:
                    assert previous in text or corrected in text,(game,previous)
                    text=text.replace(previous,corrected)
            if rel=='016_UI/024_UI_TextEntry.rb':
                for previous, corrected in ENTRY_LAYOUT:
                    assert previous in text or corrected in text,(game,previous)
                    text=text.replace(previous,corrected)
            out=text.replace('\n',newline).encode('utf8')
            if out!=raw:path.write_bytes(out)
        intl=ROOT/'repos'/game/'Data/Scripts/001_Technical/003_Intl_Messages.rb'
        raw=intl.read_bytes()
        newline='\r\n' if b'\r\n' in raw else '\n'
        text=raw.decode('utf8').replace('\r\n','\n')
        if '# BEGIN SPANISH BATTLE REFERENCES' in text:
            text=re.sub(r'# BEGIN SPANISH BATTLE REFERENCES.*?# END SPANISH BATTLE REFERENCES\n\n',
                        lambda m:BATTLE_HELPER,text,flags=re.S)
        else:text=text.replace('def _INTL(*arg)',BATTLE_HELPER+'def _INTL(*arg)',1)
        old_format='  string = pbResolveItemArticles(string.clone, arg)\n'
        new_format=old_format+'  string = pbResolveBattleReferences(string, arg)\n'
        # Both script and map messages use the same marked references.
        if new_format not in text:text=text.replace(old_format,new_format)
        out=text.replace('\n',newline).encode('utf8')
        if out!=raw:intl.write_bytes(out)
        print(game+': rótulos ajustados a su espacio.')
if __name__=='__main__':apply()
