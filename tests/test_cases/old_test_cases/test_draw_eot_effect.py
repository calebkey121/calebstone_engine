from game_engine.effects import *
from tests.TestFramework import *
from game_engine.GameLogic import GameLogic

class DrawEffectsTest(GameTestCase):
    def test_end_turn_draw_effect_with_fatigue(self):
        """Test end turn draw effect with fatigue damage"""
        self.setUp()
        
        # Create a card with end of turn draw effect
        card_drawer = Ally(
            cost=2,
            name="Card Drawer",
            attack=1,
            health=2,
            effect=DrawCardsEffect(
                amount=[2],  # Draw 2 cards at end of turn
                timing=TimingWindow.END_OF_TURN,
                text="At end of turn, draw 2 cards"
            )
        )
        
        # Create a card to be drawn
        deck_card = Ally(
            cost=1,
            name="Deck Card",
            attack=1,
            health=1
        )
        
        # Create player with just one card in deck
        test_player1, expected_player1 = self.create_player(
            hero_health=200,
            gold=5,
            hand=[card_drawer]
        )
        # Add one card to test_player1's deck
        test_player1._deck._deckList = [deck_card]
        test_player1._deck.set_num_cards()
        
        test_player2, expected_player2 = self.create_player(
            hero_health=200
        )
        
        # Setup game state
        self.game_state.player1 = test_player1
        self.game_state.player2 = test_player2
        self.game_state.current_player, self.game_state.opponent_player = test_player1, test_player2
        
        # Play the card drawer
        GameLogic.process_turn(self.game_state, {
            "type": "play_card",
            "card_index": 0
        })
        
        # End turn (this should trigger the draw effect)
        GameLogic.end_turn(self.game_state)
        
        # Set expected end states
        expected_player1._gold = 3  # 5 - 2 (cost)
        expected_player1._income = 1 # gets income at end of turn
        expected_player1._hand = [deck_card]  # Drew the one deck card
        expected_player1._hero._health = 199  # Took 1 fatigue damage
        expected_player1._army._army = [card_drawer]
        expected_player1._deck._deckList = []  # Deck is empty
        expected_player1._deck._fatigueCounter = 1
        
        self.assert_gamestate(
            expected_player1=expected_player1,
            expected_player2=expected_player2,
            message="After end turn draw effect with fatigue"
        )
