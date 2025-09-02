from .game_state import GameState
from .game_logic import GameLogic
from .player_config import PlayerConfig
from calebstone_engine.output import NoOutputHandler
from calebstone_engine.tracking import GameLogger
from typing import Optional

class GameManager:
    # consider accepting a random seed
    # might need some looking at for human player
    def __init__(self,
                 p1_config: PlayerConfig, 
                 p2_config: PlayerConfig,
                 logger: Optional[GameLogger] = None,
                 seed: Optional[int] = None):
        
        self.game_state = GameState(
            p1_hero=p1_config.hero_name,
            p2_hero=p2_config.hero_name,
            p1_deck=p1_config.build_deck(),
            p2_deck=p2_config.build_deck()
        )
        self.p1_controller = p1_config.get_controller()
        self.p2_controller = p2_config.get_controller()
        self.logger = logger or GameLogger(log_file="game_logs.jsonl")
        self.output_handler = NoOutputHandler() # ActionHistoryFileHandler("game_history.log")
        self.seed = seed
        
        self.start_game()
    
    def start_game(self):
        """Initialize game state"""
        # Optional determinism for shuffles/coin flips
        if self.seed is not None:
            import random
            random.seed(self.seed)

        GameLogic.start_game(self.game_state)
        self.logger.start_game(self.game_state)

        # Write a header to the selected output handler
        if hasattr(self.output_handler, 'display_header'):
            self.output_handler.display_header(self.game_state, seed=self.seed)

        # Begin the first turn and record the turn-start state
        GameLogic.start_turn(self.game_state)
        self.output_handler.display_state(self.game_state)
    
    def process_turn(self):
        """Process actions until turn is complete"""
        if GameLogic.is_game_over(self.game_state):
            return True

        p1_turn = self.game_state.current_player == self.game_state.p1
        current_controller = self.p1_controller if p1_turn else self.p2_controller

        action = current_controller.get_action(self.game_state)
        if action:
            self.output_handler.display_action(action, self.game_state)
            GameLogic.process_turn(self.game_state, action)
            
            is_turn_complete = (GameLogic.is_game_over(self.game_state) or 
                              action["type"] == "end_turn")
            
            if is_turn_complete and not GameLogic.is_game_over(self.game_state):
                GameLogic.start_turn(self.game_state)
                self.output_handler.display_state(self.game_state)
                
            return is_turn_complete
        
        return False  # Return if turn is over
    
    def run_game(self):
        """Run game to completion"""
        while not GameLogic.is_game_over(self.game_state):
            self.process_turn() # consider when controller isn't returning anything...
        self.logger.end_game(self.game_state)

    @staticmethod
    def run_simulation(p1_config: PlayerConfig, p2_config: PlayerConfig, num_games: int = 1000, log_file: str = "simulation_results.jsonl"):
        """Run multiple games with random controllers"""
        logger = GameLogger(log_file=log_file)
        for _ in range(num_games):
            game = GameManager(p1_config, p2_config, logger=logger)
            game.run_game()
        return logger
