# Personal translation ident, before the original opening cinematic.
# Reuses the supplied high-resolution artwork without altering it.
class SpanishCreditsIntro
  ART = "Graphics/Titles/SeCaVa/logo.png"
  JINGLE = "SeCaVa_intro"
  DURATION = 10.850645833333333
  END_TIME = DURATION + 0.25

  def self.play
    return if !File.file?(ART) || !File.file?("Audio/ME/#{JINGLE}.wav")
    new.play
  end

  def opacity_at(time, start_time, end_time, fade_in, fade_out)
    return 0 if time < start_time || time >= end_time
    value = [(time - start_time) / fade_in, (end_time - time) / fade_out, 1.0].min
    return (255 * [value, 0.0].max).round
  end

  def text_sprite
    sprite = Sprite.new(@viewport)
    sprite.bitmap = Bitmap.new(512, 384)
    sprite.bitmap.font.name = ["Arial", "Liberation Sans", "DejaVu Sans"]
    sprite.bitmap.font.bold = false
    sprite.bitmap.font.italic = false
    sprite.bitmap.font.color = Color.new(247, 243, 227)
    sprite.zoom_x = sprite.zoom_y = @scale
    sprite.x = @offset_x
    sprite.y = @offset_y
    @owned_bitmaps << sprite.bitmap
    @sprites << sprite
    return sprite
  end

  def prepare
    @viewport = Viewport.new(0, 0, Graphics.width, Graphics.height)
    @viewport.z = 100000
    @owned_bitmaps = []
    @sprites = []
    @scale = [Graphics.width / 512.0, Graphics.height / 384.0].min
    @offset_x = (Graphics.width - 512 * @scale) / 2.0
    @offset_y = (Graphics.height - 384 * @scale) / 2.0

    background = Sprite.new(@viewport)
    background.bitmap = Bitmap.new(Graphics.width, Graphics.height)
    background.bitmap.fill_rect(0, 0, Graphics.width, Graphics.height, Color.new(0, 0, 0))
    @owned_bitmaps << background.bitmap
    @sprites << background

    @artwork = Bitmap.new(ART)
    @owned_bitmaps << @artwork
    @logo = Sprite.new(@viewport)
    @logo.bitmap = @artwork
    @logo.zoom_x = @logo.zoom_y = 384.0 / @artwork.height * @scale
    @logo.x = (Graphics.width - @artwork.width * @logo.zoom_x) / 2.0
    @logo.y = @offset_y
    @logo.opacity = 0
    @sprites << @logo

    @credit = text_sprite
    bitmap = @credit.bitmap
    bitmap.font.size = 19
    bitmap.font.color = Color.new(202, 179, 118)
    heading = "TRADUCIDO POR"
    spacing = 3
    widths = heading.each_char.map { |char| bitmap.text_size(char).width }
    x = (512 - widths.inject(0, :+) - spacing * (widths.length - 1)) / 2.0
    heading.each_char.with_index do |char, index|
      bitmap.draw_text(x.round, 118, widths[index] + 2, 32, char)
      x += widths[index] + spacing
    end
    bitmap.font.size = 52
    bitmap.font.color = Color.new(247, 243, 227)
    left = bitmap.text_size("Se").width
    right = bitmap.text_size("aVa").width
    gap = 46
    x = (512 - left - gap - right) / 2.0
    bitmap.draw_text(x.round, 172, left + 3, 72, "Se")
    bitmap.draw_text((x + left + gap).round, 172, right + 3, 72, "aVa")
    @credit.opacity = 0

    # The luminous C is the original mark, not a replacement font glyph.
    @letter_c = Sprite.new(@viewport)
    @letter_c.bitmap = @artwork
    # Additive blending makes the texture's black margin transparent, allowing
    # natural letter spacing without covering the adjacent e or a.
    @letter_c.blend_type = 1
    @letter_c.src_rect.set(330, 390, 152, 207)
    @letter_c.zoom_x = @letter_c.zoom_y = 0.34 * @scale
    @letter_c.x = @offset_x + (x + left - 4) * @scale
    @letter_c.y = @offset_y + 154 * @scale
    @letter_c.opacity = 0
    @sprites << @letter_c
  end

  def play
    prepare
    # Remove the frozen loading picture before drawing the ident.
    Graphics.transition(0)
    pbBGMStop
    Input.update
    pbMEPlay(JINGLE)
    elapsed = 0.0
    loop do
      @logo.opacity = opacity_at(elapsed, 0.0, 6.0, 0.65, 0.45)
      alpha = opacity_at(elapsed, 6.25, DURATION, 0.45, 0.55)
      @credit.opacity = @letter_c.opacity = alpha
      Graphics.update
      Input.update
      # Consume the skipping key here so it cannot also skip the original movie.
      if elapsed >= 0.75 && continueKeyPressed?
        pbMEStop(0.2)
        initial = [@logo.opacity, @credit.opacity]
        fade = 0.0
        while fade < 0.2
          factor = [1.0 - fade / 0.2, 0.0].max
          @logo.opacity = (initial[0] * factor).round
          @credit.opacity = @letter_c.opacity = (initial[1] * factor).round
          Graphics.update
          Input.update
          fade += Graphics.delta_s
        end
        break
      end
      elapsed += Graphics.delta_s
      break if elapsed >= END_TIME
    end
    @logo.opacity = @credit.opacity = @letter_c.opacity = 0
    Graphics.update
    Input.update
    Graphics.freeze
  ensure
    pbMEStop
    if @sprites
      @sprites.reverse_each { |sprite| sprite.dispose unless sprite.disposed? }
    end
    if @owned_bitmaps
      @owned_bitmaps.reverse_each { |bitmap| bitmap.dispose unless bitmap.disposed? }
    end
    @viewport.dispose if @viewport && !@viewport.disposed?
  end
end
