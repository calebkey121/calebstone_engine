from .army import Army
from .deck import Deck
from .card import Card
from .ally import Ally
from .hero import Hero
from .signal import *
from game_engine.config import *
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


# Old Player, too much boilerplate, delete once happy with above
# from game_engine.Army import Army
# from game_engine.Deck import Deck
# from game_engine.Card import Card
# from game_engine.Ally import Ally
# from game_engine.Hero import Hero
# from game_engine.Signal import *
# from config.GameSettings import *
# from dataclasses import dataclass, field

# @dataclass
# class PlayerSignals:
#    """Signals owned by the player"""
#    on_gold_gained: Signal = field(default_factory=Signal)
#    on_gold_spent: Signal = field(default_factory=Signal)
#    on_income_gained: Signal = field(default_factory=Signal)
#    on_income_lost: Signal = field(default_factory=Signal)
#    on_fatigue: Signal = field(default_factory=Signal)
#    on_card_played: Signal = field(default_factory=Signal)

# class Player:
#    def __init__(self,
#                 player_name,
#                 hero_name, 
#                 deck_list,
#                 player_subscribers: dict = None,
#                 ally_subscribers: dict = None,
#                 hero_subscribers: dict = None):
       
#        # Store hero subscribers for hero initialization
#        self._hero_subscribers = hero_subscribers or {
#            "on_death": [],
#            "on_damage_taken": [],
#            "on_heal": [],
#            "on_attack": [],
#            "on_damage_dealt": []
#        }
       
#        # Initialize core components
#        self._name = player_name
#        self._hero = Hero(hero_name, hero_subscribers=self._hero_subscribers)
#        self._deck = Deck(deck_list)
#        self._army = Army()
#        self._hand = []
#        self._max_hand_size = PLAYER_MAX_HAND_SIZE
#        self._gold = 0
#        self._income = 0

#        # Initialize signals
#        self.signals = PlayerSignals()
       
#        # Store ally subscribers for use when allies are played
#        self._ally_subscribers = ally_subscribers or {
#            "on_death": [],
#            "on_attack": [],
#            "on_damage_dealt": [],
#            "on_damage_taken": []
#        }
#        self._ally_subscribers["on_death"].append(lambda x: self._army.remove_dead_allies(x))

#        # Connect player-level subscribers
#        for signal_name, callbacks in (player_subscribers or {}).items():
#            if hasattr(self.signals, signal_name):
#                signal = getattr(self.signals, signal_name)
#                signal.connect(callbacks)

#    def __repr__(self):
#        return self._name

#    # Resource Properties
#    @property
#    def gold(self):
#        return self._gold
   
#    @gold.setter
#    def gold(self, new_amount):
#        change_amount = new_amount - self.gold
#        if change_amount >= 0:
#            self.signals.on_gold_gained.emit(GameEventData())
#        else:
#            self.signals.on_gold_spent.emit(-change_amount)
#        self._gold = new_amount

#    @property
#    def income(self):
#        return self._income
   
#    @income.setter
#    def income(self, new_amount):
#        change_amount = new_amount - self.income
#        if change_amount >= 0:
#            self.signals.on_income_gained.emit(change_amount)
#        else:
#            self.signals.on_income_lost.emit(change_amount)
#        self._income += change_amount
   
#    # Status Queries
#    def get_hero_status(self):
#        return {
#            "name": self._hero._name,
#            "attack": self._hero._attack,
#            "health": self._hero.health
#        }

#    def get_army_status(self):
#        return [{"name": ally._name, "attack": ally._attack, "health": ally.health, "cost": ally._cost} 
#                for ally in self._army.get_army()]

#    def get_hand_status(self):
#        return [{"name": card._name, "attack": card._attack, "health": card.health, "cost": card._cost} 
#                for card in self._hand]

#    # Hero Methods
#    def hero_health(self):
#        return self._hero.health

#    def is_dead(self):
#        return self.hero_health() <= 0

#    # Deck Methods
#    def out_of_cards(self):
#        return self._deck.current_num_cards() <= 0

#    # Army Methods
#    def get_army_size(self):
#        return self._army.army_size()

#    def available_targets(self):
#        available_targets = []
#        available_targets.append(0)  # for hero
#        for idx, ally in enumerate(self._army.get_army()):
#            available_targets.append(idx + 1)  # army starts at 1
#        return available_targets

#    def available_attackers(self):
#        available_attackers = []
#        if self._hero.can_attack():
#            available_attackers.append(0)  # for hero
#        for idx, ally in enumerate(self._army.get_army()):
#            if ally.can_attack():
#                available_attackers.append(idx + 1)
#        return available_attackers

#    def all_characters(self):
#        return [self._hero] + self._army.get_army()

