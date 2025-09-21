from calebstone_engine.core import Ally
from calebstone_engine.effects import *

# Modified existing cards with scaled up values
SIEGE_ENGINEER = Ally(
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
    name="Castle Ward",
    cost=45,
    attack_value=65,
    health=160,
    effect=None  # This card has no effect
)

HIGHWAYMANS_AMBUSH = Ally(
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
    name="Forest Guardian",
    cost=75,
    attack_value=75,
    health=300,
    effect=HealAllAlliesEffect(
        amount=[250],
        timing=TimingWindow.ON_PLAY,
    )
)

# New epic-scale card
TITAN_OVERLORD = Ally(
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
    "TITAN_OVERLORD": TITAN_OVERLORD
}