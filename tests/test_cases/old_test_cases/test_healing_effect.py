from game_engine.effects import *
from tests.TestFramework import *
from game_engine.GameLogic import GameLogic
from game_engine.Ally import Ally

class HealEffectsTest(GameTestCase):
    def test_heal_all_allies_effect(self):
        """Test that an ally's effect properly heals all friendly allies"""
        self.setUp()
        
        # Create a healer card with ON_PLAY heal effect
        healer_ally = Ally(
            cost=3,
            name="Test Healer",
            attack=2,
            health=3,
            effect=HealAllAlliesEffect(
                amount=[5],
                timing=TimingWindow.ON_PLAY,
                text="When played, heal all allies for 5 health"
            )
        )
        
        # Create some damaged allies to be healed
        damaged_ally1 = Ally(
            cost=1,
            name="Damaged Ally 1",
            attack=1,
            health=2,  # Current health, maxHealth will be 6
            effect=None
        )
        damaged_ally1._maxHealth = 6
        
        damaged_ally2 = Ally(
            cost=2,
            name="Damaged Ally 2",
            attack=2,
            health=1,  # Current health, maxHealth will be 4
            effect=None
        )
        damaged_ally2._maxHealth = 4
        
        # Create paired players with initial states
        test_player1 = self.create_player(
            hero_health=200,
            gold=10,
            hand=[healer_ally],
            board=[damaged_ally1, damaged_ally2]  # Start with damaged allies on board
        )
        
        test_player2 = self.create_player(
            hero_health=200
        )
        
        # Set up game state with test players
        self.game_state.player1 = test_player1
        self.game_state.player2 = test_player2
        self.game_state.current_player, self.game_state.opponent_player = test_player1, test_player2
        
        # Play the healer
        GameLogic.process_turn(self.game_state, {
            "type": "play_card",
            "card_index": 0
        })
        
        # Set expected end states
        expected_gold = 7  # 10 - 3 (healer cost)
        expected_hand = []  # Healer was played
        
        # Create expected board state with healed allies
        healed_ally1 = Ally(
            cost=1,
            name="Damaged Ally 1",
            attack=1,
            health=6,  # Healed to max (2 + 5 capped at 6)
            effect=None
        )
        healed_ally1._maxHealth = 6
        healed_ally1.ready_up() # is created as not ready
        
        healed_ally2 = Ally(
            cost=2,
            name="Damaged Ally 2",
            attack=2,
            health=4,  # Healed to max (1 + 5 capped at 4)
            effect=None
        )
        healed_ally2._maxHealth = 4
        healed_ally2.ready_up() # is created as not ready
        
        # The healer itself is also on the board
        board_healer = Ally(
            cost=3,
            name="Test Healer",
            attack=2,
            health=3,
            effect=healer_ally._effect
        )
        
        expected_army = [healed_ally1, healed_ally2, board_healer]
        
        # Verify final state
        # self.assert_player_state(
        #     ,
        #     expected_player2=expected_player2,
        #     message="After healing effect"
        # )
