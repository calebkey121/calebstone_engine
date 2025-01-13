"""
Configuration module for the game engine.
Import all settings using: from game_engine.config import *
"""

from .game_settings import (
    # Hero Settings
    HERO_STARTING_HEALTH,
    HERO_MAX_HEALTH,
    
    # Player Settings
    PLAYER_MAX_GOLD,
    PLAYER_MAX_HAND_SIZE,
    PLAYER_MAX_INCOME,
    
    # Deck Settings
    DECK_STARTING_NUM_CARDS,
    
    # Army Settings
    ARMY_MAX_SIZE,
    
    # Game Progression Settings
    INCOME_PER_X_ROUNDS,
    X_ROUNDS,
    
    # Game Start Settings
    GAME_START,
)

__all__ = [
    # Hero Settings
    'HERO_STARTING_HEALTH',
    'HERO_MAX_HEALTH',
    
    # Player Settings
    'PLAYER_MAX_GOLD',
    'PLAYER_MAX_HAND_SIZE',
    'PLAYER_MAX_INCOME',
    
    # Deck Settings
    'DECK_STARTING_NUM_CARDS',
    
    # Army Settings
    'ARMY_MAX_SIZE',
    
    # Game Progression Settings
    'INCOME_PER_X_ROUNDS',
    'X_ROUNDS',
    
    # Game Start Settings
    'GAME_START',
]
