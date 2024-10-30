from game_engine.config import HERO_STARTING_HEALTH, HERO_MAX_HEALTH
from .character import Character

class Hero:
    def __init__(self, hero_name):
        self._name = hero_name
        self._character = Character(
            name=hero_name,
            attack_value=0,
            health=HERO_STARTING_HEALTH,
            max_health=HERO_MAX_HEALTH
        )
        self.signals = self._character.signals
    
    def __repr__(self):
        return f"{self.name} | {self.attack_value}/{self.health}"
    
    # Delegate all character properties/methods
    @property
    def name(self):
        return self._character._name
    
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
