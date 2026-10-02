"""Descripciones completas dentro del panel de la mochila, con páginas si hace falta."""
from pathlib import Path
import re
ROOT = Path(__file__).resolve().parents[1]
REL = Path('Data/Scripts/016_UI/007_UI_Bag.rb')
CLASS = r'''
# BEGIN BAG DESCRIPTION PAGES
class BagDescriptionSprite < BitmapSprite
  attr_reader :text

  def self.newWithSize(text, x, y, width, height, viewport = nil)
    sprite = self.new(width, height, viewport)
    sprite.x, sprite.y = x, y
    sprite.text = text
    return sprite
  end

  def baseColor=(color); @baseColor = color; refresh; end
  def shadowColor=(color); @shadowColor = color; refresh; end
  def windowskin=(skin); end

  def text=(value)
    return if @text == value
    @text = value
    @page = 0
    @elapsed = 0
    pbSetSystemFont(self.bitmap)
    chunks = getLineBrokenChunks(self.bitmap, value, self.bitmap.width - 4, nil, true)
    @line_height = 32
    @paged = chunks.any? { |chunk| chunk[2] >= 96 }
    if @paged
      self.bitmap.font.size = 25
      @line_height = 28
      chunks = getLineBrokenChunks(self.bitmap, value, self.bitmap.width - 4, nil, true)
    end
    lines = chunks.group_by { |chunk| chunk[2] / 32 }.values
    @pages = lines.each_slice(3).to_a
    @pages = [[]] if @pages.empty?
    refresh
  end

  def refresh
    return if !@pages || !@baseColor || !@shadowColor
    self.bitmap.clear
    @pages[@page].each_with_index do |line, i|
      line.each do |chunk|
        pbDrawShadowText(self.bitmap, chunk[1], i * @line_height,
                         chunk[3] + 4, @line_height, chunk[0], @baseColor, @shadowColor)
      end
    end
    if @pages.length > 1
      size = self.bitmap.font.size
      self.bitmap.font.size = 16
      self.bitmap.font.color = @baseColor
      self.bitmap.draw_text(0, 84, self.bitmap.width - 4, 16,
                            "#{@page + 1}/#{@pages.length}", 2)
      self.bitmap.font.size = size
    end
  end

  def update
    super
    return if !self.visible || !@pages || @pages.length <= 1
    @elapsed += 1
    if @elapsed >= Graphics.frame_rate * 7
      @elapsed = 0
      @page = (@page + 1) % @pages.length
      refresh
    end
  end
end
# END BAG DESCRIPTION PAGES
'''

def apply():
    for game in ('kanto', 'hoenn'):
        path = ROOT / 'repos' / game / REL
        raw = path.read_bytes()
        newline = '\r\n' if b'\r\n' in raw else '\n'
        text = raw.decode('utf-8').replace('\r\n', '\n')
        if '# BEGIN BAG DESCRIPTION PAGES' in text:
            text = re.sub(r'\n# BEGIN BAG DESCRIPTION PAGES.*?# END BAG DESCRIPTION PAGES\n', lambda m: CLASS, text, flags=re.S)
        else:
            text = text.replace('class PokemonBag_Scene\n', CLASS + '\nclass PokemonBag_Scene\n', 1)
        old = '@sprites["itemtext"] = Window_UnformattedTextPokemon.newWithSize("",\n       72, 270, Graphics.width - 72 - 24, 128, @viewport)'
        new = '@sprites["itemtext"] = BagDescriptionSprite.newWithSize("",\n       88, 284, Graphics.width - 88 - 20, Graphics.height - 284, @viewport)'
        assert old in text or new in text, game
        text = text.replace(old, new)
        result = text.replace('\n', newline).encode('utf-8')
        if result != raw:
            path.write_bytes(result)
        print(f'{game}: descripciones de mochila completas, dentro del panel.')

if __name__ == '__main__':
    apply()
