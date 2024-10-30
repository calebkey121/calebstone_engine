from game_engine.effects import *
from tests.TestFramework import GameTestCase
from game_engine.GameLogic import GameLogic
from game_engine.Ally import Ally

class CombatTest(GameTestCase):
    def test_attack_scenarios(self):
        """Test various attack scenarios"""
        self.setUp()
        
        # Create test players with initial state
        test_player1 = self.create_player(
            hero_health=200,
            gold=10,
            board=[
                Ally(name="Hero Attacker", cost=2, attack=5, health=5),
                Ally(name="Surviving Attacker", cost=2, attack=2, health=4),
                Ally(name="Killing Attacker", cost=3, attack=6, health=6),
                Ally(name="Dying Attacker", cost=1, attack=2, health=2)
            ]
        )
        
        test_player2 = self.create_player(
            hero_health=200,
            gold=10,
            board=[
                Ally(name="Surviving Defender", cost=2, attack=1, health=5),
                Ally(name="Dying Defender", cost=2, attack=2, health=4),
                Ally(name="Strong Defender", cost=4, attack=4, health=8)
            ]
        )
        
        # Set up game state
        self.game_state.player1 = test_player1
        self.game_state.player2 = test_player2
        self.game_state.current_player = test_player1
        self.game_state.opponent_player = test_player2
        
        # Execute attacks
        attacks = [
            {"type": "attack", "attacker_index": 1, "target_index": 0},  # Hero attack
            {"type": "attack", "attacker_index": 2, "target_index": 1},  # Surviving attack
            {"type": "attack", "attacker_index": 3, "target_index": 2},  # Killing attack
            {"type": "attack", "attacker_index": 4, "target_index": 2}   # Dying attack
        ]
        
        for attack in attacks:
            GameLogic.process_turn(self.game_state, attack)
        
        # Assert final state for player 1
        self.assert_player_state(
            self.game_state.player1,
            {
                'gold': 10,
                'board': [
                    {'name': "Hero Attacker", 'attack': 5, 'health': 5, 'ready': False},
                    {'name': "Surviving Attacker", 'attack': 2, 'health': 3, 'ready': False},
                    {'name': "Killing Attacker", 'attack': 6, 'health': 4, 'ready': False}
                ]
            },
            "Player 1 state after attacks"
        )
        
        # Assert final state for player 2
        self.assert_player_state(
            self.game_state.player2,
            {
                'hero_health': 195,
                'gold': 10,
                'board': [
                    {'name': "Surviving Defender", 'attack': 1, 'health': 3},
                    {'name': "Strong Defender", 'attack': 4, 'health': 6}
                ]
            },
            "Player 2 state after attacks"
        )
