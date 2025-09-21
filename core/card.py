class Card:
    # --- Stable card ID registry (name -> int), append-only ---
    _CARD_IDS = {}

    def _assign_id(name: str | None) -> int | None:
        if name is None:
            return None
        if name in Card._CARD_IDS:
            return Card._CARD_IDS[name]
        new_id = len(Card._CARD_IDS)
        Card._CARD_IDS[name] = new_id
        return new_id

    def __init__(self, cost=-1, name=None, effect=None, text=None, card_type_id=None):
        self._cost = cost
        self._name = name
        self._effect = effect
        self._text = text or (effect.text if effect else "")
        # Stable categorical ID; if not provided, assign from name
        if card_type_id is not None:
            self._id = card_type_id
        else:
            self._id = Card._assign_id(self._name)
    
    def __repr__(self):
        return self.name or "Unnamed Card"

    # Property for cost
    @property
    def cost(self):
        return self._cost

    @cost.setter
    def cost(self, value):
        if isinstance(value, int) and value >= 0:
            self._cost = value
        else:
            raise ValueError("Cost must be a non-negative integer.")

    # Property for name
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if isinstance(value, str):
            self._name = value
        else:
            raise ValueError("Name must be a string.")

    # Property for effect
    @property
    def effect(self):
        return self._effect

    @effect.setter
    def effect(self, value):
        self._effect = value
        # Update text with the effect's text if text is not provided
        if self._text is None or self._text == "":
            self._text = value.text if value else ""

    # Property for text
    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        if isinstance(value, str):
            self._text = value
        else:
            raise ValueError("Text must be a string.")

    # Property for stable card ID (categorical, non-negative int or None)
    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if value is None:
            self._id = None
        elif isinstance(value, int) and value >= 0:
            self._id = value
        else:
            raise ValueError("id must be a non-negative integer or None.")
