# BEGIN CLOTHES DESCRIPTION SCROLL
class ClothesDescriptionSprite < SpriteWrapper
  include AutomaticDescriptionScroll
  attr_reader :text

  def self.newWithSize(text, x, y, width, height, viewport = nil)
    sprite = self.new(width, height, viewport)
    sprite.x, sprite.y = x, y
    sprite.text = text
    return sprite
  end

  def initialize(width, height, viewport = nil)
    super(viewport)
    @panel_width, @panel_height = width, height
    @text = nil
    pbResetDescriptionScroll(0)
  end

  def baseColor=(color); @baseColor = color; refresh; end
  def shadowColor=(color); @shadowColor = color; refresh; end
  def windowskin=(skin); end

  def text=(value)
    value = value.to_s
    return if @text == value
    @text = value
    refresh
  end

  def refresh
    return if @text.nil? || !@baseColor || !@shadowColor || self.disposed?
    measure = Bitmap.new(1, 1)
    begin
      pbSetSystemFont(measure)
      dimensions = [0, 0]
      chunks = getLineBrokenChunks(measure, @text, @panel_width - 4, dimensions, true)
      content_height = dimensions[1] + 6  # Original four-pixel offset and shadow.
      content = Bitmap.new(@panel_width, [content_height, @panel_height].max)
      content.font = measure.font.clone
      chunks.each do |chunk|
        pbDrawShadowText(content, chunk[1], chunk[2], chunk[3] + 4, 32,
                         chunk[0], @baseColor, @shadowColor)
      end
      previous = self.bitmap
      self.bitmap = content
      previous.dispose if previous && !previous.disposed?
      self.src_rect.set(0, 0, @panel_width, @panel_height)
      pbResetDescriptionScroll(content_height - @panel_height)
    ensure
      measure.dispose
    end
  end

  def update
    return if self.disposed?
    super
    position = pbNextDescriptionScrollPosition
    self.src_rect.y = position if position
  end

  def dispose
    return if self.disposed?
    self.bitmap.dispose if self.bitmap && !self.bitmap.disposed?
    super
  end
end
# END CLOTHES DESCRIPTION SCROLL

