from .card import Card
from .character import Character

class Ally(Card):
    def __init__(self, orig=None, cost=None, name=None, attack_value=None, health=None, effect=None, id=None, text=None):
        if orig:
            super().__init__(orig.id, cost=orig.cost, name=orig.name, effect=orig.effect, text=orig.text)
            self._character = Character(
                name=orig.name,
                attack_value=orig.attack_value,
                health=orig.health,
                max_health=orig.max_health
            )
        else:
            super().__init__(id, cost, name, effect, text)
            self._character = Character(name, attack_value, health)
        
        # For convenience, expose character's signals directly
        self.signals = self._character.signals
    
    def __repr__(self):
        return f"({self.cost}) {self.name} | {self.attack_value}/{self.health}"
    
    # Delegate all character properties/methods | Needed because its also a Card, not just character
    @property
    def health(self):
        return self._character.health
    
    @health.setter
    def health(self, value):
        self._character.health = value
    
    @property
    def attack_value(self):
        return self._character._attack_value
        
    @attack_value.setter
    def attack_value(self, value):
        self._character._attack_value = value
    
    @property
    def max_health(self):
        return self._character._max_health
        
    @property
    def ready(self):
        return self._character._ready

    def ready_up(self):
        self._character.ready_up()
    
    def ready_down(self):
        self._character.ready_down()
    
    def can_attack(self):
        return self._character.can_attack()
    
    def attack(self, target):
        self._character.attack(target)
    
    def die(self):
        self._character.die()
    
    def damage(self, source, amount):
        self._character.damage(source, amount)
    
    def heal(self, source, amount):
        self._character.heal(source, amount)
