class Window_JukeboxLocalized < Window_CommandPokemon
  def drawItem(index, count, rect)
    return super unless getCurrentLanguage == :SPANISH
    saved_font = self.contents.font.clone
    begin
      rect = drawCursor(index, rect)
      text = @commands[index]
      pbFitCompleteText(self.contents, text, rect.width - 4)
      pbDrawShadowText(self.contents, rect.x, rect.y + (saved_font.size - self.contents.font.size) / 2,
                       rect.width, rect.height, text, self.baseColor, self.shadowColor)
    ensure
      self.contents.font = saved_font
    end
  end
end

#===============================================================================
#
#===============================================================================
class PokemonJukebox_Scene
  def pbUpdate
    pbUpdateSpriteHash(@sprites)
  end

  def pbStartScene(commands)
    @commands = commands
    @viewport = Viewport.new(0,0,Graphics.width,Graphics.height)
    @viewport.z = 99999
    @sprites = {}

    @sprites["background"] = IconSprite.new(0,0,@viewport)
    if isDarkMode
      @sprites["background"].setBitmap("Graphics/Pictures/Pokegear/bg_dark")
    else
      @sprites["background"].setBitmap("Graphics/Pictures/Pokegear/bg")
    end
    @sprites["ui"] = IconSprite.new(0,0,@viewport)
    @sprites["ui"].setBitmap("Graphics/Pictures/jukeboxbg")
    @sprites["header"] = Window_UnformattedTextPokemon.newWithSize(
       _INTL("Jukebox"),2,-18,128,64,@viewport)

    if isDarkMode
      @sprites["header"].baseColor   = pbColor(:LIGHT_TEXT_MAIN_COLOR)
      @sprites["header"].shadowColor = pbColor(:LIGHT_TEXT_SHADOW_COLOR)
    else
      @sprites["header"].baseColor   = pbColor(:DARK_TEXT_MAIN_COLOR)
      @sprites["header"].shadowColor = pbColor(:DARK_TEXT_SHADOW_COLOR)
    end

    @sprites["header"].windowskin  = nil
    @sprites["commands"] = Window_JukeboxLocalized.newWithSize(@commands,
       94,92,324,224,@viewport)
    @sprites["commands"].windowskin = nil

    @sprites["commands"].baseColor   = pbColor(:DARK_TEXT_MAIN_COLOR)
    @sprites["commands"].shadowColor = pbColor(:DARK_TEXT_SHADOW_COLOR)

    pbFadeInAndShow(@sprites) { pbUpdate }
  end

  def pbScene
    ret = -1
    loop do
      Graphics.update
      Input.update
      pbUpdate
      if Input.trigger?(Input::BACK)
        break
      elsif Input.trigger?(Input::USE)
        ret = @sprites["commands"].index
        break
      end
    end
    return ret
  end

  def pbSetCommands(newcommands,newindex)
    @sprites["commands"].commands = (!newcommands) ? @commands : newcommands
    @sprites["commands"].index    = newindex
  end

  def pbEndScene
    pbFadeOutAndHide(@sprites) { pbUpdate }
    pbDisposeSpriteHash(@sprites)
    @viewport.dispose
  end
end

