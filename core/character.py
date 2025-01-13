from dataclasses import dataclass, field
from .signal import *

@dataclass
class CharacterSignals:
    """Signals shared by all characters"""
    on_death: Signal = field(default_factory=Signal)
    on_heal_received: Signal = field(default_factory=Signal)
    on_attack: Signal = field(default_factory=Signal)
    on_attacked: Signal = field(default_factory=Signal)
    on_damage_dealt: Signal = field(default_factory=Signal)
    on_damage_taken: Signal = field(default_factory=Signal)

class Character:
    def __init__(self, name, attack_value, health, max_health=None):
        self._name = name
        self._attack_value = attack_value
        self._health = health
        self._max_health = max_health or health
        self._ready = False
        self.signals = CharacterSignals()
    
    def __repr__(self):
        return self._name
    
    @property
    def attack_value(self):
        return self._attack_value

    @property
    def health(self):
        return self._health
        
    @health.setter
    def health(self, new_amount):
        if new_amount <= 0:
            if self._health > 0:  # Only die once
                self.die()
        new_amount = min(new_amount, self._max_health)
        self._health = new_amount
    
    def ready_up(self):
        if self._attack_value > 0:
            self._ready = True
            
    def ready_down(self):
        self._ready = False
        
    def can_attack(self):
        return self._ready and self._attack_value > 0
    
    def heal(self, source, amount):
        raw_heal = amount  # may buff in the future
        missing_health = self._max_health - self.health
        effective_heal = min(raw_heal, missing_health)
        extra_heal = max(0, raw_heal - missing_health)
        
        if self._health <= 0:  # Can't heal dead characters
            return None
        self.health += raw_heal
        
        # Emit Triggers
        on_heal_received_data = HealEventData(
            source=source,
            target=self,
            effective_heal=effective_heal,
            extra_heal=extra_heal
        )
        self.signals.on_heal_received.emit(on_heal_received_data)
        
        return raw_heal, effective_heal, extra_heal
    
    def damage(self, source, amount):
        raw_damage = amount # may mitigate in the future
        effective_damage = min(raw_damage, self.health)
        extra_amount = max(0, raw_damage - self.health)
        self.health -= raw_damage

        # Emit Triggers
        on_damage_dealt_data = DamageEventData(source=source, target=self, effective_damage=effective_damage, extra_damage=extra_amount)
        source.signals.on_damage_dealt.emit(on_damage_dealt_data)
        on_damage_taken_data = DamageEventData(source=source, target=self, effective_damage=effective_damage, extra_damage=extra_amount)
        self.signals.on_damage_taken.emit(on_damage_taken_data)
        return raw_damage, effective_damage, extra_amount

        
    def attack(self, target):
        if not self.can_attack():
            raise ValueError(f"{self._name} cannot attack right now")
        
        # Before attack starts, emit on attack
        self.signals.on_attack.emit(GameEventData(self)) # do we care abt target?
        
        # Damage Target
        target.damage(source=self, amount=self.attack_value)
        
        # Damage Attacker
        self.damage(source=target, amount=target.attack_value)

        target.signals.on_attacked.emit(GameEventData(self))
        
        self.ready_down()
    
    def die(self):
        self.signals.on_death.emit(GameEventData(self))
    
    @staticmethod
    def is_character(obj):
        # needed because allies/heros aren't direct subclasses of char, they have a .character attr
        return isinstance(obj._character, Character)
