
LOCALIZABLE_GRAPHICS_FOLDERS = ["Pictures","Titles"]
LOCALIZABLE_GRAPHICS_REGEX = /Graphics\/(#{LOCALIZABLE_GRAPHICS_FOLDERS.map { |f| Regexp.escape(f) }.join("|")})(\/|$)/i

LOCALIZED_GRAPHICS_FOLDERS = {
  :FRENCH  => "Graphics/Localized/fr",
  :SPANISH => "Graphics/Localized/es",
  :CHINESE => "Graphics/Localized/zh"
}

def pbLocalizedBitmapFilename(original_filename)
  language = getCurrentLanguage
  return original_filename if language == :ENGLISH
  folder = LOCALIZED_GRAPHICS_FOLDERS[language]
  return original_filename if !folder
  return original_filename if original_filename !~ LOCALIZABLE_GRAPHICS_REGEX

  graphics_match = LOCALIZABLE_GRAPHICS_REGEX.match(original_filename)
  canonical_folder = LOCALIZABLE_GRAPHICS_FOLDERS.find { |name| name.casecmp(graphics_match[1]) == 0 }
  localized_filename = original_filename.sub(LOCALIZABLE_GRAPHICS_REGEX,
    "#{folder}/#{canonical_folder}#{graphics_match[2]}")
  ext_match = localized_filename.match(KNOWN_BITMAP_EXTENSIONS)
  localized_noext = localized_filename.sub(KNOWN_BITMAP_EXTENSIONS, "")

  found = false
  RTP.eachPathFor(localized_noext) { |path|
    if ext_match
      found = true if pbTryString(path + ext_match[0])
    else
      found = true if pbTryString(path + ".png")
      found = true if !found && pbTryString(path + ".gif")
      found = true if !found && pbTryString(path + ".dat")
    end
    break if found
  }

  return found ? localized_filename : original_filename
end


def getCurrentLanguage
  return :ENGLISH unless $PokemonSystem&.language
  lang_entry = Settings::LANGUAGES[Settings::GAME_ID]&.[]($PokemonSystem.language)
  return :ENGLISH unless lang_entry
  case lang_entry[1]
  when "english.dat"
    return :ENGLISH
  when "french.dat"
    return :FRENCH
  when "spanish.dat"
    return :SPANISH
  when "chinese.dat"
    return :CHINESE
  end
  return :ENGLISH
end
