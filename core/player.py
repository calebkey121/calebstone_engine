from .army import Army
from .deck import Deck
from .card import Card
from .ally import Ally
from .hero import Hero
from .signal import *
from calebstone_engine.config import *
from dataclasses import dataclass, field

@dataclass
class PlayerSignals:
   """Signals owned by the player"""
   on_fatigue: Signal = field(default_factory=Signal)
   on_card_played: Signal = field(default_factory=Signal)
   on_gold_gained: Signal = field(default_factory=Signal)
   on_gold_spent: Signal = field(default_factory=Signal)
   on_income_gained: Signal = field(default_factory=Signal)
   on_income_lost: Signal = field(default_factory=Signal)

class Player:
    def __init__(self, player_name, hero_name, deck_list):
        # Initialize core components
        self._name = player_name
        self._deck = Deck(deck_list)
        self._army = Army(Hero(hero_name))
        self._hand = []
        self._max_hand_size = PLAYER_MAX_HAND_SIZE
        self._gold = 0
        self._income = 0
        # have self.hero, just points to Army

        # Initialize signals
        self.signals = PlayerSignals()
        
        # Store ally subscribers that should be added on play
        self._ally_subscribers = {
            "on_death" : lambda x: self.army.remove_dead_allies()
        }

    def __repr__(self):
        return self._name

    @property
    def hero(self):
        return self.army.hero

    # Resource Properties
    @property
    def gold(self):
        return self._gold

    @gold.setter
    def gold(self, new_amount):
        change_amount = new_amount - self.gold
        if change_amount >= 0:
            self.signals.on_gold_gained.emit(ResourceEventData(source=self, amount=change_amount))
        else:
            self.signals.on_gold_spent.emit(ResourceEventData(source=self, amount=-change_amount))
        self._gold = new_amount

    @property
    def income(self):
        return self._income

    @income.setter
    def income(self, new_amount):
        change_amount = new_amount - self.income
        if change_amount >= 0:
            self.signals.on_income_gained.emit(ResourceEventData(source=self, amount=change_amount))
        else:
            self.signals.on_income_lost.emit(ResourceEventData(source=self, amount=-change_amount))
        self._income += change_amount

    @property
    def army(self):
        return self._army

    # Core Game Actions
    def play_ally(self, card):
        if self.army.is_full() or card.cost > self.gold:
            raise ValueError("Card unplayable")
        if not card in self._hand:
            raise ValueError("Card not in hand!")
            
        self.army.add_ally(card)
        card.ready_down()
        self.gold -= card._cost
        self.remove_from_hand(card)
        self.signals.on_card_played.emit(CardPlayedEventData(source=self, card=card))
        
        # Connect all relevant subscribers to the ally's signals
        for signal_name, callbacks in self._ally_subscribers.items():
            if hasattr(card.signals, signal_name):
                ally_signal = getattr(card.signals, signal_name)
                ally_signal.connect(callbacks)

    def draw_card(self):
        if self._deck.out_of_cards():
            fatigue_damage = self._deck.take_fatigue()
            self.hero.health -= fatigue_damage
            self.signals.on_fatigue.emit(FatigueEventData(source=self, damage=fatigue_damage))
            return

        card = self._deck.draw_card()
        if not self.hand_is_full():
            self._hand.append(card)
        

    def draw_cards(self, number):
        if not isinstance(number, int) or number < 0:
            raise ValueError(f"Number of cards to draw must be positive. Got: {number}")
        for _ in range(number):
            self.draw_card()

    # Hand Management
    def num_cards_in_hand(self):
        return len(self._hand)

    def card_at(self, idx):
        return self._hand[idx]

    def remove_from_hand(self, card):
        if not isinstance(card, Card):
            raise ValueError(f"Expected Card argument. Got: {card}")
        try:
            self._hand.remove(card)
        except ValueError:
            raise ValueError("Card was not in hand.")

    def hand_is_full(self):
        return len(self._hand) >= self._max_hand_size

    def playable_cards(self):
        """Returns indices of playable cards"""
        return [idx for idx, card in enumerate(self._hand) if card.cost <= self.gold]

    # Game State Queries
    def available_targets(self):
        """Returns indices of valid targets (0=hero, 1+=army)"""
        return list(range(0, len(self.army.get_all())))

    def available_attackers(self):
        """Returns indices of characters that can attack (0=hero, 1+=army)"""
        attackers = []
        return attackers + [i for i, char in enumerate(self.army.get_all()) if char.can_attack()]

    def all_characters(self):
        """Returns list of all characters that can be targeted"""
        return self.army.get_all()

    def is_dead(self):
        return self.hero.health <= 0
