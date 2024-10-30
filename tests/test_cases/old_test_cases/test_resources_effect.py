from game_engine.effects import *
from tests.TestFramework import *
from game_engine.GameLogic import GameLogic

class ResourceEffectsTest(GameTestCase):
    def test_gain_gold_effect(self):
        """Test that an ally properly gives gold when played"""
        self.setUp()
        
        # Create a card that gives gold on play
        gold_giver = Ally(
            cost=2,
            name="Gold Giver",
            attack=1,
            health=1,
            effect=GainGoldEffect(
                amount=[3],
                timing=TimingWindow.ON_PLAY,
                text="When played, gain 3 gold"
            )
        )
        
        # Create paired players with initial states
        test_player1, expected_player1 = self.create_player(
            hero_health=200,
            gold=5,
            hand=[gold_giver]
        )
        
        test_player2, expected_player2 = self.create_player(
            hero_health=200
        )
        
        # Set up game state
        self.game_state.player1 = test_player1
        self.game_state.player2 = test_player2
        self.game_state.current_player, self.game_state.opponent_player = test_player1, test_player2
        
        # Play the card
        GameLogic.process_turn(self.game_state, {
            "type": "play_card",
            "card_index": 0
        })
        
        # Set expected end states
        expected_player1._gold = 6  # 5 - 2 (cost) + 3 (effect)
        expected_player1._hand = []  # Card was played
        expected_player1._army._army = [gold_giver]  # Card is now on board
        
        self.assert_gamestate(
            expected_player1=expected_player1,
            expected_player2=expected_player2,
            message="After gold gain effect"
        )

    def test_gain_income_effect(self):
        """Test that an ally properly increases income when played"""
        self.setUp()
        
        # Create a card that gives income on play
        income_giver = Ally(
            cost=3,
            name="Income Giver",
            attack=2,
            health=2,
            effect=GainIncomeEffect(
                amount=[2],
                timing=TimingWindow.ON_PLAY,
                text="When played, gain 2 income"
            )
        )
        
        # Create paired players with initial states
        test_player1, expected_player1 = self.create_player(
            hero_health=200,
            gold=10,
            income=1,  # Starting with some income
            hand=[income_giver]
        )
        
        test_player2, expected_player2 = self.create_player(
            hero_health=200,
            income=1  # Other player's income shouldn't change
        )
        
        # Set up game state
        self.game_state.player1 = test_player1
        self.game_state.player2 = test_player2
        self.game_state.current_player, self.game_state.opponent_player = test_player1, test_player2
        
        # Play the card
        GameLogic.process_turn(self.game_state, {
            "type": "play_card",
            "card_index": 0
        })
        
        # Set expected end states
        expected_player1._gold = 7  # 10 - 3 (cost)
        expected_player1._income = 3  # 1 + 2 (effect)
        expected_player1._hand = []  # Card was played
        expected_player1._army._army = [income_giver]  # Card is now on board
        
        self.assert_gamestate(
            expected_player1=expected_player1,
            expected_player2=expected_player2,
            message="After income gain effect"
        )

    def test_combined_resource_effects(self):
        """Test that income and gold effects can work together"""
        self.setUp()
        
        # Create a card that gives both gold and income
        resource_giver = Ally(
            cost=4,
            name="Resource Giver",
            attack=2,
            health=2,
            effect=GainGoldEffect(  # Could make a combined effect class if this is common
                amount=[3],
                timing=TimingWindow.ON_PLAY,
                text="When played, gain 3 gold"
            )
        )
        
        income_giver = Ally(
            cost=3,
            name="Income Giver",
            attack=1,
            health=1,
            effect=GainIncomeEffect(
                amount=[2],
                timing=TimingWindow.ON_PLAY,
                text="When played, gain 2 income"
            )
        )
        
        # Create paired players with initial states
        test_player1, expected_player1 = self.create_player(
            hero_health=200,
            gold=10,
            income=1,
            hand=[resource_giver, income_giver]
        )
        
        test_player2, expected_player2 = self.create_player(
            hero_health=200
        )
        
        # Set up game state
        self.game_state.player1 = test_player1
        self.game_state.player2 = test_player2
        self.game_state.current_player, self.game_state.opponent_player = test_player1, test_player2
        
        # Play both cards
        GameLogic.process_turn(self.game_state, {
            "type": "play_card",
            "card_index": 0  # Play resource_giver first
        })
        
        GameLogic.process_turn(self.game_state, {
            "type": "play_card",
            "card_index": 0  # Play income_giver second
        })
        
        # Set expected end states
        expected_player1._gold = 6  # 10 - 4 - 3 + 3
        expected_player1._income = 3  # 1 + 2
        expected_player1._hand = []  # Both cards were played
        expected_player1._army._army = [resource_giver, income_giver]  # Both cards on board
        
        self.assert_gamestate(
            expected_player1=expected_player1,
            expected_player2=expected_player2,
            message="After both resource effects"
        )