class ClothesShopView < PokemonMart_Scene

  def initialize(currency_name = _INTL("Money"))
    @currency_name = currency_name
    @currency_name = get_cosmetic_currency_name if Settings::HOENN
  end

  def pbStartBuyOrSellScene(buying, stock, adapter)
    super(buying, stock, adapter)
    previous_description = @sprites["itemtextwindow"]
    description = ClothesDescriptionSprite.newWithSize(previous_description.text,
      previous_description.x, previous_description.y,
      previous_description.bitmap.width, previous_description.bitmap.height, @viewport)
    description.baseColor = Color.new(248, 248, 248)
    description.shadowColor = Color.new(0, 0, 0)
    description.z = previous_description.z
    description.opacity = previous_description.opacity
    description.visible = previous_description.visible
    @sprites["itemtextwindow"] = description
    previous_description.dispose
    @sprites["icon"].visible = false
    if @adapter.isShop?
      @sprites["background"].setBitmap("Graphics/Pictures/Outfits/martScreenOutfit")
    else
      @sprites["background"].setBitmap("Graphics/Pictures/Outfits/changeOutfitScreen")
    end

    preview_y = @adapter.isShop? ? 80 : 0
    @sprites["trainerPreview"] = TrainerClothesPreview.new(0, preview_y, true, "WALLET")

    @sprites["trainerPreview"].show()
    @sprites["moneywindow"].visible = false if !@adapter.isShop?
    @sprites["itemwindow"].setAllowPageJump(false)

    Kernel.pbDisplayText(@adapter.toggleText, 100, 240, 99999) if @adapter.toggleText

  end

  def select_specific_item(scroll_to_item_id,go_to_end_of_list_if_nil=false)
    itemwindow = @sprites["itemwindow"]
    if !scroll_to_item_id && go_to_end_of_list_if_nil
      itemwindow.index=@adapter.items.length-1
      itemwindow.refresh
    end
    i=0
    for item in @adapter.items
      next if !item.is_a?(Outfit)
      if item.id == scroll_to_item_id
        itemwindow.index=i
        itemwindow.refresh
      end
      i+=1
    end
  end

  def scroll_map
    pbScrollMap(DIRECTION_UP, 5, 6)
    pbScrollMap(DIRECTION_RIGHT, 7, 6)
    @initial_direction = $game_player.direction
    $game_player.turn_down
    pbRefreshSceneMap

      # pbSEPlay("GUI menu open")
      # $game_player.center($game_player.x+7, $game_player.y-5)
      # @initial_direction = $game_player.direction
      # $game_player.turn_down
      # Graphics.update
      # Input.update
      # pbRefreshSceneMap
  end

  def scroll_back_map

    @adapter.reset_player_clothes()
    pbScrollMap(DIRECTION_LEFT, 7, 6)
    pbScrollMap(DIRECTION_DOWN, 5, 6)
    $game_player.turn_generic(@initial_direction)

    # $game_player.center($game_player.x, $game_player.y)
    # Graphics.update
    # Input.update
    # pbRefreshSceneMap
  end

  def refreshStock(adapter)
    @adapter = adapter
    @sprites["itemwindow"].dispose if !@sprites
    @sprites["itemwindow"] = Window_PokemonMart.new(@stock, BuyAdapter.new(adapter),
                                                    Graphics.width - 316 - 16, 12, 330 + 16, Graphics.height - 126)
  end

  def pbRefresh
    if @subscene
      @subscene.pbRefresh
    else
      itemwindow = @sprites["itemwindow"]
      item = itemwindow.item
      if itemwindow.item
        if itemwindow.item.is_a?(Symbol)
          text = @adapter.getSpecialItemCaption(item)
        else
          text = @adapter.getDescription(item)
        end
      else
        text = getQuitDescription
      end
      @sprites["itemtextwindow"].text = text
      itemwindow.refresh
    end
    @sprites["moneywindow"].text = _INTL("{2}:\r\n<r>{1}", @adapter.getMoneyString, @currency_name)
  end

  def updateTrainerPreview()
    displayNewItem(@sprites["itemwindow"])
  end

  def displayNewItem(itemwindow)
    item = itemwindow.item
    if item
      if item.is_a?(Symbol)
        description = @adapter.getSpecialItemDescription(itemwindow.item)
      else
        description = @adapter.getDescription(itemwindow.item)
        @adapter.updateVersion(itemwindow.item)
      end
      @adapter.updateTrainerPreview(itemwindow.item, @sprites["trainerPreview"])
    else
      description = getQuitDescription
    end
    @sprites["itemtextwindow"].text = description
  end

  def getQuitDescription
    return _INTL("Outfits are submitted by the community. More will be added with future updates.")
  end
  def updatePreviewWindow
    itemwindow= @sprites["itemwindow"]
    @adapter.updateTrainerPreview(itemwindow.item, @sprites["trainerPreview"])
  end

  def pbChooseBuyItem
    itemwindow = @sprites["itemwindow"]
    refreshStock(@adapter) if !itemwindow
    displayNewItem(itemwindow)
    @sprites["helpwindow"].visible = false
    pbActivateWindow(@sprites, "itemwindow") {
      pbRefresh
      loop do
        Graphics.update
        Input.update
        olditem = itemwindow.item
        self.update
        if itemwindow.item != olditem
          displayNewItem(itemwindow)
        end
        if Input.trigger?(Input::L) #X button
          @adapter.switchVersion(itemwindow.item, -1)
          updateTrainerPreview()
        end

        if Input.trigger?(Input::R)  #Y button
          switchItemVersion(itemwindow)
        end
        if Input.trigger?(Input::SPECIAL) #Z button
          @adapter.toggleEvent(itemwindow.item)
          updateTrainerPreview()
        end

        if Input.trigger?(Input::BACK)
          pbPlayCloseMenuSE
          return nil
        elsif Input.trigger?(Input::USE)
          if itemwindow.item.is_a?(Symbol)
            ret = onSpecialActionTrigger(itemwindow)
            return ret if ret
          elsif itemwindow.index < @stock.length
            pbRefresh
            return @stock[itemwindow.index]
          else
            return nil
          end
        end
      end
    }
  end

  def onSpecialActionTrigger(itemwindow)
    @adapter.doSpecialItemAction(itemwindow.item)
    updateTrainerPreview()
    return nil
  end
  def onItemClick(itemwindow)
    if itemwindow.item.is_a?(Symbol)
      @adapter.doSpecialItemAction(itemwindow.item)
      updateTrainerPreview()
    elsif itemwindow.index < @stock.length
      pbRefresh
      return @stock[itemwindow.index]
    else
      return nil
    end
  end

  def switchItemVersion(itemwindow)
    @adapter.switchVersion(itemwindow.item, 1)
    updateTrainerPreview()
  end

  def update
    if Input.trigger?(Input::LEFT)
      pbSEPlay("GUI party switch", 80, 100)
      $game_player.turn_right_90
      pbRefreshSceneMap
    end
    if Input.trigger?(Input::RIGHT)
      pbSEPlay("GUI party switch", 80, 100)
      $game_player.turn_left_90
      pbRefreshSceneMap
    end
    super
  end

  def pbEndBuyScene
    if !@sprites.empty?
      @sprites["trainerPreview"].erase()
      @sprites["trainerPreview"] = nil
    end
    pbDisposeSpriteHash(@sprites)
    @viewport.dispose
    Kernel.pbClearText()
    # Scroll left after showing screen
    scroll_back_map()
  end

end
