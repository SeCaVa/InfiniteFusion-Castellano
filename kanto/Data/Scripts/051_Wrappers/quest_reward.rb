class QuestReward
  attr_accessor :item
  attr_accessor :quantity
  attr_accessor :nb_quests
  attr_accessor :description
  attr_accessor :can_have_multiple

  # Translate on access: these objects may be built before selecting a language.
  def description
    return @description unless getCurrentLanguage == :SPANISH && @description.is_a?(String)
    return _INTL(@description)
  end

  def initialize(nb_quests,item,quantity,description,can_have_multiple=false)
    @nb_quests =nb_quests
    @item =item
    @quantity =quantity
    @description =description
    @can_have_multiple = can_have_multiple
  end
end