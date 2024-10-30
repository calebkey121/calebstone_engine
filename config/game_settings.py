"""
Game-wide configuration constants.
All game settings and constants are defined here and can be imported from game_engine.config
"""

### HERO SETTINGS ###
HERO_STARTING_HEALTH = 1000
HERO_MAX_HEALTH = 1000

### PLAYER SETTINGS ###
PLAYER_MAX_GOLD = 100
PLAYER_MAX_HAND_SIZE = 10
PLAYER_MAX_INCOME = 999999

### DECK SETTINGS ###
DECK_STARTING_NUM_CARDS = 45

### ARMY SETTINGS ###
ARMY_MAX_SIZE = 7

### GAME PROGRESSION SETTINGS ###
INCOME_PER_X_ROUNDS = 5
X_ROUNDS = 2

### GAME START SETTINGS ###
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