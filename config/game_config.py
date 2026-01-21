from dataclasses import dataclass, field
from typing import Dict

GAME_START = {
    'FIRST_PLAYER': {
        'GOLD': 15,
        'INCOME': 10,
        'CARDS_DRAWN': 4
    },
    'SECOND_PLAYER': {
        'GOLD': 20,
        'INCOME': 10,
        'CARDS_DRAWN': 5
    }
}

@dataclass(frozen=True)
class GameConfig:
    # Hero settings
    hero_starting_health: int = 1000
    hero_max_health: int = 1000

    # Player settings
    player_max_gold: int = 200
    player_max_hand_size: int = 10
    player_max_income: int = 75

    # Deck settings
    deck_start_size: int = 45

    # Army settings
    army_max_size: int = 7

    # Game progression settings
    income_per_x_rounds: int = 5
    x_rounds: int = 2

    # Game start settings
    game_start: Dict[str, int] = field(default_factory=lambda: GAME_START.copy())