#    def in_army(self, ally):
#        return self._army.in_army(ally)

#    # Hand Methods
#    def current_hand_size(self):
#        return len(self._hand)

#    def get_from_hand(self, position):
#        return self._hand[position]

#    def any_cards(self):
#        return len(self._hand) > 0

#    def hand_is_full(self):
#        return self.current_hand_size() == self.max_hand_size()

#    def any_playable_cards(self):
#        playable = False
#        for i in self._hand:
#            if i.cost() <= self.gold:
#                playable = True
#        return playable

#    def playable_cards(self):
#        playable = []
#        for idx, card in enumerate(self._hand):
#            if card._cost <= self.gold:
#                playable.append(idx)
#        return playable

#    def playable_card(self, card):
#        if not isinstance(card, Card):
#            raise ValueError(f"Checking non Card type. Got: {card}")
#        playable = False
#        if card.cost() <= self.gold():
#            playable = True
#        return playable

#    def playable_hand(self):
#        playable = []
#        for i in self._hand:
#            if i.cost() <= self.gold:
#                playable.append(i)
#        return playable

#    def in_hand(self, card):
#        if not isinstance(card, Card):
#            raise ValueError(f"Checking non Card type. Got: {card}")
#        return card in self._hand

#    def has_enough_gold(self, index):
#        if not isinstance(index, int):
#            raise ValueError(f"Checking non int index. Got: {index}")
#        return self._hand[index]._cost <= self.gold

#    # Game Actions
#    def ready_up(self):
#        self._hero.ready_up()
#        self._army.ready_up()

#    def call_to_arms(self, ally):
#        if not isinstance(ally, Ally):
#            raise ValueError(f"Tried adding non ally to army. Got: {ally}")
#        self._army.add_ally(ally)

#    def play_ally(self, card):
#        if self._army.is_full() or card._cost > self.gold:
#            raise ValueError("Card unplayable")
#        if not card in self._hand:
#            raise ValueError("Card not in hand!")
#        self._army.add_ally(card)
#        card.ready_down()
#        self.gold -= card._cost
#        self.remove_from_hand(card)
#        self.signals.on_card_played.emit(card)
       
#        # Connect all relevant subscribers to the ally's signals
#        for signal_name, callbacks in self._ally_subscribers.items():
#            if hasattr(card, signal_name):
#                ally_signal = getattr(card, signal_name)
#                ally_signal.connect(callbacks)

#    def max_hand_size(self, new_size=None):
#        if new_size:
#            self._max_hand_size = new_size
#        return self._max_hand_size

#    def remove_from_hand(self, card):
#        if not isinstance(card, Card):
#            raise ValueError(f"Expected Card argument. Got: {card}")
#        for i in self._hand:
#            if i == card:
#                self._hand.remove(i)
#                return
#        raise ValueError("Card was not in hand.")

#    def draw_card(self):
#        if self.out_of_cards():
#            fatigue_damage = self._deck.take_fatigue()
#            self.damage_hero(fatigue_damage)
#            self.signals.on_fatigue.emit(fatigue_damage)
#            return
#        card = self._deck.draw_card()
#        if not self.hand_is_full():
#            self._hand.append(card)

#    def draw_cards(self, number):
#        if not isinstance(number, int) or number < 0:
#            raise ValueError(f"Number of cards to draw must be a positive integer. Got: {number}")
#        for i in range(number):
#            self.draw_card()

#    # Damage and Healing Methods
#    def damage_hero(self, damage):
#        if not isinstance(damage, int):
#            raise ValueError(f"Damage must be an integer. Got: {damage}")
#        self._hero.health -= damage

#    def damage_army(self, damage):
#        if not isinstance(damage, int) or damage < 0:
#            raise ValueError(f"Damage must be a positive integer. Got: {damage}")
#        for ally in self._army._army:
#            ally.health -= damage

#    def damage_all(self, damage):
#        if not isinstance(damage, int) or damage < 0:
#            raise ValueError(f"Damage must be a positive integer. Got: {damage}")
#        self.damage_hero(damage)
#        self.damage_army(damage)

#    def heal_hero(self, heal):
#        if not isinstance(heal, int):
#            raise ValueError(f"Heal amount must be an integer. Got: {heal}")
#        self._hero.health += heal

#    def heal_army(self, heal):
#        if not isinstance(heal, int) or heal < 0:
#            raise ValueError(f"Heal amount must be a positive integer. Got: {heal}")
#        for ally in self._army.get_army():
#            ally.health += heal

#    def heal_all(self, heal):
#        if not isinstance(heal, int) or heal < 0:
#            raise ValueError(f"Heal amount must be a positive integer. Got: {heal}")
#        self.heal_hero(heal)
#        self.heal_army(heal)
