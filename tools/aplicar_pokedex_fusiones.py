"""Activa las entradas revisadas del idioma y ajusta sus páginas sin recortarlas.

Cambios reproducibles en ambos juegos; no modifica textos, sprites ni autores
de los JSON que descarga el juego. Las traducciones se generan en spanish.dat.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REL = Path('Data/Scripts/016_UI/Pokedex/004_UI_Pokedex_Entry.rb')

OLD_PAGES = '''  def splitTextIntoPages(text, max_chars_per_page)
    words = text.split
    pages = []
    current_page = ""

    words.each do |word|
      if current_page.length + word.length + 1 > max_chars_per_page
        pages << current_page.strip
        current_page = word
      else
        current_page += " " unless current_page.empty?
        current_page += word
      end
    end

    pages << current_page.strip unless current_page.empty?
    pages
  end'''

NEW_PAGES = '''  def splitTextIntoPages(text)
    # Measure with the actual overlay font; reserve the fourth line for paging.
    bitmap = @sprites["overlay"].bitmap
    max_width = Graphics.width - 88
    lines = []
    current_line = ""
    text.split.each do |word|
      candidate = current_line.empty? ? word : current_line + " " + word
      if !current_line.empty? && bitmap.text_size(candidate).width > max_width
        lines << current_line
        current_line = word
      else
        current_line = candidate
      end
      # An unusually long unbroken word must not overflow the text panel.
      if bitmap.text_size(current_line).width > max_width
        fragment = ""
        current_line.each_char do |char|
          if !fragment.empty? && bitmap.text_size(fragment + char).width > max_width
            lines << fragment
            fragment = char
          else
            fragment += char
          end
        end
        current_line = fragment
      end
    end
    lines << current_line unless current_line.empty?
    pages = lines.each_slice(3).map { |page| page.join("\\n") }
    pages = [""] if pages.empty?
    @entry_pages_count = pages.length
    return pages
  end'''

OLD_ENTRIES = '''      return entries.map { |entry| [entry["entry"], entry["author"]] }'''
NEW_ENTRIES = '''      # Translate before substituting POKENAME; preserve each original author.
      localized = entries.select { |entry|
        original = entry["entry"].gsub(/[[:space:]]+/, " ").strip
        _INTL(original) != original
      }
      entries = localized unless localized.empty?
      return entries.map { |entry|
        original = entry["entry"].gsub(/[[:space:]]+/, " ").strip
        [_INTL(original), entry["author"]]
      }'''

def apply():
    for game in ('kanto', 'hoenn'):
        path = ROOT / 'repos' / game / REL
        raw = path.read_bytes()
        newline = '\r\n' if b'\r\n' in raw else '\n'
        source = raw.decode('utf-8').replace('\r\n', '\n')
        source = source.replace('original = entry["entry"].gsub(/\\s+/, " ").strip',
                                'original = entry["entry"].gsub(/[[:space:]]+/, " ").strip')
        replacements = [
            ('  def drawEntryText(overlay, species_data, reloading = false)\n    baseColor',
             '  def drawEntryText(overlay, species_data, reloading = false)\n    @entry_text = nil unless reloading\n    baseColor'),
            ('    @entry_author = nil\n    pbUpdateDummyPokemon',
             '    @entry_author = nil unless reloading\n    pbUpdateDummyPokemon'),
            ('      customEntry, entryAuthor = getCustomEntryText(species_data)',
             '''      # Keep the same description and credit when turning its pages.
      if reloading && @entry_text
        customEntry, entryAuthor = @entry_text, @entry_author
      else
        customEntry, entryAuthor = getCustomEntryText(species_data)
      end'''),
            ('    max_chars_per_page = 150\n    pages = splitTextIntoPages(entryText, max_chars_per_page)',
             '    pages = splitTextIntoPages(entryText)'),
            (OLD_ENTRIES, NEW_ENTRIES),
            (OLD_PAGES, NEW_PAGES),
            ('    @entry_page = 0 if !@entry_page || pages.length == 1',
             '    @entry_page = (@entry_page || 0) % pages.length'),
            ('    @entry_page = @entry_page == 1 ? 0 : 1',
             '    @entry_page = ((@entry_page || 0) + 1) % (@entry_pages_count || 1)'),
            ('  def splitTextIntoPages(text, max_chars_per_page)',
             '  def splitTextIntoPages(text)'),
        ]
        for old, new in replacements:
            if new in source:
                continue
            assert source.count(old) == 1, f'Código original distinto: {game}, {old[:70]}'
            source = source.replace(old, new)
        result = source.replace('\n', newline).encode('utf-8')
        if result != raw:
            path.write_bytes(result)
        print(f'{game}: lectura traducida y páginas medidas con la fuente real.')

if __name__ == '__main__':
    apply()
