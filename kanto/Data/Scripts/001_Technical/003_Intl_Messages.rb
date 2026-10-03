def pbAddScriptTexts(items, script)
  script.force_encoding(Encoding::UTF_8)
  script.scan(/(?:_I|sign)\s*\(\s*\"((?:[^\\\"]*\\\"?)*[^\"]*)\"/) do |s|
    string = s[0]
    string.gsub!(/\\\"/, "\"")
    string.gsub!(/\\\\/, "\\")
    items.push(string)
  end
end

def pbAddRgssScriptTexts(items, script)
  script.force_encoding(Encoding::UTF_8)
  script.scan(/(?:_INTL|_ISPRINTF)\s*\(\s*\"((?:[^\\\"]*\\\"?)*[^\"]*)\"/) do |s|
    string = s[0]
    string.gsub!(/\\r/, "\r")
    string.gsub!(/\\n/, "\n")
    string.gsub!(/\\1/, "\1")
    string.gsub!(/\\\"/, "\"")
    string.gsub!(/\\\\/, "\\")
    items.push(string)
  end
end

def pbSetTextMessages
  Graphics.update
  begin
    t = System.uptime
    texts = []
    # Get script texts from Scripts.rxdata
    $RGSS_SCRIPTS.each do |script|
      if System.uptime - t >= 5
        t += 5
        Graphics.update
      end
      scr = Zlib::Inflate.inflate(script[2])
      pbAddRgssScriptTexts(texts, scr)
    end
    Dir.all("Data/Scripts").each do |script_file|
      if System.uptime - t >= 5
        t += 5
        Graphics.update
      end
      File.open(script_file, "rb") do |f|
        pbAddRgssScriptTexts(texts, f.read)
      end
    end
    # Must add messages because this code is used by both game system and Editor
    MessageTypes.addMessagesAsHash(MessageTypes::ScriptTexts, texts)
    commonevents = load_data("Data/CommonEvents.rxdata")
    items = []
    choices = []
    for event in commonevents.compact
      if Time.now.to_i - t >= 5
        t = Time.now.to_i
        Graphics.update
      end
      begin
        neednewline = false
        lastitem = ""
        for j in 0...event.list.size
          list = event.list[j]
          if neednewline && list.code != 401
            if lastitem != ""
              lastitem.gsub!(/([^\.\!\?])\s\s+/) { |m| $1 + " " }
              items.push(lastitem)
              lastitem = ""
            end
            neednewline = false
          end
          if list.code == 101
            lastitem += "#{list.parameters[0]}"
            neednewline = true
          elsif list.code == 102
            for k in 0...list.parameters[0].length
              choices.push(list.parameters[0][k])
            end
            neednewline = false
          elsif list.code == 401
            lastitem += " " if lastitem != ""
            lastitem += "#{list.parameters[0]}"
            neednewline = true
          elsif list.code == 355 || list.code == 655
            pbAddScriptTexts(items, list.parameters[0])
          elsif list.code == 111 && list.parameters[0] == 12
            pbAddScriptTexts(items, list.parameters[1])
          elsif list.code == 209
            route = list.parameters[1]
            for k in 0...route.list.size
              if route.list[k].code == 45
                pbAddScriptTexts(items, route.list[k].parameters[0])
              end
            end
          end
        end
        if neednewline
          if lastitem != ""
            items.push(lastitem)
            lastitem = ""
          end
        end
      end
    end
    if Time.now.to_i - t >= 5
      t = Time.now.to_i
      Graphics.update
    end
    items |= []
    choices |= []
    items.concat(choices)
    MessageTypes.setMapMessagesAsHash(0, items)
    mapinfos = pbLoadMapInfos
    mapnames = []
    for id in mapinfos.keys
      mapnames[id] = mapinfos[id].name
    end
    MessageTypes.setMessages(MessageTypes::MapNames, mapnames)
    for id in mapinfos.keys
      if Time.now.to_i - t >= 5
        t = Time.now.to_i
        Graphics.update
      end
      filename = sprintf("Data/Map%03d.rxdata", id)
      next if !pbRgssExists?(filename)
      map = load_data(filename)
      items = []
      choices = []
      for event in map.events.values
        if Time.now.to_i - t >= 5
          t = Time.now.to_i
          Graphics.update
        end
        begin
          for i in 0...event.pages.size
            neednewline = false
            lastitem = ""
            for j in 0...event.pages[i].list.size
              list = event.pages[i].list[j]
              if neednewline && list.code != 401
                if lastitem != ""
                  lastitem.gsub!(/([^\.\!\?])\s\s+/) { |m| $1 + " " }
                  items.push(lastitem)
                  lastitem = ""
                end
                neednewline = false
              end
              if list.code == 101
                lastitem += "#{list.parameters[0]}"
                neednewline = true
              elsif list.code == 102
                for k in 0...list.parameters[0].length
                  choices.push(list.parameters[0][k])
                end
                neednewline = false
              elsif list.code == 401
                lastitem += " " if lastitem != ""
                lastitem += "#{list.parameters[0]}"
                neednewline = true
              elsif list.code == 355 || list.code == 655
                pbAddScriptTexts(items, list.parameters[0])
              elsif list.code == 111 && list.parameters[0] == 12
                pbAddScriptTexts(items, list.parameters[1])
              elsif list.code == 209
                route = list.parameters[1]
                for k in 0...route.list.size
                  if route.list[k].code == 45
                    pbAddScriptTexts(items, route.list[k].parameters[0])
                  end
                end
              end
            end
            if neednewline
              if lastitem != ""
                items.push(lastitem)
                lastitem = ""
              end
            end
          end
        end
      end
      if Time.now.to_i - t >= 5
        t = Time.now.to_i
        Graphics.update
      end
      items |= []
      choices |= []
      items.concat(choices)
      MessageTypes.setMapMessagesAsHash(id, items)
      if Time.now.to_i - t >= 5
        t = Time.now.to_i
        Graphics.update
      end
    end
    pbAddTrainerTextMessages
    pbAddOutfitTextMessages
  rescue Hangup
  end
  Graphics.update
end


def pbAddTrainerTextMessages
  names      = []
  loseTexts  = []
  speeches   = []
  infoTexts   = []
  GameData::Trainer.each do |trainer|
    names.push(trainer.real_name)

    loseTexts.push(trainer.real_lose_text)
    loseTexts.push(trainer.loseText_rematch) if trainer.loseText_rematch
    loseTexts.push(trainer.loseText_rematch_double) if trainer.loseText_rematch_double

    speeches.push(trainer.battleText) if trainer.battleText
    speeches.push(trainer.preRematchText) if trainer.preRematchText
    speeches.push(trainer.preRematchText_caught) if trainer.preRematchText_caught
    speeches.push(trainer.preRematchText_evolved) if trainer.preRematchText_evolved
    speeches.push(trainer.preRematchText_fused) if trainer.preRematchText_fused
    speeches.push(trainer.preRematchText_unfused) if trainer.preRematchText_unfused
    speeches.push(trainer.preRematchText_reversed) if trainer.preRematchText_reversed
    speeches.push(trainer.preRematchText_gift) if trainer.preRematchText_gift

    infoTexts.push(trainer.infoText) if trainer.infoText
  end
  MessageTypes.addMessagesAsHash(MessageTypes::TrainerNames, names)
  MessageTypes.addMessagesAsHash(MessageTypes::TrainerLoseText, loseTexts)
  MessageTypes.addMessagesAsHash(MessageTypes::BeginSpeech, speeches)
  MessageTypes.addMessagesAsHash(MessageTypes::TrainerInfoText, infoTexts)
end

def pbCollectOutfitTexts(obj, texts)
  case obj
  when Hash
    texts << obj["name"] if obj["name"].is_a?(String)
    texts << obj["description"] if obj["description"].is_a?(String)
    obj.each_value { |v| pbCollectOutfitTexts(v, texts) }
  when Array
    obj.each { |v| pbCollectOutfitTexts(v, texts) }
  end
end

def pbAddOutfitTextMessages
  texts = []

  files = [
    Settings::CLOTHES_DATA_PATH,
    Settings::HAIRSTYLE_DATA_PATH,
    Settings::HATS_DATA_PATH
  ]

  files.each do |file|
    json_data = File.read(file)
    data = HTTPLite::JSON.parse(json_data)

    data.each do |entry|
      texts << entry["name"] if entry["name"]
      texts << entry["description"] if entry["description"]
    end
  end

  MessageTypes.addMessagesAsHash(MessageTypes::OutfitTexts, texts)
end

def pbEachIntlSection(file)
  lineno = 1
  re = /^\s*\[\s*([^\]]+)\s*\]\s*$/
  havesection = false
  sectionname = nil
  lastsection = []
  file.each_line { |line|
    if lineno == 1 && line[0].ord == 0xEF && line[1].ord == 0xBB && line[2].ord == 0xBF
      line = line[3, line.length - 3]
    end
    if !line[/^\#/] && !line[/^\s*$/]
      if line[re]
        if havesection
          yield lastsection, sectionname
        end
        lastsection.clear
        sectionname = $~[1]
        havesection = true
      else
        if sectionname == nil
          raise _INTL("Expected a section at the beginning of the file (line {1})", lineno)
        end
        lastsection.push(line.gsub(/\s+$/, ""))
      end
    end
    lineno += 1
    if lineno % 500 == 0
      Graphics.update
    end
  }
  if havesection
    yield lastsection, sectionname
  end
end

def pbGetText(infile)
  begin
    file = File.open(infile, "rb")
  rescue
    raise _INTL("Can't find {1}", infile)
  end
  intldat = []
  begin
    pbEachIntlSection(file) { |section, name|
      next if section.length == 0
      if !name[/^([Mm][Aa][Pp])?(\d+)$/]
        raise _INTL("Invalid section name {1}", name)
      end
      ismap = $~[1] && $~[1] != ""
      id = $~[2].to_i
      itemlength = 0
      if section[0][/^\d+$/]
        intlhash = []
        itemlength = 3
        if ismap
          raise _INTL("Section {1} can't be an ordered list (section was recognized as an ordered list because its first line is a number)", name)
        end
        if section.length % 3 != 0
          raise _INTL("Section {1}'s line count is not divisible by 3 (section was recognized as an ordered list because its first line is a number)", name)
        end
      else
        intlhash = OrderedHash.new
        itemlength = 2
        if section.length % 2 != 0
          raise _INTL("Section {1} has an odd number of entries (section was recognized as a hash because its first line is not a number)", name)
        end
      end
      i = 0
      loop do break unless i < section.length
        if itemlength == 3
        if !section[i][/^\d+$/]
          raise _INTL("Expected a number in section {1}, got {2} instead", name, section[i])
        end
        key = section[i].to_i
        i += 1
      else
        key = MessageTypes.denormalizeValue(section[i])
      end
        intlhash[key] = MessageTypes.denormalizeValue(section[i + 1])
        i += 2       end
      if ismap
        intldat[0] = [] if !intldat[0]
        intldat[0][id] = intlhash
      else
        intldat[id] = intlhash
      end
    }
  ensure
    file.close
  end
  return intldat
end

def pbCompileText
  outfile = File.open("intl.dat", "wb")
  begin
    intldat = pbGetText("intl.txt")
    Marshal.dump(intldat, outfile)
  rescue
    raise
  ensure
    outfile.close
  end
end

class OrderedHash < Hash
  def initialize
    @keys = []
    super
  end

  def keys
    return @keys.clone
  end

  def inspect
    str = "{"
    for i in 0...@keys.length
      str += ", " if i > 0
      str += @keys[i].inspect + "=>" + self[@keys[i]].inspect
    end
    str += "}"
    return str
  end

  alias :to_s :inspect

  def []=(key, value)
    oldvalue = self[key]
    if !oldvalue && value
      @keys.push(key)
    elsif !value
      @keys |= []
      @keys -= [key]
    end
    return super(key, value)
  end

  def self._load(string)
    ret = self.new
    keysvalues = Marshal.load(string)
    keys = keysvalues[0]
    values = keysvalues[1]
    for i in 0...keys.length
      ret[keys[i]] = values[i]
    end
    return ret
  end

  def _dump(_depth = 100)
    values = []
    for key in @keys
      values.push(self[key])
    end
    return Marshal.dump([@keys, values])
  end
end

class Messages
  def initialize(filename = nil, delayLoad = false)
    @messages = nil
    @filename = filename
    if @filename && !delayLoad
      loadMessageFile(@filename)
    end
  end

  def delayedLoad
    if @filename && !@messages
      loadMessageFile(@filename)
      @filename = nil
    end
  end

  def self.stringToKey(str)
    if str && str[/[\r\n\t\1]|^\s+|\s+$|\s{2,}/]
      key = str.clone
      key.gsub!(/^\s+/, "")
      key.gsub!(/\s+$/, "")
      key.gsub!(/\s{2,}/, " ")
      return key
    end
    return str
  end

  def self.normalizeValue(value)
    if value[/[\r\n\t\x01]|^[\[\]]/]
      ret = value.clone
      ret.gsub!(/\r/, "<<r>>")
      ret.gsub!(/\n/, "<<n>>")
      ret.gsub!(/\t/, "<<t>>")
      ret.gsub!(/\[/, "<<[>>")
      ret.gsub!(/\]/, "<<]>>")
      ret.gsub!(/\x01/, "<<1>>")
      return ret
    end
    return value
  end

  def self.denormalizeValue(value)
    if value[/<<[rnt1\[\]]>>/]
      ret = value.clone
      ret.gsub!(/<<1>>/, "\1")
      ret.gsub!(/<<r>>/, "\r")
      ret.gsub!(/<<n>>/, "\n")
      ret.gsub!(/<<\[>>/, "[")
      ret.gsub!(/<<\]>>/, "]")
      ret.gsub!(/<<t>>/, "\t")
      return ret
    end
    return value
  end

  def self.writeObject(f, msgs, secname, origMessages = nil)
    return if !msgs
    if msgs.is_a?(Array)
      f.write("[#{secname}]\r\n")
      for j in 0...msgs.length
        next if nil_or_empty?(msgs[j])
        value = Messages.normalizeValue(msgs[j])
        origValue = ""
        if origMessages
          origValue = Messages.normalizeValue(origMessages.get(secname, j))
        else
          origValue = Messages.normalizeValue(MessageTypes.get(secname, j))
        end
        f.write("#{j}\r\n")
        f.write(origValue + "\r\n")
        f.write(value + "\r\n")
      end
    elsif msgs.is_a?(OrderedHash)
      f.write("[#{secname}]\r\n")
      keys = msgs.keys
      for key in keys
        next if nil_or_empty?(msgs[key])
        value = Messages.normalizeValue(msgs[key])
        valkey = Messages.normalizeValue(key)
        # key is already serialized
        f.write(valkey + "\r\n")
        f.write(value + "\r\n")
      end
    end
  end

  def messages
    return @messages || []
  end

  def extract(outfile)
    #    return if !@messages
    origMessages = Messages.new("Data/messages.dat")
    File.open(outfile, "wb") { |f|
      f.write(0xef.chr)
      f.write(0xbb.chr)
      f.write(0xbf.chr)
      f.write("# To localize this text for a particular language, please\r\n")
      f.write("# translate every second line of this file.\r\n")
      if origMessages.messages[0]
        for i in 0...origMessages.messages[0].length
          msgs = origMessages.messages[0][i]
          Messages.writeObject(f, msgs, "Map#{i}", origMessages)
        end
      end
      for i in 1...origMessages.messages.length
        msgs = origMessages.messages[i]
        Messages.writeObject(f, msgs, i, origMessages)
      end
    }
  end

  def setMessages(type, array)
    @messages = [] if !@messages
    arr = []
    for i in 0...array.length
      arr[i] = (array[i]) ? array[i] : ""
    end
    @messages[type] = arr
  end

  def addMessages(type, array)
    @messages = [] if !@messages
    arr = (@messages[type]) ? @messages[type] : []
    for i in 0...array.length
      arr[i] = (array[i]) ? array[i] : (arr[i]) ? arr[i] : ""
    end
    @messages[type] = arr
  end

  def self.createHash(_type, array)
    arr = OrderedHash.new
    for i in 0...array.length
      if array[i]
        key = Messages.stringToKey(array[i])
        arr[key] = array[i]
      end
    end
    return arr
  end

  def self.addToHash(_type, array, hash)
    hash = OrderedHash.new if !hash
    for i in 0...array.length
      if array[i]
        key = Messages.stringToKey(array[i])
        hash[key] = array[i]
      end
    end
    return hash
  end

  def setMapMessagesAsHash(type, array)
    @messages = [] if !@messages
    @messages[0] = [] if !@messages[0]
    @messages[0][type] = Messages.createHash(type, array)
  end

  def addMapMessagesAsHash(type, array)
    @messages = [] if !@messages
    @messages[0] = [] if !@messages[0]
    @messages[0][type] = Messages.addToHash(type, array, @messages[0][type])
  end

  def setMessagesAsHash(type, array)
    @messages = [] if !@messages
    @messages[type] = Messages.createHash(type, array)
  end

  def addMessagesAsHash(type, array)
    @messages = [] if !@messages
    @messages[type] = Messages.addToHash(type, array, @messages[type])
  end

  def saveMessages(filename = nil)
    filename = "Data/messages.dat" if !filename
    raw = Marshal.dump(@messages)
    File.open(filename, "wb") { |f| f.write(Encryption.xor(raw)) }
  end

  def loadMessageFile(filename)
    begin
      raw = File.open(filename, "rb") { |f| f.read }
      begin
        @messages = Marshal.load(Encryption.xor(raw))
      rescue TypeError, ArgumentError
        @messages = Marshal.load(raw)  # fallback for old unencrypted file
      end
      if !@messages.is_a?(Array)
        @messages = nil
        raise "Corrupted data"
      end
      return @messages
    rescue
      @messages = nil
      return nil
    end
  end

  def set(type, id, value)
    delayedLoad
    return if !@messages
    return if !@messages[type]
    @messages[type][id] = value
  end

  def getCount(type)
    delayedLoad
    return 0 if !@messages
    return 0 if !@messages[type]
    return @messages[type].length
  end

  def get(type, id)
    delayedLoad
    return "" if !@messages
    return "" if !@messages[type]
    return "" if !@messages[type][id]
    return @messages[type][id]
  end

  def getFromHash(type, key)
    delayedLoad
    return key if !@messages || !@messages[type] || !key
    id = Messages.stringToKey(key)
    return key if !@messages[type][id]
    return @messages[type][id]
  end

  def getFromMapHash(type, key)
    delayedLoad
    return key if !@messages
    return key if !@messages[0]
    return key if !@messages[0][type] && !@messages[0][0]
    id = Messages.stringToKey(key)
    if @messages[0][type] && @messages[0][type][id]
      return @messages[0][type][id]
    elsif @messages[0][0] && @messages[0][0][id]
      return @messages[0][0][id]
    end
    return key
  end
end

# Translations may contain gender markers like "[[o|a]]" (masculine|feminine),
# resolved here with the player's gender when the text is looked up.
def pbResolveGenderMarkers(str)
  return str if !str.is_a?(String) || !str.include?("[[")
  female = $Trainer && $Trainer.respond_to?(:female?) && $Trainer.female?
  return str.gsub(/\[\[([^\|\[\]]*)\|([^\[\]]*)\]\]/) { female ? $2 : $1 }
end


# BEGIN SPANISH ITEM CONCORDANCE
SPANISH_ITEM_FORMS = {}
["Abono Brote", "Abono Fijador", "Abono Fértil", "Abono Lento", "Abono Rápido", "Activaobjeto", "Adaptador de Red", "Amuleto", "Amuleto Iris", "Amuleto Oval", "Anillo de Oro", "Antihielo", "Antiparalizador", "Antiquemar", "Antídoto", "At. Especial X", "Ataque Esp. XX", "Ataque Esp. XXX", "Ataque Esp. XXXX", "Ataque X", "Ataque XX", "Ataque XXX", "Ataque XXXX", "Atuendo Favorito", "Blanco", "Bonguri Amarillo", "Bonguri Azul", "Bonguri Blanco", "Bonguri Negro", "Bonguri Rojo", "Bonguri Rosa", "Bonguri Verde", "Botón Escape", "Brazal", "Brazal Firme", "Brazal Recio", "Buscaobjetos", "Café", "Café con Leche", "Calcio", "Caramelo Exp.", "Caramelo Furia", "Caramelo Raro", "Carburante", "Carbón", "Cascabel Alivio", "Cascabel Concha", "Casco Dentado", "Chaleco Asalto", "Cinto Recio", "Cinturón Negro", "Colgante Viejo", "Collar de Diamantes", "Colmillo Agudo", "Colmillo de Dragón", "Corazón Dulce", "Cordón Unión", "Crítico X", "Cuaderno de Misiones", "Cubresuelos", "Depurador", "Despertar", "Diamante", "Diario de Misiones", "Diente Marino", "Disco Extraño", "Dulce de Nata", "EXP. Total", "Electrizador", "Elixir", "Elixir Máximo", "Emblema de Bronce", "Emblema de Oro", "Emblema de Plata", "Enlace de Caja", "Equipo de Buceo", "Equipo de Escalada", "Espejo del Sueño", "Espray", "Espray Involución", "Farol", "Fragmento Cometa", "Fusionador Infinito", "Fósil Aleta", "Fósil Coraza", "Fósil Cráneo", "Fósil Domo", "Fósil Garra", "Fósil Hélix", "Fósil Mandíbula", "Fósil Raíz", "Gen Furia", "Generador", "Globo Helio", "Habilitador", "Hechizo", "Hielo Perpetuo", "Hierro", "Hipermáximo", "Hueso Grueso", "Hueso Raro", "Huevo Suerte", "Imán", "Incienso Acua", "Incienso Duplo", "Incienso Floral", "Incienso Fusión", "Incienso Lento", "Incienso Marino", "Incienso Puro", "Incienso Raro", "Incienso Roca", "Incienso Suave", "Invertidor de ADN", "Kit de Tinte de Gorra", "Kit de Tinte de Ropa", "Lazo Destino", "Lodo Negro", "Magmatizador", "Mapa", "Mapa Viejo", "Menú Lujoso", "Menú Rocket", "Metrónomo", "Mineral Evol", "Monedero", "Musgo Brillante", "Muñeco Mareanie", "Más PP", "Más PS", "Necrozium", "Néctar Amarillo", "Néctar Azul", "Néctar Rojo", "Néctar Rosa", "Objeto desconocido", "Orbe Claro", "Orbe Oscuro", "Palo", "Paquete", "Paracontacto", "Pasaje Navel", "Pase Seagallop", "Pase de Tren", "Pañuelo Amarillo", "Pañuelo Azul", "Pañuelo Elección", "Pañuelo Rojo", "Pañuelo Rosa", "Pañuelo Verde", "Pañuelo de Seda", "Periscopio", "Petardo", "Pico", "Pico Afilado", "Piolet", "Plátano", "Plátano Dorado", "Poké Muñeco", "PokéNav", "Pokéradar", "Pokéseñuelo", "Polvo Brillo", "Polvo Curación", "Polvo Energía", "Polvo Estelar", "Polvo Metálico", "Polvo Plata", "Polvo Veloz", "Porcehelado", "Prisma Extraño", "Protector", "Puño Suerte", "Quitaestado", "Rastreador Clima", "Real Cobre", "Real Oro", "Real Plata", "Recuerdo Safari", "Refleluz", "Refresco", "Regalo", "Repartir Exp", "Repelente", "Repelente Máximo", "Restaurar Todo", "Revest. Metálico", "Revivir", "Revivir Máximo", "Rocío Bondad", "Rubí", "Saco Hollín", "Saco de Dormir", "Saco de Dormir Cómodo", "Saco de Dormir de Campo", "Seguro Debilidad", "Silbato de Emergencia", "Superfusionador", "Supermáximo", "Superrepelente", "Telescopio", "Teletransportador", "Tequila", "Ticket Barco", "Tiraobjeto", "Trozo Estrella", "Tubo Pokécubos", "Tubérculo", "Uniforme Rocket", "Uniforme del Equipo Aqua", "Uniforme del Equipo Magma", "Visor Silph", "Zafiro", "Zahorí", "Zinc", "Zumo de Baya", "objeto_desconocido", "Ámbar Viejo", "Éter", "Éter Máximo"].each { |name| SPANISH_ITEM_FORMS[name] = 0 }
["Acopio Ball", "Aleta de Seadra", "Amigo Ball", "Amor Ball", "Arena Fina", "Ball Ascua", "Ball Brillo", "Ball Caramelo", "Ball Chispa", "Ball Escarcha", "Ball Estado", "Ball Fusión", "Ball GS", "Ball Género", "Ball Habilidad", "Ball Impulso", "Ball Invisible", "Ball Perfecta", "Ball Pura", "Ball Rocket", "Ball Tóxica", "Ball Virus", "Banda Aguante", "Banda Atadura", "Banda Recia", "Bandera Blanca", "Barrita Plus", "Baya Acardo", "Baya Alcho", "Baya Algama", "Baya Andano", "Baya Ango", "Baya Anjiro", "Baya Aostan", "Baya Arabol", "Baya Aranja", "Baya Aricoc", "Baya Aslac", "Baya Atania", "Baya Baribá", "Baya Caoca", "Baya Caquic", "Baya Chilan", "Baya Chiri", "Baya Dillo", "Baya Drasi", "Baya Enigma", "Baya Frambu", "Baya Gonlan", "Baya Grana", "Baya Gualot", "Baya Guaya", "Baya Hibis", "Baya Higog", "Baya Ispero", "Baya Jaboca", "Baya Kebia", "Baya Kouba", "Baya Lagro", "Baya Latano", "Baya Lichi", "Baya Magua", "Baya Mais", "Baya Meloc", "Baya Meluce", "Baya Monli", "Baya Oram", "Baya Pabaya", "Baya Pasio", "Baya Payapa", "Baya Peragu", "Baya Perasi", "Baya Pinia", "Baya Pinkan", "Baya Plama", "Baya Pomaro", "Baya Rautan", "Baya Rimoya", "Baya Rudion", "Baya Safre", "Baya Sambia", "Baya Tamar", "Baya Tamate", "Baya Uvav", "Baya Wikano", "Baya Wiki", "Baya Yapati", "Baya Yecana", "Baya Zanama", "Baya Zidra", "Baya Ziuela", "Baya Zonlan", "Baya Zreza", "Bici", "Bici Acrobática", "Bici Veloz", "Bici de Carreras", "Bola Férrea", "Bola Luminosa", "Bola de Humo", "Bola de Nieve", "Bota Vieja", "Buceo Ball", "Car. Corazón", "Car. Mosaico", "Car. Sideral", "Carretilla", "Carta Acero", "Carta Aérea", "Carta Flores", "Carta Fuego", "Carta Hierba", "Carta Mina", "Carta Nieve", "Carta Pared", "Carta Pompas", "Carta a Máximo", "Carta de Amor", "Caña Buena", "Caña Vieja", "Cebo Ball", "Ceniza Sagrada", "Cerveza", "Cinta Aguante", "Cinta Elección", "Cinta Experto", "Cinta Fuerte", "Cola Plúmbea", "Cola Skitty", "Cola Slowpoke", "Competi Ball", "Concha Cardumen", "Corona Antigua", "Cosa", "CrioROM", "Cuchara Torcida", "Cuerda Huida", "Cura Total", "Cáps. Habilidad", "Cápsula Secreta", "Def. Especial X", "Defensa Esp. XX", "Defensa Esp. XXX", "Defensa Esp. XXXX", "Defensa X", "Defensa XX", "Defensa XXX", "Defensa XXXX", "Diamansfera", "Dinamita", "Efigie Antigua", "Ensueño Ball", "Escama Bella", "Escama Corazón", "Escama Dragón", "Escama Marina", "Esmeralda", "Flauta Amarilla", "Flauta Azul", "Flauta Azur", "Flauta Blanca", "Flauta Negra", "Flauta Roja", "Flecha Venenosa", "Franja Recia", "Fruta Extraña", "FulgoROM", "Gafa Protectora", "Galleta Lava", "Garra Afilada", "Garra Garfio", "Garra Rápida", "Gema Acero", "Gema Agua", "Gema Bicho", "Gema Dragón", "Gema Eléctrica", "Gema Fantasma", "Gema Fuego", "Gema Hada", "Gema Hielo", "Gema Lucha", "Gema Normal", "Gema Planta", "Gema Psíquica", "Gema Roca", "Gema Siniestra", "Gema Tierra", "Gema Veneno", "Gema Voladora", "Gloria Ball", "Griseosfera", "HidroROM", "Hierba Blanca", "Hierba Mental", "Hierba Revivir", "Hierba Única", "Hiperpoción", "Honor Ball", "Identificación Rocket", "Incubadora", "Leche Mu-mu", "Lente Recia", "Limonada", "Llamasfera", "Llave Ascensor", "Llave Magnética", "Llave de la Central", "Llave del Capitán", "Llave del Dormitorio", "Lujo Ball", "Luna Ball", "Lupa", "Lustresfera", "MO01", "MO02", "MO03", "MO04", "MO05", "MO06", "MO07", "MO08", "MO09", "MO10", "MO11", "MT00", "MT01", "MT02", "MT03", "MT04", "MT05", "MT06", "MT07", "MT08", "MT09", "MT10", "MT100", "MT101", "MT102", "MT103", "MT104", "MT105", "MT106", "MT107", "MT108", "MT109", "MT11", "MT110", "MT111", "MT112", "MT113", "MT114", "MT115", "MT116", "MT117", "MT118", "MT119", "MT12", "MT120", "MT121", "MT122", "MT13", "MT14", "MT15", "MT16", "MT17", "MT18", "MT19", "MT20", "MT21", "MT22", "MT23", "MT24", "MT25", "MT26", "MT27", "MT28", "MT29", "MT30", "MT31", "MT32", "MT33", "MT34", "MT35", "MT36", "MT37", "MT38", "MT39", "MT40", "MT41", "MT42", "MT43", "MT44", "MT45", "MT46", "MT47", "MT48", "MT49", "MT50", "MT51", "MT52", "MT53", "MT54", "MT55", "MT56", "MT57", "MT58", "MT59", "MT60", "MT61", "MT62", "MT63", "MT64", "MT65", "MT66", "MT67", "MT68", "MT69", "MT70", "MT71", "MT72", "MT73", "MT74", "MT75", "MT76", "MT77", "MT78", "MT79", "MT80", "MT81", "MT82", "MT83", "MT84", "MT85", "MT86", "MT87", "MT88", "MT89", "MT90", "MT91", "MT92", "MT93", "MT94", "MT95", "MT96", "MT97", "MT98", "MT99", "Malla Ball", "Master Ball", "Maxipepita", "Medalla de Dem", "Mejora", "Miel", "Miniseta", "Mochila Propulsora", "Moneda Amuleto", "Muda Concha", "Máscara de Gas", "Nerviosfera", "Nido Ball", "Nivel Ball", "Ocaso Ball", "Parte Amarilla", "Parte Azul", "Parte Roja", "Parte Verde", "Pata de Mankey", "Pepita", "Perla", "Perla Grande", "Pesa Recia", "Peso Ball", "Piedra Agua", "Piedra Alba", "Piedra Dura", "Piedra Día", "Piedra Espíritu", "Piedra Eterna", "Piedra Fuego", "Piedra Género", "Piedra Hielo", "Piedra Hoja", "Piedra Imán", "Piedra Lunar", "Piedra Niebla", "Piedra Noche", "Piedra Oval", "Piedra Pómez", "Piedra Solar", "Piedra Trueno", "Pieza de Nave", "Pila", "PiroROM", "Pizza", "Pluma Aguante", "Pluma Bonita", "Pluma Corrupta", "Pluma Genio", "Pluma Listeza", "Pluma Lunar", "Pluma Músculo", "Pluma Salud", "Pluma Ímpetu", "Poción", "Poción Máxima", "Poción Secreta", "Poké Ball", "Poké Flauta", "Pokédex", "Precisión X", "Precisión XX", "Precisión XXX", "Precisión XXXX", "Protección X", "Proteína", "Punta ADN", "Rapid Ball", "Raíz Energía", "Raíz Grande", "Regadera", "Roca Calor", "Roca Helada", "Roca Lluvia", "Roca Suave", "Roca del Rey", "Safari Ball", "Sal Cardumen", "Sana Ball", "Sarta Perlas", "Semilla Bruma", "Semilla Electro", "Semilla Hierba", "Semilla Milagro", "Semilla Psique", "Seta Aroma", "Seta Grande", "Seta Venenosa", "Super Ball", "Supercaña", "Superincubadora", "Superpoción", "Tabla Acero", "Tabla Bicho", "Tabla Cielo", "Tabla Draco", "Tabla Duende", "Tabla Fuerte", "Tabla Helada", "Tabla Linfa", "Tabla Llama", "Tabla Mental", "Tabla Oscura", "Tabla Pradal", "Tabla Pétrea", "Tabla Terrax", "Tabla Terror", "Tabla Trueno", "Tabla Tóxica", "Tabla de Surf", "Tablilla Regi", "Tarjeta Roja", "Tela Terrible", "Toxiestrella", "Toxisfera", "Turno Ball", "Ultra Ball", "Velocidad X", "Velocidad XX", "Velocidad XXX", "Velocidad XXXX", "Veloz Ball", "Vidasfera", "Wailmegadera"].each { |name| SPANISH_ITEM_FORMS[name] = 1 }
["Abonos Fértiles", "Activaobjetos", "Adaptadores de Red", "Amuletos", "Amuletos Iris", "Amuletos Oval", "Anillos de Oro", "Antihielos", "Antiparalizadores", "Antiquemares", "Antídotos", "Ataques Esp. XX", "Ataques Esp. XXX", "Ataques Esp. XXXX", "Ataques Especiales X", "Ataques X", "Ataques XX", "Ataques XXX", "Ataques XXXX", "Atuendos Favoritos", "Blancos", "Bonguris Amarillos", "Bonguris Azules", "Bonguris Blancos", "Bonguris Negros", "Bonguris Rojos", "Bonguris Rosas", "Bonguris Verdes", "Botones Escape", "Brazales", "Brazales Firmes", "Brazales Recios", "Cafés", "Cafés con Leche", "Calcios", "Caramelos Exp.", "Caramelos Furia", "Caramelos Raros", "Carburantes", "Cascabeles Alivio", "Cascabeles Concha", "Cascos Dentados", "Chalecos Asalto", "Cintos Recios", "Cinturones Negros", "Colgantes Viejos", "Collares de Diamantes", "Colmillo Dragón", "Colmillos Agudos", "Corazones Dulces", "Cordones Unión", "Críticos X", "Cuadernos de Misiones", "Depuradores", "Despertares", "Diamantes", "Diarios de Misiones", "Dientes Marinos", "Discos Extraños", "Dulces de Nata", "EXP. Totales", "Electrizadores", "Elixires", "Elixires Máximos", "Emblemas de Bronce", "Emblemas de Oro", "Emblemas de Plata", "Enlaces de Caja", "Equipos de Buceo", "Equipos de Escalada", "Espejos del Sueño", "Espráis", "Espráis Involución", "Faroles", "Fragmentos Cometa", "Fusionadores Infinitos", "Fósiles Aleta", "Fósiles Coraza", "Fósiles Cráneo", "Fósiles Domo", "Fósiles Garra", "Fósiles Hélix", "Fósiles Mandíbula", "Fósiles Raíz", "Generadores", "Genes Furia", "Globos Helio", "Habilitadores", "Hechizos", "Hielos Perpetuos", "Hierros", "Hipermáximos", "Huesos Gruesos", "Huesos Raros", "Huevos Suerte", "Imanes", "Inciensos Acua", "Inciensos Duplos", "Inciensos Florales", "Inciensos Fusión", "Inciensos Lentos", "Inciensos Marinos", "Inciensos Puros", "Inciensos Raros", "Inciensos Roca", "Inciensos Suaves", "Invertidores de ADN", "Kits de Tinte de Gorra", "Kits de Tinte de Ropa", "Ladrillos", "Lazos Destino", "Lodos Negros", "Magmatizadores", "Mapas", "Mapas Viejos", "Menús Lujosos", "Menús Rocket", "Metrónomos", "Minerales Evol", "Monederos", "Musgos Brillantes", "Muñecos Mareanie", "Néctares Amarillos", "Néctares Azules", "Néctares Rojos", "Néctares Rosas", "Orbes Claros", "Orbes Oscuros", "PP Máximos", "Palos", "Paquetes", "Paracontactos", "Pasajes Navel", "Pases Seagallop", "Pases de Tren", "Pañuelos Amarillos", "Pañuelos Azules", "Pañuelos Elección", "Pañuelos Rojos", "Pañuelos Rosa", "Pañuelos Verdes", "Pañuelos de Seda", "Periscopios", "Petardos", "Picos", "Picos Afilados", "Piolets", "Plátanos", "Plátanos Dorados", "Poké Muñecos", "Pokéradares", "Pokéseñuelos", "Polvos Brillo", "Polvos Curación", "Polvos Estelares", "Porcehelados", "Prismas Extraños", "Protectores", "Puños Suerte", "Quitaestados", "Rastreadores Clima", "Reales Cobre", "Reales Oro", "Reales Plata", "Recuerdos MMMM", "Recuerdos Safari", "Refleluces", "Refrescos", "Regalos", "Repelentes", "Repelentes Máximos", "Restos", "Revest. Metálicos", "Rocíos Bondad", "Rubíes", "Sacos Hollín", "Sacos de Dormir", "Sacos de Dormir Cómodos", "Sacos de Dormir de Campo", "Seguros Debilidad", "Separadores Infinitos", "Silbatos de Emergencia", "Superfusionadores", "Supermáximos", "Superrepelentes", "Tablones de Madera", "Telescopios", "Teletransportadores", "Tequilas", "Tickets Barco", "Tiraobjetos", "Trozos Estrella", "Tubos Pokécubos", "Tubérculos", "Uniformes Rocket", "Uniformes del Equipo Aqua", "Uniformes del Equipo Magma", "Visores Silph", "Zafiros", "Zahoríes", "Zumos de Baya", "objeto_desconocidos", "Ámbares Viejos", "Éteres", "Éteres Máximos"].each { |name| SPANISH_ITEM_FORMS[name] = 2 }
["Acopio Balls", "Aletas de Seadra", "Algas", "Amigo Balls", "Amor Balls", "Balls Ascua", "Balls Brillo", "Balls Caramelo", "Balls Chispa", "Balls Escarcha", "Balls Estado", "Balls Fusión", "Balls GS", "Balls Género", "Balls Habilidad", "Balls Impulso", "Balls Invisibles", "Balls Perfectas", "Balls Puras", "Balls Rocket", "Balls Tóxicas", "Balls Virus", "Banda Focus", "Bandas Atadura", "Bandas Recias", "Banderas Blancas", "Barritas Plus", "Bayas Acardo", "Bayas Alcho", "Bayas Algama", "Bayas Andano", "Bayas Ango", "Bayas Anjiro", "Bayas Aostan", "Bayas Arabol", "Bayas Aranja", "Bayas Aricoc", "Bayas Aslac", "Bayas Atania", "Bayas Baribá", "Bayas Caoca", "Bayas Caquic", "Bayas Chilan", "Bayas Chiri", "Bayas Dillo", "Bayas Drasi", "Bayas Enigma", "Bayas Frambu", "Bayas Gonlan", "Bayas Grana", "Bayas Gualot", "Bayas Guaya", "Bayas Hibis", "Bayas Higog", "Bayas Ispero", "Bayas Jaboca", "Bayas Kebia", "Bayas Kouba", "Bayas Lagro", "Bayas Latano", "Bayas Lichi", "Bayas Magua", "Bayas Mais", "Bayas Meloc", "Bayas Meluce", "Bayas Monli", "Bayas Oram", "Bayas Pabaya", "Bayas Pasio", "Bayas Payapa", "Bayas Peragu", "Bayas Perasi", "Bayas Pinia", "Bayas Pinkan", "Bayas Plama", "Bayas Pomaro", "Bayas Rautan", "Bayas Rimoya", "Bayas Rudion", "Bayas Safre", "Bayas Sambia", "Bayas Tamar", "Bayas Tamate", "Bayas Uvav", "Bayas Wikano", "Bayas Wiki", "Bayas Yapati", "Bayas Yecana", "Bayas Zanama", "Bayas Zidra", "Bayas Ziuela", "Bayas Zonlan", "Bayas Zreza", "Bicis", "Bicis Acrobáticas", "Bicis Veloces", "Bicis de Carreras", "Bolas Férreas", "Bolas Luminosas", "Bolas de Humo", "Bolas de Nieve", "Botas Golbat", "Botas Mágicas", "Botas Viejas", "Buceo Balls", "Carretillas", "Cartas Acero", "Cartas Aéreas", "Cartas Corazón", "Cartas Flores", "Cartas Fuego", "Cartas Hierba", "Cartas Mina", "Cartas Mosaico", "Cartas Nieve", "Cartas Pared", "Cartas Pompas", "Cartas Sideral", "Cartas a Máximo", "Cartas de Amor", "Cañas Buenas", "Cañas Viejas", "Cebo Balls", "Cenizas Sagradas", "Cervezas", "Cinta Focus", "Cintas Elección", "Cintas Experto", "Cintas Fuertes", "Colas Plúmbeas", "Colas Skitty", "Colas Slowpoke", "Competi Balls", "Conchas Cardumen", "Coronas Antiguas", "Cosas", "Cucharas Torcidas", "Cuerdas Huida", "Curas Totales", "Cápsulas Habilidad", "Cápsulas Secretas", "Defensas Esp. XX", "Defensas Esp. XXX", "Defensas Esp. XXXX", "Defensas Especiales X", "Defensas X", "Defensas XX", "Defensas XXX", "Defensas XXXX", "Diamansferas", "Dinamitas", "Efigies Antiguas", "Ensueño Balls", "Escamas Bellas", "Escamas Corazón", "Escamas Dragón", "Escamas Marinas", "Esmeraldas", "Esporas Musgosas", "Estatuas de Bellsprout", "Flautas Amarillas", "Flautas Azules", "Flautas Azur", "Flautas Blancas", "Flautas Negras", "Flautas Rojas", "Flechas Venenosas", "Franjas Recias", "Frutas Extrañas", "Gafas Elección", "Gafas Especiales", "Gafas Protectoras", "Gafas de Sol", "Galletas Lava", "Garras Afiladas", "Garras Garfio", "Garras Rápidas", "Gemas Acero", "Gemas Agua", "Gemas Bicho", "Gemas Dragón", "Gemas Eléctricas", "Gemas Fantasma", "Gemas Fuego", "Gemas Hada", "Gemas Hielo", "Gemas Lucha", "Gemas Normales", "Gemas Planta", "Gemas Psíquicas", "Gemas Roca", "Gemas Siniestras", "Gemas Tierra", "Gemas Veneno", "Gemas Voladoras", "Gloria Balls", "Griseosferas", "Hierbas Blancas", "Hierbas Mentales", "Hierbas Revivir", "Hierbas Únicas", "Hiperpociones", "Honor Balls", "Identificaciones Rocket", "Incubadoras", "Lentes Recias", "Limonadas", "Llamasferas", "Llaves Ascensor", "Llaves Magnéticas", "Llaves de la Central", "Llaves del Capitán", "Llaves del Dormitorio", "Lujo Balls", "Luna Balls", "Lupas", "Lustresferas", "Malla Balls", "Master Balls", "Maxipepitas", "Medallas de Dem", "Mejoras", "Minisetas", "Mochilas Propulsoras", "Monedas Amuleto", "Mudas Concha", "Máscaras de Gas", "Nerviosferas", "Nido Balls", "Nivel Balls", "Ocaso Balls", "Partes Amarillas", "Partes Azules", "Partes Rojas", "Partes Verdes", "Patas de Krabby", "Patas de Mankey", "Pepitas", "Perlas", "Perlas Grandes", "Pesas Recias", "Peso Balls", "Piedras Agua", "Piedras Alba", "Piedras Duras", "Piedras Día", "Piedras Espíritu", "Piedras Eternas", "Piedras Fuego", "Piedras Género", "Piedras Hielo", "Piedras Hoja", "Piedras Imán", "Piedras Lunares", "Piedras Niebla", "Piedras Noche", "Piedras Oval", "Piedras Pómez", "Piedras Solares", "Piedras Trueno", "Piezas Devon", "Piezas de Nave", "Pilas", "Pizzas", "Plumas Aguante", "Plumas Bonitas", "Plumas Genio", "Plumas Listeza", "Plumas Lunares", "Plumas Músculo", "Plumas Salud", "Plumas Ímpetu", "Pociones", "Pociones Máximas", "Pociones Secretas", "Poké Balls", "Poké Flautas", "Precisiones X", "Precisiones XX", "Precisiones XXX", "Precisiones XXXX", "Protecciones X", "Proteínas", "Puntas ADN", "Rapid Balls", "Raíces Energía", "Raíces Grandes", "Regaderas", "Rocas Calor", "Rocas Heladas", "Rocas Lluvia", "Rocas Suaves", "Rocas del Rey", "Safari Balls", "Sales Cardumen", "Sana Balls", "Sartas Perlas", "Semillas Bruma", "Semillas Electro", "Semillas Hierba", "Semillas Milagro", "Semillas Psique", "Setas Aroma", "Setas Grandes", "Setas Venenosas", "Super Balls", "Supercañas", "Superincubadoras", "Superpociones", "Tablas Acero", "Tablas Bicho", "Tablas Cielo", "Tablas Draco", "Tablas Duende", "Tablas Fuertes", "Tablas Heladas", "Tablas Linfa", "Tablas Llama", "Tablas Mentales", "Tablas Oscuras", "Tablas Pradal", "Tablas Pétreas", "Tablas Terrax", "Tablas Terror", "Tablas Trueno", "Tablas Tóxicas", "Tablas de Surf", "Tablillas Regi", "Tarjetas Rojas", "Telas Terribles", "Tijeras", "Toxiestrellas", "Toxisferas", "Turno Balls", "Ultra Balls", "Velocidades X", "Velocidades XX", "Velocidades XXX", "Velocidades XXXX", "Veloz Balls", "Vidasferas", "Wailmegaderas"].each { |name| SPANISH_ITEM_FORMS[name] = 3 }
["Agua Fresca", "Agua Mística", "Ánfora"].each { |name| SPANISH_ITEM_FORMS[name] = 5 }
["Ánforas"].each { |name| SPANISH_ITEM_FORMS[name] = 7 }

def pbResolveItemArticles(text, args)
  return text if !text.is_a?(String)
  return text if !text.include?("{art:")
  return text.gsub(/\{art:(\d+):(el|un|este|del|al|otro)\}/) do
    index, kind = $1.to_i, $2
    name = args[index].to_s
    form = SPANISH_ITEM_FORMS[name] || 0
    female = (form & 1) != 0
    plural = (form & 2) != 0
    stressed_a = (form & 4) != 0 && !plural
    definite = plural ? (female ? "las" : "los") : (female && !stressed_a ? "la" : "el")
    case kind
    when "el"   then definite
    when "un"   then plural ? (female ? "unas" : "unos") : (female && !stressed_a ? "una" : "un")
    when "este" then plural ? (female ? "estas" : "estos") : (female ? "esta" : "este")
    when "otro" then plural ? (female ? "otras" : "otros") : (female ? "otra" : "otro")
    when "del"  then definite == "el" ? "del" : "de " + definite
    when "al"   then definite == "el" ? "al" : "a " + definite
    end
  end
end
# END SPANISH ITEM CONCORDANCE

module MessageTypes
  # Value 0 is used for common event and map event text
  Species = 1
  Kinds = 2
  Entries = 3
  FormNames = 4
  Moves = 5
  MoveDescriptions = 6
  Items = 7
  ItemPlurals = 8
  ItemDescriptions = 9
  Abilities = 10
  AbilityDescs = 11
  Types = 12
  TrainerTypes = 13
  TrainerNames = 14
  BeginSpeech = 15
  EndSpeechWin = 16
  EndSpeechLose = 17
  RegionNames = 18
  PlaceNames = 19
  PlaceDescriptions = 20
  MapNames = 21
  PhoneMessages = 22
  TrainerLoseText = 23
  ScriptTexts = 24
  RibbonNames = 25
  RibbonDescriptions = 26
  TrainerInfoText = 27
  OutfitTexts = 28
  @@messages = Messages.new
  @@messagesFallback = Messages.new("Data/messages.dat", true)

  def self.stringToKey(str)
    return Messages.stringToKey(str)
  end

  def self.normalizeValue(value)
    return Messages.normalizeValue(value)
  end

  def self.denormalizeValue(value)
    Messages.denormalizeValue(value)
  end

  def self.writeObject(f, msgs, secname)
    Messages.denormalizeValue(str)
  end

  def self.extract(outfile)
    @@messages.extract(outfile)
  end

  def self.setMessages(type, array)
    @@messages.setMessages(type, array)
  end

  def self.addMessages(type, array)
    @@messages.addMessages(type, array)
  end

  def self.createHash(type, array)
    Messages.createHash(type, array)
  end

  def self.addMapMessagesAsHash(type, array)
    @@messages.addMapMessagesAsHash(type, array)
  end

  def self.setMapMessagesAsHash(type, array)
    @@messages.setMapMessagesAsHash(type, array)
  end

  def self.addMessagesAsHash(type, array)
    @@messages.addMessagesAsHash(type, array)
  end

  def self.setMessagesAsHash(type, array)
    @@messages.setMessagesAsHash(type, array)
  end

  def self.saveMessages(filename = nil)
    @@messages.saveMessages(filename)
  end

  def self.loadMessageFile(filename)
    @@messages.loadMessageFile(filename)
  end

  def self.get(type, id)
    ret = @@messages.get(type, id)
    if ret == ""
      ret = @@messagesFallback.get(type, id)
    end
    return pbResolveGenderMarkers(ret)
  end

  def self.getCount(type)
    c1 = @@messages.getCount(type)
    c2 = @@messagesFallback.getCount(type)
    return c1 > c2 ? c1 : c2
  end

  def self.getOriginal(type, id)
    return @@messagesFallback.get(type, id)
  end

  def self.getFromHash(type, key)
    pbResolveGenderMarkers(@@messages.getFromHash(type, key))
  end

  def self.getFromMapHash(type, key)
    pbResolveGenderMarkers(@@messages.getFromMapHash(type, key))
  end
end

def pbLoadMessages(file)
  return MessageTypes.loadMessageFile(file)
end

def pbGetMessageCount(type)
  return MessageTypes.getCount(type)
end

def pbGetMessage(type, id)
  return MessageTypes.get(type, id)
end

def pbGetMessageFromHash(type, id)
  return MessageTypes.getFromHash(type, id)
end

# Replaces first argument with a localized version and formats the other
# parameters by replacing {1}, {2}, etc. with those placeholders.
def _OUTFIT_INTL(str)
  return MessageTypes.getFromHash(MessageTypes::OutfitTexts, str)
end

# BEGIN SPANISH BATTLE REFERENCES
# Only generated battler/team references carry this type; nicknames stay untouched.
class SpanishBattleReference < String; end

def pbResolveBattleReferences(text, args)
  return text if !text.is_a?(String)
  for i in 1...args.length
    reference = args[i]
    next if !reference.is_a?(SpanishBattleReference) || reference !~ /\A(?:[Ee]l|[Tt]u) /
    lower = reference.sub(/\A./) { |char| char.downcase }
    # Spanish contractions belong to the sentence, never to the nickname.
    if lower.start_with?("el ")
      text.gsub!(/\b([Dd]e|[Aa])\s+\{#{i}\}/) do
        preposition = $1
        contraction = preposition.downcase == "de" ? "del " : "al "
        contraction = contraction.sub(/\A./) { |char| char.upcase } if preposition =~ /\A[A-Z]/
        contraction + lower.sub(/\Ael /, "")
      end
    end
    text.gsub!(/\{#{i}\}/) do
      prefix = $`.gsub(/<[^>]*>/, "").gsub(/\\[a-z]+\[[^\]]*\]/i, "")
      beginning = prefix =~ /\A\s*[¡¿]*\s*\z/ || prefix =~ /[.!?…]\s*[¡¿]*\s*\z/
      beginning ? lower.sub(/\A./) { |char| char.upcase } : lower
    end
  end
  return text
end
# END SPANISH BATTLE REFERENCES

def _INTL(*arg)
  begin
    string = MessageTypes.getFromHash(MessageTypes::ScriptTexts, arg[0])
  rescue
    string = arg[0]
  end
  string = pbResolveItemArticles(string.clone, arg)
  string = pbResolveBattleReferences(string, arg)
  for i in 1...arg.length
    string.gsub!(/\{#{i}\}/, "#{arg[i]}")
  end
  return string
end

# Replaces first argument with a localized version and formats the other
# parameters by replacing {1}, {2}, etc. with those placeholders.
# This version acts more like sprintf, supports e.g. {1:d} or {2:s}
def _ISPRINTF(*arg)
  begin
    string = MessageTypes.getFromHash(MessageTypes::ScriptTexts, arg[0])
  rescue
    string = arg[0]
  end
  string = string.clone
  for i in 1...arg.length
    string.gsub!(/\{#{i}\:([^\}]+?)\}/) { |m|
      next sprintf("%" + $1, arg[i])
    }
  end
  return string
end

def _I(str)
  return _MAPINTL($game_map.map_id, str)
end

def _MAPINTL(mapid, *arg)
  string = MessageTypes.getFromMapHash(mapid, arg[0])
  string = pbResolveItemArticles(string.clone, arg)
  string = pbResolveBattleReferences(string, arg)
  for i in 1...arg.length
    string.gsub!(/\{#{i}\}/, "#{arg[i]}")
  end
  return string
end

def _MAPISPRINTF(mapid, *arg)
  string = MessageTypes.getFromMapHash(mapid, arg[0])
  string = string.clone
  for i in 1...arg.length
    string.gsub!(/\{#{i}\:([^\}]+?)\}/) { |m|
      next sprintf("%" + $1, arg[i])
    }
  end
  return string
end
