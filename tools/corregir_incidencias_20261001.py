"""Aplica correcciones de interfaz revisadas a ambos repositorios, sin tocar partidas.

Idempotente: solo sustituye bloques conocidos y falla si el original no coincide.
Los diccionarios se mantienen por separado; este script conserva los cambios Ruby.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAMBIOS = {
    '016_UI/015_UI_Options.rb': [
        ('height = (Graphics.height - @sprites["title"].height - @sprites["textbox"].height) +32',
         'height = Graphics.height - @sprites["title"].height - @sprites["textbox"].height'),
        ('optionwidth = rect.width * 9 / 20',
         'optionwidth = (index == @options.length) ? rect.width : rect.width * 9 / 20'),
        ('pbDrawShadowText(self.contents, rect.x, rect.y, optionwidth, rect.height, optionname,',
         'pbDrawShadowText(self.contents, rect.x, rect.y - 4 + (font_size - self.contents.font.size) / 2, optionwidth, rect.height, optionname,'),
    ],
    '050_Outfits/UI/CharacterSelectMenu.rb': [
        ('[text1, xposition, yposition, 2, baseColor, shadowColor],',
         '[text1, xposition, yposition, 2, baseColor, shadowColor, false, 128],'),
        ('  def get_cursor_x_position(index)\n',
         '  def get_cursor_x_position(index)\n'
         '    hair_selected = (@hair_row && index == @hair_row)\n'
         '    @sprites["select"].zoom_x = hair_selected ? 184.0 / @sprites["select"].bitmap.width : 1.0\n'
         '    return hair_field_center(index) - 92 if hair_selected\n'),
        ('    @sprites["rightarrow"].visible = true\n    @sprites["leftarrow"].visible = true\n',
         '    if @hair_row && y_index == @hair_row\n'
         '      @sprites["leftarrow"].x = hair_field_center(y_index) - 134\n'
         '      @sprites["rightarrow"].x = hair_field_center(y_index) + 96\n'
         '    end\n'
         '    @sprites["rightarrow"].visible = true\n    @sprites["leftarrow"].visible = true\n'),
        ('  def displayText(spriteId, text, y_index)\n',
         '  # Widen only the hair field, preserving the original border corners.\n'
         '  def hair_field_center(index)\n'
         '    return [get_value_x_position(index), 234].min\n'
         '  end\n\n'
         '  def prepare_hair_field(index)\n'
         '    @hair_row = index\n'
         '    return if @sprites["hair_field"]\n'
         '    source = @sprites["bg"].bitmap\n'
         '    sx = get_value_x_position(index) - 72\n'
         '    sy = get_cursor_y_position(index) + 2\n'
         '    field = BitmapSprite.new(184, 34, @viewport)\n'
         '    field.x = hair_field_center(index) - 92\n'
         '    field.y = sy\n'
         '    field.z = @sprites["bg"].z + 1\n'
         '    field.bitmap.blt(0, 0, source, Rect.new(sx, sy, 6, 34))\n'
         '    field.bitmap.stretch_blt(Rect.new(6, 0, 172, 34), source, Rect.new(sx + 6, sy, 132, 34))\n'
         '    field.bitmap.blt(178, 0, source, Rect.new(sx + 138, sy, 6, 34))\n'
         '    @sprites["hair_field"] = field\n'
         '    @sprites["select"].z = @sprites["bg"].z + 2\n'
         '    @sprites["leftarrow"].z = @sprites["bg"].z + 3\n'
         '    @sprites["rightarrow"].z = @sprites["bg"].z + 3\n'
         '  end\n\n'
         '  def displayText(spriteId, text, y_index)\n'),
        ('    text1 = _INTL(text)\n',
         '    text1 = _INTL(text)\n'
         '    if spriteId == "hair"\n'
         '      prepare_hair_field(y_index)\n'
         '      xposition = hair_field_center(y_index)\n'
         '      @textValues[spriteId].z = @sprites["bg"].z + 4\n'
         '    end\n'),
        ('    pbSetSystemFont(@textValues[spriteId].bitmap)\n',
         '    pbSetSystemFont(@textValues[spriteId].bitmap)\n'
         '    if spriteId == "hair"\n'
         '      # Keep the regular font; only one size step is normally needed.\n'
         '      bitmap = @textValues[spriteId].bitmap\n'
         '      original_size = bitmap.font.size\n'
         '      while bitmap.text_size(text1).width > 172 && bitmap.font.size > 25\n'
         '        bitmap.font.size -= 1\n'
         '      end\n'
         '      textPosition[0][2] += (original_size - bitmap.font.size) / 2\n'
         '      textPosition[0][7] = 172\n'
         '    end\n'),
    ],
    '016_UI/007_UI_Bag.rb': [
        ('[PokemonBag.pocketNames[@bag.lastpocket],94,176,2,pnBase,pnShadow]',
         '[PokemonBag.pocketNames[@bag.lastpocket],94,176,2,pnBase,pnShadow,false,172]'),
    ],
    '016_UI/024_UI_TextEntry.rb': [
        ('def pbEnterNPCName(helptext,minlength,maxlength,initialText="",id=0,nofadeout=false)\n  return pbEnterText',
         'def pbEnterNPCName(helptext,minlength,maxlength,initialText="",id=0,nofadeout=false)\n'
         '  # Some map events pass the rival prompt and default name without _INTL.\n'
         '  if helptext == "Rival\'s nickname?" || helptext == _INTL("Rival\'s nickname?")\n'
         '    helptext = _INTL("Rival\'s nickname?")\n'
         '    initialText = _INTL("Blue") if initialText == "Blue"\n'
         '  end\n  return pbEnterText'),
    ],
    '052_InfiniteFusion/Gameplay/0_Utilities/SystemUtils.rb': [
        ('def optionsMenu(options = [], cmdIfCancel = -1, startingOption = 0)\n',
         'def optionsMenu(options = [], cmdIfCancel = -1, startingOption = 0)\n'
         '  # Older common events build this download-source menu without _INTL.\n'
         '  # Event scripts may split a quoted option across lines.\n'
         '  if options.any? { |option| option.gsub(/\\s+/, " ").strip == "The game\'s official Discord" }\n'
         '    options = options.map { |option| _INTL(option.gsub(/\\s+/, " ").strip) }\n'
         '  end\n'),
    ],
}

def aplicar():
    for game in ('kanto', 'hoenn'):
        for rel, cambios in CAMBIOS.items():
            path = ROOT / 'repos' / game / 'Data' / 'Scripts' / rel
            src = path.read_text(encoding='utf-8')
            # Actualizar también las versiones de la primera tanda.
            if rel == '050_Outfits/UI/CharacterSelectMenu.rb':
                src = src.replace('[text1, xposition, yposition, 2, baseColor, shadowColor, false, 144],',
                                  '[text1, xposition, yposition, 2, baseColor, shadowColor, false, 128],')
            if rel == '052_InfiniteFusion/Gameplay/0_Utilities/SystemUtils.rb':
                src = src.replace('  if options.include?("The game\'s official Discord")\n'
                                  '    options = options.map { |option| _INTL(option) }\n',
                                  '  # Event scripts may split a quoted option across lines.\n'
                                  '  if options.any? { |option| option.gsub(/\\s+/, " ").strip == "The game\'s official Discord" }\n'
                                  '    options = options.map { |option| _INTL(option.gsub(/\\s+/, " ").strip) }\n')
            for antes, despues in cambios:
                if despues in src:
                    continue
                if src.count(antes) != 1:
                    raise ValueError(f'Bloque inesperado: {game}/{rel}: {antes[:65]}')
                src = src.replace(antes, despues, 1)
            with path.open('w', encoding='utf-8', newline='\n') as out:
                out.write(src)
            print(f'{game}: {rel}')

if __name__ == '__main__':
    aplicar()
