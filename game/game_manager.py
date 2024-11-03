
from .game_state import GameState, GameResult
from .game_logic import GameLogic
from game_engine.cards import create_deck, DeckType
from game_engine.controllers import RandomController, Controller
from game_engine.output import NoOutputHandler
from game_engine.tracking import GameLogger
from typing import Optional

class GameManager:
    def __init__(self, logger: Optional[GameLogger] = None, 
                 player1_controller: Optional[Controller] = None,
                 player2_controller: Optional[Controller] = None):
        
        self.game_state = GameState(
            player1Hero="Caleb", 
            player2Hero="Dio", 
            player1Deck=create_deck(DeckType.TEST), 
            player2Deck=create_deck(DeckType.TEST)
        )
        self.player1_controller = player1_controller or RandomController()
        self.player2_controller = player2_controller or RandomController()
        self.output_handler = NoOutputHandler()
        self.logger = logger or GameLogger(log_file="game_logs.jsonl")
        
        self.start_game()
    
    def start_game(self):
        """Initialize game state"""
        GameLogic.start_game(self.game_state)
        self.logger.start_game(self.game_state)
        GameLogic.start_turn(self.game_state)
    
    def process_turn(self):
        """Process actions until turn is complete"""
        if GameLogic.is_game_over(self.game_state):
            return True

        current_controller = (self.player1_controller 
                            if self.game_state.is_player1_turn() 
                            else self.player2_controller)

        action = current_controller.get_action(self.game_state)
        if action:
            self.output_handler.display_action(action, self.game_state)
            GameLogic.process_turn(self.game_state, action)
            
            is_turn_complete = (GameLogic.is_game_over(self.game_state) or 
                              action["type"] == "end_turn")
            
            if is_turn_complete and not GameLogic.is_game_over(self.game_state):
                GameLogic.start_turn(self.game_state)
                
            return is_turn_complete
        
        return False  # No action yet
    
    def run_game(self):
        """Run game to completion"""
        while not GameLogic.is_game_over(self.game_state):
            self.process_turn()
        self.logger.end_game(self.game_state)

    @staticmethod
    def run_simulation(num_games: int = 1000, log_file: str = "simulation_results.jsonl"):
        """Run multiple games with random controllers"""
        logger = GameLogger(log_file=log_file)
        for _ in range(num_games):
            game = GameManager(logger=logger)
            game.run_game()
        return logger
