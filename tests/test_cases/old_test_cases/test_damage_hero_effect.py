from game_engine.effects import *
from tests.TestFramework import *
from game_engine.GameLogic import GameLogic
# Example test case:
class DamageEffectsTest(GameTestCase):
    def test_damage_hero_effect(self):
        """Test that an ally's death effect properly damages enemy hero"""
        self.setUp()

        # Create test card
        test_ally = Ally(
            cost=2,
            name="Test Damager",
            attack=2,
            health=2,
            effect=DamageEnemyHeroEffect(
                amount=[7],
                timing=TimingWindow.ON_DEATH,
                text="When this dies, deal 7 damage to the enemy hero"
            )
        )
        
        # Create paired players with initial states
        test_player1, expected_player1 = self.create_player(
            hero_health=200,
            gold=10,
            hand=[test_ally]
        )
        
        test_player2, expected_player2 = self.create_player(
            hero_health=200
        )
        
        # Set up game state with test players
        self.game_state.player1 = test_player1
        self.game_state.player2 = test_player2
        self.game_state.current_player, self.game_state.opponent_player = test_player1, test_player2
        
        # Play the card
        GameLogic.process_turn(self.game_state, {
            "type": "play_card",
            "card_index": 0
        })
        
        # Kill the test ally
        test_ally_on_board = self.game_state.player1._army.get_army()[0]
        test_ally_on_board.health = 0
        
        # Set expected end states
        expected_player1._gold = 8  # 10 - 2 (cost)
        expected_player1._army._army = []  # Ally died
        expected_player1._hand = []  # Card was played
        
        expected_player2._hero._health = 193  # 200 - 7 (death effect damage)
        
        self.assert_gamestate(
            expected_player1=expected_player1,
            expected_player2=expected_player2,
            message="After test ally death effect"
        )
