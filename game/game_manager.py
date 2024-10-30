
from .game_state import GameState, GameResult
from .game_logic import GameLogic
from game_engine.cards import create_deck, DeckType
from game_engine.controllers import RandomController
from game_engine.output import NoOutputHandler
from game_engine.tracking import GameLogger
from typing import Optional

"""
Purpose:
    This class manages the game flow and game logic. It controls what happens during a player’s turn and resolves interactions between players, allies, heroes, etc.
Responsibilities:
    Run the main game loop, switching between players and calling methods on GameState and the Player class.
    Resolve actions: When a player performs an action (play card, attack), the GameManager ensures it’s valid and calls the appropriate methods on the game state and players.
    Handle inter-player interactions (e.g., Player 1 attacking Player 2’s ally).
Notes:
    The GameManager orchestrates the game flow but doesn’t hold the game state directly (that’s the job of GameState).
    It interacts with the Player class and GameState to execute actions, but it doesn’t modify state directly—this is done via the player methods (play_card(), take_damage(), etc.).
"""
class GameManager:
    def __init__(self, logger: Optional[GameLogger] = None):
        self.game_state = GameState(player1Hero="Caleb", player2Hero="Dio", player1Deck=create_deck(DeckType.TEST), player2Deck=create_deck(DeckType.TEST))
        self.player1_controller = RandomController()
        self.player2_controller = RandomController()
        self.output_handler = NoOutputHandler()
        self.logger = logger or GameLogger(log_file="game_logs.jsonl")
        self.start_game()
    
    def start_game(self):
        GameLogic.start_game(self.game_state)
        self.logger.start_game(self.game_state)
        self.run_game()
    
    def print_result(self) -> None:
        result_messages = {
            GameResult.IN_PROGRESS: "Game isn't over",
            GameResult.TIE: "It's a tie!",
            GameResult.PLAYER1_WIN: "Player 1 wins!",
            GameResult.PLAYER2_WIN: "Player 2 wins!"
        }
        print(result_messages[self.get_result()])

    def run_game(self):
        while not GameLogic.is_game_over(self.game_state):
            GameLogic.start_turn(self.game_state)
            # Display or log the result of the action
            
            current_controller = self.player1_controller if self.game_state.is_player1_turn() else self.player2_controller
            player = self.game_state.current_player
            opponent = self.game_state.opponent_player
            while ( action := current_controller.get_action(self.game_state) ):
                if action["type"] == "play_card":
                    card = player._hand[action["card_index"]]
                elif action["type"] == "attack":
                    attacker = player.army.get_all()[action["attacker_index"]]
                    target = opponent.army.get_all()[action["target_index"]]
                self.output_handler.display_action(action, self.game_state)
                GameLogic.process_turn(self.game_state, action)
                if GameLogic.is_game_over(self.game_state) or action["type"] == "end_turn":
                    break
        self.end_game()
    
    def end_game(self):
        self.logger.end_game(self.game_state)
        
def main():
    game = GameManager()

if __name__ == "__main__":
    main()
