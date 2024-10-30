class Card:
    def __init__(self, cost=-1, name=None, effect=None, text=None):
        self._cost = cost
        self._name = name
        self._effect = effect
        self._text = text or (effect.text if effect else "")
    
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
