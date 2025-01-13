from dataclasses import dataclass
from typing import Optional, Any

# Base class for all game events
@dataclass
class GameEventData:
    """Base class for all game events"""
    source: Any  # The originator of the event
    
    def __post_init__(self):
        if not self.source:
            raise ValueError("Event source cannot be None")

# Combat-related events
@dataclass
class DamageEventData(GameEventData):
    """Data for damage events"""
    target: Any  # The target being attacked
    effective_damage: int  # Actual damage dealt (considering health)
    extra_damage: int = 0  # Amount of damage beyond what was needed

@dataclass
class HealEventData(GameEventData):
    """Data for healing events"""
    target: Any
    effective_heal: int  # Actual healing done (considering max health)
    extra_heal: int = 0  # Amount of healing beyond max health

# Resource-related events
@dataclass
class ResourceEventData(GameEventData):
    """Data for gold gain/loss events"""
    # source is None if its a typical game effect like at start of round
    amount: int  # Positive for gain, negative for loss

# Card-related events
@dataclass
class CardPlayedEventData(GameEventData):
    """Data for when a card is played"""
    card: Any

@dataclass
class CardDrawnEventData(GameEventData):
    """Data for when a card is drawn"""
    card: Any

# Game state events
@dataclass
class FatigueEventData(GameEventData):
    """Data for fatigue damage events"""
    damage: int

class Signal:
    def __init__(self):
        self._subscribers = []
        
    def connect(self, subscriber):
        if isinstance(subscriber, list):
            self._subscribers.extend(subscriber)
        else:
            self._subscribers.append(subscriber)
            
    def emit(self, data: GameEventData = None):
        for subscriber in self._subscribers:
            subscriber(data)
