from typing import List, TYPE_CHECKING
from calebstone_engine.cards.decklists import create_deck
import random
if TYPE_CHECKING:
    from card import Card

class Deck:
    def __init__(self, deck_list, deck_start_size: int):
        deck_list = create_deck(deck_list)
        if len(deck_list) != deck_start_size:
            raise RuntimeError(f"GameConfig.deck_start_size = {deck_start_size}, was given deck_list of size {len(deck_list)}")

        self._deck_list = deck_list
        self._deck_start_size = deck_start_size
        self._fatigue_counter = 0
        self._is_shuffled = False
        self.set_num_cards()

    @property
    def current_num_cards(self):
        return self._current_num_cards
    
    def set_num_cards(self):
        """Sets deck list length"""
        self._current_num_cards = len(self._deck_list)

    def add_card(self, card):
        """Adds card to deck"""
        self._deck_list.append(card)
        self.set_num_cards()

    def remove_card(self, card):
        """Remove specific card from deck"""
        self._deck_list.remove(card)
        self.set_num_cards()

    def out_of_cards(self):
        return self._current_num_cards <= 0

    def shuffle(self):
        """Shuffles deck if not already shuffled"""
        if not self._is_shuffled:
            random.shuffle(self._deck_list)
            self._is_shuffled = True

    def draw_card(self):
        """Draw top card from deck, shuffling first if needed"""
        if self.out_of_cards():
            raise ValueError("Tried drawing a card when out of cards")
            
        if not self._is_shuffled:
            self.shuffle()
            
        # Take from end for efficiency
        card = self._deck_list.pop()
        self.set_num_cards()
        return card
    
    def take_fatigue(self):
        self._fatigue_counter += 1
        return self._fatigue_counter
