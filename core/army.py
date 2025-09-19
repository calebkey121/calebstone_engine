from .character import Character  # Base class for Hero/Ally
from calebstone_engine.config import ARMY_MAX_SIZE

class Army:
    def __init__(self, hero):
        self._max_size = ARMY_MAX_SIZE
        self._army = [hero]  # Hero is always first position
    
    def __repr__(self):
        return repr([c for c in self._army])

    @property
    def size(self):
        # Don't count hero in size limit
        return len(self._army) - 1
    
    @property
    def hero(self):
        return self._army[0]
    
    @property
    def allies(self):
        # Everything but hero
        return self._army[1:]
    
    def get_all(self):
        return self._army
    
    def is_full(self):
        # Don't count hero in size limit
        return self.size >= self._max_size
    
    def ready_up(self):
        for character in self._army:
            character.ready_up()
    
    def add_ally(self, ally):
        if not Character.is_character(ally):
            raise ValueError(f"Must be adding a character. Got: {ally}")
        if self.is_full():
            raise ValueError("Army is full")
        self._army.append(ally)
    
    def add_allies(self, allies):
        for ally in allies:
            self.add_ally(ally)
    
    def remove_dead_allies(self):
        """Remove all dead allies from army"""
        self._army = [self.hero] + [
            ally for ally in self.allies 
            if ally.health > 0
        ]
    
    def get_character(self, index):
        return self._army[index]
    
    def get_ally(self, index): # meh
        return self._army[index + 1]
    
    def available_attackers(self):
        """Returns indices of characters that can attack"""
        return [i for i, char in enumerate(self._army) 
               if char.can_attack()]
    
    def available_targets(self):
        """Returns indices of all characters"""
        return list(range(len(self._army)))

    def contains(self, character):
        return character in self._army
