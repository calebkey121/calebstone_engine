from calebstone_engine.core import Player
from .game_logic import GameLogic
from enum import Enum, auto

class GameResult(Enum):
    IN_PROGRESS = auto()
    TIE = auto()
    P1_WIN = auto()
    P2_WIN = auto()

class GameState:
    def __init__(self, p1_hero, p1_deck, p2_hero, p2_deck):
        # Create both players with all subscriber types
        self.p1 = Player(
            player_name="p1",
            hero_name=p1_hero,
            deck_list=p1_deck,
        )
        
        self.p2 = Player(
            player_name="p2",
            hero_name=p2_hero,
            deck_list=p2_deck,
        )

        self.current_player = None
        self.opponent_player = None
        self.current_round = 0
        self.who_went_first = None
        self.total_turns = 0 # how many total turns have been taken?
        self.is_first_turn_of_round = True  # Track position within round

    
    def switch_turn(self):
        # Swap players
        self.current_player, self.opponent_player = self.opponent_player, self.current_player
        
        # Increment turn counter
        self.total_turns += 1
        
        # Update round tracking
        if self.is_first_turn_of_round:
            self.is_first_turn_of_round = False
        else:
            self.is_first_turn_of_round = True
            self.current_round += 1
    
    # Possible Actions
    def possible_cards_to_play(self):
        if self.current_player.army.is_full():
            return []
        actions = []
        playable_cards = self.current_player.playable_cards()
        for card in playable_cards:
            actions.append({
                "type": "play_card",
                "card_index": card
            })
        return actions
    
    def possible_attacks(self):
        actions = []
        attackers = self.current_player.available_attackers()
        targets = self.opponent_player.available_targets()
        for attacker in attackers:
            for target in targets:
                actions.append({
                    "type": "attack",
                    "attacker_index": attacker,
                    "target_index": target
                })
        return actions

    def possible_actions(self):
        actions = self.possible_cards_to_play() + self.possible_attacks()
        if not actions:
            actions.append({
                "type": "end_turn"
            })
        return actions


    def get_result(self) -> GameResult:
        if not GameLogic.is_game_over(self):
            return GameResult.IN_PROGRESS
        
        if self.p1.is_dead() and self.p2.is_dead():
            return GameResult.TIE
        elif self.p1.is_dead():
            return GameResult.P2_WIN
        else:
            return GameResult.P1_WIN

    def to_vector(self):
        # Convert game state to vector (for ML or saving)
        return [
            self.p1.health, len(self.p1.hand), len(self.p1.army), 
            self.p2.health, len(self.p2.hand), len(self.p2.army),
            self.round_count, self.total_turns
        ]
