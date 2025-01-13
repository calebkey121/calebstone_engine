from dataclasses import dataclass
from typing import List, Dict, Optional
from game_engine.GameState import GameState
from game_engine.GameLogic import GameLogic
from game_engine.Ally import Ally
from tests.TestFramework import GameTestCase

@dataclass
class PlayerScenario:
    """Represents initial setup and expected end state for a player"""
    # Initial state
    player_name: str = None
    hero_name: str = None
    hero_health: int = 200
    gold: int = 0
    income: int = 0
    hand: List[Ally] = None
    board: List[Ally] = None
    deck_list: List[Ally] = None
    
    # Expected final state
    expected_final_state: Dict = None

def run_scenario(test_case: GameTestCase,
                player1: PlayerScenario,
                player2: PlayerScenario,
                actions: List[List[Dict]],
                message: str = "Scenario failed"):
    """
    Runs a game scenario using the existing GameTestCase framework.
    
    Args:
        test_case: The GameTestCase instance
        player1: PlayerScenario for player 1
        player2: PlayerScenario for player 2
        actions: List of turns, where each turn is a list of actions
        message: Message to display on failure
    """
    # Initialize players using existing framework
    test_player1 = test_case.create_player(
        player_name=player1.player_name,
        hero_name=player1.hero_name,
        hero_health=player1.hero_health,
        gold=player1.gold,
        income=player1.income,
        hand=player1.hand or [],
        board=player1.board or [],
        deck_list=player1.deck_list or []
    )
    
    test_player2 = test_case.create_player(
        player_name=player2.player_name,
        hero_name=player2.hero_name,
        hero_health=player2.hero_health,
        gold=player2.gold,
        income=player2.income,
        hand=player2.hand or [],
        board=player2.board or [],
        deck_list=player2.deck_list or []
    )
    
    # Set up game state
    test_case.game_state.player1 = test_player1
    test_case.game_state.player2 = test_player2
    test_case.game_state.current_player = test_player1
    test_case.game_state.opponent_player = test_player2
    test_case.game_state.total_turns = 1
    test_case.game_state.current_round = 1
    
    # Process all turns
    for turn_actions in actions:
        # Start turn
        GameLogic.start_turn(test_case.game_state)
        
        # Process all actions for this turn
        for action in turn_actions:
            GameLogic.process_turn(test_case.game_state, action)
            
            # If this is an end_turn action, switch players
            if action["type"] == "end_turn":
                break
    
    # Verify final states using existing assert method
    if player1.expected_final_state:
        test_case.assert_player_state(
            test_case.game_state.player1,
            player1.expected_final_state,
            f"{message} - Player 1 state mismatch"
        )
    
    if player2.expected_final_state:
        test_case.assert_player_state(
            test_case.game_state.player2,
            player2.expected_final_state,
            f"{message} - Player 2 state mismatch"
        )
