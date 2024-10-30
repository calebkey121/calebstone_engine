from .character import Character  # Base class for Hero/Ally
from game_engine.config import ARMY_MAX_SIZE

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
    
    def available_attackers(self):
        """Returns indices of characters that can attack"""
        return [i for i, char in enumerate(self._army) 
               if char.can_attack()]
    
    def available_targets(self):
        """Returns indices of all characters"""
        return list(range(len(self._army)))

    def contains(self, character):
        return character in self._army

# reworking army to include all characters, remove below once satisfied with above
# from game_engine.Ally import Ally
# from config.GameSettings import ARMY_MAX_SIZE

# # The main way to organize allies in the game army
# # assumes only one type of ally
# class Army:
#     def __init__(self):
#         self._maxSize = ARMY_MAX_SIZE
#         self._armySize = 0
#         self._army = []

#     def __repr__(self):
#         return repr([a._name for a in self._army])

#     # more for testing
#     # def __eq__(self, other: 'Army') -> bool:
#     #     if not isinstance(other, Army):
#     #         return NotImplemented
#     #     return (
#     #         all(a1 == a2 for a1, a2 in zip(self._army, other._army))
#     #     )

#     # getter/setters
#     def max_size(self, maxSize=None):
#         if maxSize:
#             self._maxSize = maxSize
#         return self._maxSize
    
#     def army_size(self, armySize=None):
#         if armySize:
#             self._armySize = armySize
#         return self._armySize
    
#     def get_army(self):
#         return self._army

#     def set_army_size(self):
#         self._armySize = len(self._army)

#     # can any allies attack?
#     def available_attackers(self):
#         for ally in self._army:
#             if ally.is_ready():
#                 return True
#         return False
    
#     # Returns true if the army is full
#     def is_full(self):
#         return self.army_size() == self.max_size()

#     def ready_up(self):
#         for ally in self._army:
#             ally.ready_up()

#     def add_ally(self, ally):
#         if not isinstance(ally, Ally) or self.is_full():
#             raise ValueError("Must be adding an ally to a non full army")
#         self._army.append(ally)
#         self.set_army_size()

#     #This clears your Army of dead Allies
#     def remove_dead_allies(self, ally=None):
#         if not ally: # clear all 
#             for i in self._army:
#                 if i._health <= 0:
#                     self._army.remove(i)
#             self.set_army_size()
#         else: # clear specific Ally
#             self._army.remove(ally)
        

#     # find the index of a specific ally on the army
#     def find_ally(self, ally):
#         if not isinstance(ally, Ally):
#             raise ValueError(f"Checking non Ally type. Got: {ally}")
#         for i in self._army:
#             if i == ally:
#                 return i
#         raise ValueError("Checking Ally thats not in the army") # do we really wanna be this strict?

#     def get_ally_at(self, index):
#         return self._army[index] # errors on out of index, fine

#     def in_army(self, ally):
#         if not isinstance(ally, Ally):
#             raise ValueError(f"Checking non Ally type. Got: {ally}")
#         return ally in self._army
