from dataclasses import dataclass, field
from typing import Dict

DEFAULT_DECK = {
    "SIEGE_ENGINEER": 3,
    "ROYAL_FALCONER": 3,
    "WANDERING_MINSTREL": 3,
    "COURT_ALCHEMIST": 3,
    "MERCENARY_CAPTAIN": 3,
    "VILLAGE_BLACKSMITH": 3,
    "JOUSTING_CHAMPION": 3,
    "DIRE_WOLF": 3,
    "CASTLE_WARD": 3,
    "HIGHWAYMANS_AMBUSH": 3,
    "BANDIT_OUTLAW": 3,
    "UNDEAD_CREATURES": 3,
    "HIGHLAND_SCOUT": 3,
    "BOW_MARSHAL": 3,
    "FOREST_GUARDIAN": 3,
}

@dataclass(frozen=True)
class PlayerConfig:
    player_id: str = "p1"
    controller: str = "random"
    hero: str = "Caleb"
    deck: Dict[str, int] = field(default_factory=lambda: DEFAULT_DECK.copy())
