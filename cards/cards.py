from calebstone_engine.core.ally import Ally
from calebstone_engine.effects import *
from enum import IntEnum

class CardId(IntEnum):
    SIEGE_ENGINEER = 0
    ROYAL_FALCONER = 1
    WANDERING_MINSTREL = 2
    COURT_ALCHEMIST = 3
    MERCENARY_CAPTAIN = 4
    VILLAGE_BLACKSMITH = 5
    JOUSTING_CHAMPION = 6
    DIRE_WOLF = 7
    CASTLE_WARD = 8
    HIGHWAYMANS_AMBUSH = 9
    BANDIT_OUTLAW = 10
    UNDEAD_CREATURES = 11
    HIGHLAND_SCOUT = 12
    BOW_MARSHAL = 13
    FOREST_GUARDIAN = 14
    TITAN_OVERLORD = 15
    # append new ones at the end

# Modified existing cards with scaled up values
SIEGE_ENGINEER = Ally(
    id=CardId.SIEGE_ENGINEER,
    name="Siege Engineer",
    cost=5,
    attack_value=0,
    health=35,
    effect=HealAllAlliesEffect(
        amount=[50],
        timing=TimingWindow.ON_PLAY,
    )
)

ROYAL_FALCONER = Ally(
    id=CardId.ROYAL_FALCONER,
    name="Royal Falconer",
    cost=10,
    attack_value=30,
    health=20,
    effect=DamageEnemyHeroEffect(
        amount=[35],
        timing=TimingWindow.ON_DEATH,
    )
)

WANDERING_MINSTREL = Ally(
    id=CardId.WANDERING_MINSTREL,
    name="Wandering Minstrel",
    cost=15,
    attack_value=25,
    health=50,
    effect=HealAllAlliesEffect(
        amount=[75],
        timing=TimingWindow.END_OF_TURN,
    )
)

COURT_ALCHEMIST = Ally(
    id=CardId.COURT_ALCHEMIST,
    name="Court Alchemist",
    cost=20,
    attack_value=75,
    health=25,
    effect=DamageAllEnemiesEffect(
        amount=[30],
        timing=TimingWindow.ON_PLAY,
    )
)

MERCENARY_CAPTAIN = Ally(
    id=CardId.MERCENARY_CAPTAIN,
    name="Mercenary Captain",
    cost=25,
    attack_value=45,
    health=80,
    effect=GainGoldEffect(
        amount=[15],
        timing=TimingWindow.ON_PLAY,
    )
)

VILLAGE_BLACKSMITH = Ally(
    id=CardId.VILLAGE_BLACKSMITH,
    name="Village Blacksmith",
    cost=30,
    attack_value=20,
    health=130,
    effect=GainIncomeEffect(
        amount=[10],
        timing=TimingWindow.ON_PLAY,
    )
)

JOUSTING_CHAMPION = Ally(
    id=CardId.JOUSTING_CHAMPION,
    name="Jousting Champion",
    cost=35,
    attack_value=85,
    health=90,
    effect=GainGoldEffect(
        amount=[15],
        timing=TimingWindow.END_OF_TURN,
    )
)

DIRE_WOLF = Ally(
    id=CardId.DIRE_WOLF,
    name="Dire Wolf",
    cost=40,
    attack_value=125,
    health=75,
    effect=DrawCardsEffect(
        amount=[2],
        timing=TimingWindow.ON_PLAY,
    )
)

CASTLE_WARD = Ally(
    id=CardId.CASTLE_WARD,
    name="Castle Ward",
    cost=45,
    attack_value=65,
    health=160,
    effect=None  # This card has no effect
)

HIGHWAYMANS_AMBUSH = Ally(
    id=CardId.HIGHWAYMANS_AMBUSH,
    name="Highwayman's Ambush",
    cost=50,
    attack_value=55,
    health=195,
    effect=DamageAllEnemiesEffect(
        amount=[25],
        timing=TimingWindow.ON_PLAY,
    )
)

BANDIT_OUTLAW = Ally(
    id=CardId.BANDIT_OUTLAW,
    name="Bandit Outlaw",
    cost=55,
    attack_value=115,
    health=135,
    effect=GainGoldEffect(
        amount=[10],
        timing=TimingWindow.ON_DEATH,
    )
)

UNDEAD_CREATURES = Ally(
    id=CardId.UNDEAD_CREATURES,
    name="Undead Creatures",
    cost=60,
    attack_value=150,
    health=150,
    effect=DamageAllEnemiesEffect(
        amount=[40],
        timing=TimingWindow.END_OF_TURN,
    )
)

HIGHLAND_SCOUT = Ally(
    id=CardId.HIGHLAND_SCOUT,
    name="Highland Scout",
    cost=65,
    attack_value=200,
    health=125,
    effect=DrawCardsEffect(
        amount=[3],
        timing=TimingWindow.ON_PLAY,
    )
)

BOW_MARSHAL = Ally(
    id=CardId.BOW_MARSHAL,
    name="Bow Marshal",
    cost=70,
    attack_value=175,
    health=175,
    effect=DamageAllEnemiesEffect(
        amount=[50],
        timing=TimingWindow.ON_PLAY,
    )
)

FOREST_GUARDIAN = Ally(
    id=CardId.FOREST_GUARDIAN,
    name="Forest Guardian",
    cost=75,
    attack_value=75,
    health=300,
    effect=HealAllAlliesEffect(
        amount=[250],
        timing=TimingWindow.ON_PLAY,
    )
)

TITAN_OVERLORD = Ally(
    id=CardId.TITAN_OVERLORD,
    name="Titan Overlord",
    cost=80,
    attack_value=250,
    health=250,
    effect=DamageAllEnemiesEffect(
        amount=[100],
        timing=TimingWindow.END_OF_TURN,
    )
)

# Export all cards in a dictionary for easy reference
CARD_CATALOG = {
    "SIEGE_ENGINEER": SIEGE_ENGINEER,
    "ROYAL_FALCONER": ROYAL_FALCONER,
    "WANDERING_MINSTREL": WANDERING_MINSTREL,
    "COURT_ALCHEMIST": COURT_ALCHEMIST,
    "MERCENARY_CAPTAIN": MERCENARY_CAPTAIN,
    "VILLAGE_BLACKSMITH": VILLAGE_BLACKSMITH,
    "JOUSTING_CHAMPION": JOUSTING_CHAMPION,
    "DIRE_WOLF": DIRE_WOLF,
    "CASTLE_WARD": CASTLE_WARD,
    "HIGHWAYMANS_AMBUSH": HIGHWAYMANS_AMBUSH,
    "BANDIT_OUTLAW": BANDIT_OUTLAW,
    "UNDEAD_CREATURES": UNDEAD_CREATURES,
    "HIGHLAND_SCOUT": HIGHLAND_SCOUT,
    "BOW_MARSHAL": BOW_MARSHAL,
    "FOREST_GUARDIAN": FOREST_GUARDIAN,
    #"TITAN_OVERLORD": TITAN_OVERLORD
}