from .card import Card

class Building(Card):
    def __init__(self, orig=None, cost=-1, name=None, health=-1, text=None, showText=False, selected=False, play_effect=None, amount=None):
        if orig:
            super().__init__(orig._cost, orig._name, orig._text, orig._showText, orig._selected, orig._playEffect, orig._amount)
            self._maxHealth = orig._maxHealth
            self._health = orig._health
            self._targeted = False
        else:
            super().__init__(cost, name, text, showText, selected, play_effect, amount)
            self._maxHealth = health
            self._health = health
            self._targeted = False
        
# GETTERS/SETTERS ********************************************************************************************
    def health(self, h=None):
        if isinstance(h, int):
            self._health = h
        return self._health
# ************************************************************************************************************
# Select *****************************************************************************************************
    def select(self):
        self._selected = True
    def unselect(self):
        self._selected = False
    def is_selected(self):
        return self._selected
# ************************************************************************************************************
# BATTLE *****************************************************************************************************
    # Lower your own health by damage amount 
    def lower_health(self, damage):
        self._health -= damage

    def heal(self, healAmount):
        self._health += healAmount
        if self._health  > self._maxHealth:
            self._health = self._maxHealth
