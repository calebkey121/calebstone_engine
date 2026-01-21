from calebstone_engine.core.ally import Ally
from .cards import CARD_CATALOG
from enum import Enum

class DeckType(Enum):
    """Available deck archetypes"""
    STANDARD = "standard"
    TEST = "test"
    EARLY = 'early'
    LATE = 'late'

# Collection of all deck compositions
DECK_COMPOSITIONS = {
    DeckType.STANDARD: {
        "SIEGE_ENGINEER": 2,
        "ROYAL_FALCONER": 2,
        "WANDERING_MINSTREL": 2,
        "COURT_ALCHEMIST": 2,
        "MERCENARY_CAPTAIN": 2,
        "VILLAGE_BLACKSMITH": 3,
        "JOUSTING_CHAMPION": 3,
        "DIRE_WOLF": 3,
        "CASTLE_WARD": 3,
        "HIGHWAYMANS_AMBUSH": 3,
        "BANDIT_OUTLAW": 3,
        "UNDEAD_CREATURES": 3,
        "HIGHLAND_SCOUT": 3,
        "BOW_MARSHAL": 3,
        "FOREST_GUARDIAN": 3
    },

    DeckType.EARLY: {
        # Early game (5-20 cost)
        "SIEGE_ENGINEER": 4,      # 5 cost, utility
        "ROYAL_FALCONER": 4,      # 10 cost, aggro
        "WANDERING_MINSTREL": 4,  # 15 cost, sustain
        "COURT_ALCHEMIST": 4,     # 20 cost, control
        
        # Mid game (25-40 cost)
        "MERCENARY_CAPTAIN": 3,   # 25 cost, economy
        "VILLAGE_BLACKSMITH": 3,  # 30 cost, economy
        "JOUSTING_CHAMPION": 3,   # 35 cost, value
        "DIRE_WOLF": 3,          # 40 cost, threat
        
        # Late game (45-60 cost)
        "CASTLE_WARD": 2,         # 45 cost, tank
        "HIGHWAYMANS_AMBUSH": 2,  # 50 cost, control
        "BANDIT_OUTLAW": 2,       # 55 cost, value
        "UNDEAD_CREATURES": 2,    # 60 cost, finisher
        
        # Super late game (65-80 cost)
        "HIGHLAND_SCOUT": 1,      # 65 cost, draw
        "BOW_MARSHAL": 1,         # 70 cost, control
        "FOREST_GUARDIAN": 1,     # 75 cost, heal
        "TITAN_OVERLORD": 1       # 80 cost, finisher
    },

    DeckType.LATE: {
        # Early game (5-20 cost)
        "SIEGE_ENGINEER": 1,      # 5 cost, utility
        "ROYAL_FALCONER": 1,      # 10 cost, aggro
        "WANDERING_MINSTREL": 1,  # 15 cost, sustain
        "COURT_ALCHEMIST": 1,     # 20 cost, control
        
        # Mid game (25-40 cost)
        "MERCENARY_CAPTAIN": 2,   # 25 cost, economy
        "VILLAGE_BLACKSMITH": 2,  # 30 cost, economy
        "JOUSTING_CHAMPION": 2,   # 35 cost, value
        "DIRE_WOLF": 2,          # 40 cost, threat
        
        # Late game (45-60 cost)
        "CASTLE_WARD": 3,         # 45 cost, tank
        "HIGHWAYMANS_AMBUSH": 3,  # 50 cost, control
        "BANDIT_OUTLAW": 3,       # 55 cost, value
        "UNDEAD_CREATURES": 3,    # 60 cost, finisher
        
        # Super late game (65-80 cost)
        "HIGHLAND_SCOUT": 4,      # 65 cost, draw
        "BOW_MARSHAL": 4,         # 70 cost, control
        "FOREST_GUARDIAN": 4,     # 75 cost, heal
        "TITAN_OVERLORD": 4       # 80 cost, finisher
    },
}

def create_deck(deck_type = DeckType.STANDARD) -> list:
    """
    Creates a fresh deck from the specified deck composition.
    
    Args:
        deck_type: DeckType enum specifying which deck composition to use
        
    Returns:
        list: List of Ally objects representing the deck
    """
    #if deck_type not in DeckType:
    #    raise ValueError(f"Invalid deck type. Choose from: {[t.value for t in DeckType]}")
        
    deck_list = []
    if type(deck_type) == DeckType:
        composition = DECK_COMPOSITIONS[deck_type]
    elif type(deck_type) == str:
        composition = DECK_COMPOSITIONS[DeckType(deck_type)]
    elif type(deck_type) == dict:
        composition = deck_type
    else:
        raise RuntimeError("create_deck expects a DeckType or dict")
    
    for card_name, copies in composition.items():
        card = CARD_CATALOG[card_name]
        for _ in range(copies):
            deck_list.append(Ally(orig=card))
    
    return deck_list
