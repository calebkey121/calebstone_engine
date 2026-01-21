from .game_state import GameState
from .game_logic import GameLogic
from calebstone_engine.config import PlayerConfig, GameConfig
from calebstone_engine.output import NoOutputHandler
from calebstone_engine.tracking import SimulationRecord, GameRecordEmitter
from calebstone_engine.controllers import Controller
from typing import Optional
import random, secrets

class GameManager:
    def __init__(self,
                 game_config: GameConfig = GameConfig(),
                 p1_config: PlayerConfig = PlayerConfig(),
                 p2_config: PlayerConfig = PlayerConfig(),
                 log_file: Optional[str] = None,
                 seed: Optional[int] = None):

        self.seed = int(seed) if seed is not None else secrets.randbits(32)
        self.rng = random.Random(self.seed)
        self.p1 = p1_config
        self.p2 = p2_config
        self.p1_controller = Controller.create_controller(p1_config.controller)
        self.p2_controller = Controller.create_controller(p2_config.controller)
        self.game_state = GameState(
            game_config=game_config,
            p1_config=p1_config,
            p2_config=p2_config,
            rng=self.rng,
        )
        self.game_record = GameRecordEmitter(log_file=log_file)
        self.output_handler = NoOutputHandler() # ActionHistoryFileHandler("game_history.log")
        
        self.start_game()
    
    def start_game(self):
        """Initialize game state"""
        GameLogic.start_game(self.game_state)
        self.game_record.start_game(self.game_state)

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
        self.game_record = self.game_record.end_game(self.game_state, p1_id=self.p1.player_id, p2_id=self.p2.player_id, seed=self.seed)

    @staticmethod
    def run_simulation(game_config: GameConfig, p1_config: PlayerConfig, p2_config: PlayerConfig, num_games: int = 1000, log_file: str = "simulation_results.jsonl"):
        """Run multiple games with random controllers"""
        logger = SimulationRecord()
        for _ in range(num_games):
            game = GameManager(game_config, p1_config, p2_config)
            game.run_game()
            logger.record(game.game_record)
        return logger
    
def main():
    a = GameManager()

if __name__ == "__main__":
    main()
