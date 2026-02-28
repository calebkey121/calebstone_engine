from calebstone_engine.core.player import Player
from calebstone_engine.config import GameConfig, PlayerConfig
from .game_logic import GameLogic
from enum import Enum, auto
from calebstone_engine.cards.decklists import create_deck

class GameResult(Enum):
    IN_PROGRESS = auto()
    TIE = auto()
    P1_WIN = auto()
    P2_WIN = auto()

class GameState:
    def __init__(self, game_config: GameConfig, p1_config: PlayerConfig, p2_config: PlayerConfig, rng):
        # Create both players with all subscriber types
        self.rng = rng
        self.game_config = game_config
        self.p1 = Player(p1_config, game_config, rng=self.rng)
        self.p2 = Player(p2_config, game_config, rng=self.rng)
        self.current_player = None
        self.opposing_player = None
        self.current_round = 0
        self.who_went_first = None
        self.total_turns = 0 # how many total turns have been taken?
        self.is_first_turn_of_round = True  # Track position within round

    
    def switch_turn(self):
        # Swap players
        self.current_player, self.opposing_player = self.opposing_player, self.current_player
        
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
        targets = self.opposing_player.available_targets()
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
        # End turn is always a legal action.
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