#===============================================================================
#
#===============================================================================
class PokemonJukeboxScreen
  SPANISH_MUSIC_LABELS = {
    "Credits" => "Créditos",
    "Evolution" => "Evolución",
    "Evolution Start" => "Inicio de la evolución",
    "Evolution Success" => "Evolución completada",
    "art_gallery" => "Galería de arte",
    "battle_champion" => "Combate: Campeón",
    "battle_cynthia" => "Combate: Cintia",
    "battle_deoxys" => "Combate: Deoxys",
    "battle_elitefour" => "Combate: Alto Mando",
    "battle_frontierBrain" => "Combate: As del Frente",
    "battle_grunt" => "Combate: recluta",
    "battle_gymLeader" => "Combate: líder de Gimnasio",
    "battle_kanto_legend" => "Combate: legendarios de Kanto",
    "battle_magma_boss" => "Combate: líder del Equipo Magma",
    "battle_regi" => "Combate: Regis",
    "battle_rival" => "Combate: rival",
    "battle_spearpillar" => "Combate: Columna Lanza",
    "battle_trainer" => "Combate: entrenador",
    "battle_weatherTrio" => "Combate: trío del clima",
    "battle_wild" => "Combate: Pokémon salvaje",
    "bicycle" => "Bicicleta",
    "birch_lab" => "Laboratorio de Abedul",
    "boutique" => "Boutique",
    "cableCar" => "Teleférico",
    "chased_wild_pokemon" => "Persecución de Pokémon salvajes",
    "city_coumarine" => "Ciudad Témpera",
    "city_dewford" => "Pueblo Azuliza",
    "city_evergrande" => "Ciudad Colosalia",
    "city_fallarbor" => "Pueblo Pardal",
    "city_fortree" => "Ciudad Arborada",
    "city_lilycove" => "Ciudad Calagua",
    "city_littleroot" => "Villa Raíz",
    "city_oldale" => "Pueblo Escaso",
    "city_petalburg" => "Ciudad Petalia",
    "city_rustboro" => "Ciudad Férrica",
    "city_slateport" => "Ciudad Portual",
    "city_sootopolis" => "Ciudad Arrecípolis",
    "city_verdanturf" => "Pueblo Verdegal",
    "clefairy_drums" => "Tambores de Clefairy",
    "cutscene_awaken" => "El despertar",
    "cutscene_rayquaza" => "La aparición de Rayquaza",
    "dragalge_by_lozyeahh" => "Dragalge — Lozyeahh",
    "drought" => "Sequía",
    "dungeon_hideout" => "Guarida",
    "dungeon_mount_pyre" => "Monte Pírico",
    "dungeon_origin_cave" => "Cueva Ancestral",
    "dungeon_peak_mount_pyre" => "Cima del Monte Pírico",
    "dungeon_petalburg_woods" => "Bosque Petalia",
    "encounter_archie_maxie" => "Encuentro con Aquiles y Magno",
    "fusion" => "Fusión",
    "fusion_short" => "Fusión (versión breve)",
    "game_corner" => "Casino",
    "game_introduction" => "Presentación del juego",
    "gym" => "Gimnasio",
    "heavy_rain" => "Lluvia intensa",
    "intro_part1" => "Introducción: parte 1",
    "intro_part2" => "Introducción: parte 2",
    "intro_part3" => "Introducción: parte 3",
    "introduction" => "Introducción",
    "marine_museum" => "Museo Oceánico",
    "museum" => "Museo",
    "orre" => "Aura",
    "part1_end" => "Final de la primera parte",
    "pif_title" => "Tema de Infinite Fusion",
    "pokemart" => "Tienda Pokémon",
    "pokemart_trumpet" => "Tienda Pokémon (trompeta)",
    "pokemon_center" => "Centro Pokémon",
    "pokemon_go_map" => "Mapa de Pokémon GO",
    "rival_brendan" => "Encuentro con Bruno",
    "rival_may" => "Encuentro con Aura",
    "route_101" => "Ruta 101",
    "route_104" => "Ruta 104",
    "route_110" => "Ruta 110",
    "route_111" => "Ruta 111",
    "route_113" => "Ruta 113",
    "route_119" => "Ruta 119",
    "route_120" => "Ruta 120",
    "route_123" => "Ruta 123",
    "route_mtChimney" => "Monte Cenizo",
    "route_safari" => "Zona Safari",
    "route_sunkenShip" => "Nao Abandonada",
    "sharpedo" => "Sharpedo",
    "ship" => "Barco",
    "spotted_interviewer" => "Encuentro con entrevistadores",
    "spotted_team_aqua" => "Encuentro con el Equipo Aqua",
    "spotted_team_magma" => "Encuentro con el Equipo Magma",
    "surf" => "Surf",
    "title_screen" => "Pantalla de título",
    "trainer_school" => "Escuela de Entrenadores",
    "trick_house" => "Casa Treta",
    "trumpet_petalburg_woods" => "Bosque Petalia (trompeta)",
    "underwater" => "Bajo el agua",
    "zigzagoon" => "Zigzagoon",
  }

  def music_label(track)
    return track unless getCurrentLanguage == :SPANISH
    SPANISH_MUSIC_LABELS[track] || track
  end
  def initialize(scene)
    @scene = scene
  end

  def pbStartScreen
    commands = []
    cmdMarch   = -1
    cmdLullaby = -1
    cmdOak     = -1
    cmdCustom  = -1
    commands[cmdCustom = commands.length]  = _INTL("Play Music")
    commands[commands.length]              = _INTL("Exit")
    @scene.pbStartScene(commands)
    loop do
      cmd = @scene.pbScene
      if cmd<0
        pbPlayCloseMenuSE
        break
      elsif cmdCustom>=0 && cmd==cmdCustom
        pbPlayDecisionSE
        files = getMusicList
        @scene.pbSetCommands(files.map { |track| music_label(track) },0)
        loop do
          cmd2 = @scene.pbScene
          if cmd2<0
            pbPlayCancelSE
            break
          elsif cmd2==0
            pbPlayDecisionSE
            pbBGMPlay($game_map.bgm)
            $game_system.setDefaultBGM(nil)
            $PokemonMap.whiteFluteUsed = false if $PokemonMap
            $PokemonMap.blackFluteUsed = false if $PokemonMap
          else
            pbPlayDecisionSE
            $game_system.bgm_stop
            bgm_name = files[cmd2]
            pbBGMPlay(bgm_name)
            $game_system.setDefaultBGM(bgm_name)
            $PokemonMap.whiteFluteUsed = false if $PokemonMap
            $PokemonMap.blackFluteUsed = false if $PokemonMap
          end
        end
        @scene.pbSetCommands(nil,cmdCustom)
      else   # Exit
        pbPlayCloseMenuSE
        break
      end
    end
    @scene.pbEndScene
  end




  def getFolderMusic
    files = []
    Dir.chdir("Audio/BGM/") {
      Dir.glob("*.mp3") { |f| files.push(File.basename(f, ".*")) }
      Dir.glob("*.MP3") { |f| files.push(File.basename(f, ".*")) }
      Dir.glob("*.ogg") { |f| files.push(File.basename(f, ".*")) }
      Dir.glob("*.OGG") { |f| files.push(File.basename(f, ".*")) }
      Dir.glob("*.wav") { |f| files.push(File.basename(f, ".*")) }
      Dir.glob("*.WAV") { |f| files.push(File.basename(f, ".*")) }
      Dir.glob("*.mid") { |f| files.push(File.basename(f, ".*")) }
      Dir.glob("*.MID") { |f| files.push(File.basename(f, ".*")) }
      Dir.glob("*.midi") { |f| files.push(File.basename(f, ".*")) }
      Dir.glob("*.MIDI") { |f| files.push(File.basename(f, ".*")) }
    }
    return files
  end
  def getMusicList
    folder_music = getFolderMusic
    encountered_music_list = $PokemonSystem.encountered_music
    available_music =  [_INTL("(Default)")]
    encountered_music_list.each do |track|
      available_music << track if folder_music.include?(track)
    end
    return available_music
  end
end
