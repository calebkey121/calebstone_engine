from game_engine.effects import *
from tests.TestFramework import GameTestCase
from tests.TestScenario import *
from game_engine.Ally import Ally

class SOT_Test(GameTestCase):
    def test_start_of_turn(self):
        """Template test showcasing all major features:
        - Hand management (playing cards, drawing)
        - Deck interactions (drawing, effects)
        - Combat (attacking, defending)
        - Hero interactions
        - Resource management (gold, income)
        - Effect triggers (ON_PLAY, ON_DEATH, END_OF_TURN)
        - Complex multi-turn scenarios
        """
        self.setUp()

        # Create various effects
        gain_3_gold = GainGoldEffect(
            amount=[3],
            timing=TimingWindow.START_OF_TURN,
            text="At start of turn, gain 3 gold"
        )
        gain_4_income = GainIncomeEffect(
            amount=[4],
            timing=TimingWindow.START_OF_TURN,
            text="At start of turn, gain 4 income"
        )

        # Define initial player states
        player1 = PlayerScenario(
            player_name = "Test Player 1",
            hero_health=200,
            gold=10,
            income=2,
            # Start with a mix of utility cards
            hand = [
                Ally(name="Hand1 1", cost=1, attack=1, health=1),
                Ally(name="Hand1 2", cost=2, attack=2, health=2),
            ],
            # Start with some board presence
            board = [
                Ally(name="Board1 1", cost=5, attack=6, health=4),
                Ally(name="Board1 2", cost=3, attack=2, health=5),
            ],
            # Deck for drawing
            deck_list = [
                Ally(name="Deck1 1", cost=1, attack=1, health=1),
                Ally(name="Deck1 2", cost=2, attack=2, health=2),
                Ally(name="Deck1 3", cost=3, attack=3, health=3),
            ].copy(),
            # Expected end state after all actions
            expected_final_state={
                'hero_health': 200,
                'gold': 12,  # Initial 10 + 2 (income)
                'income': 2,
            }
        )

        player2 = PlayerScenario(
            player_name = "Test Player 2",
            hero_health=200,
            gold=8,
            income=3,
            # Start with some hand cards
            hand=[
                Ally(name="Hand2 1", cost=3, attack=3, health=6),
                Ally(name="Hand2 2", cost=4, attack=4, health=7)
            ],
            # Start with board presence
            board=[
                Ally(name="Board2 1", cost=5, attack=4, health=8, effect=gain_4_income),
                Ally(name="Board2 2", cost=3, attack=3, health=4, effect=gain_3_gold)
            ],
            # Use different deck cards
            deck_list=[
                Ally(name="Deck2 1", cost=1, attack=1, health=1),
                Ally(name="Deck2 2", cost=2, attack=2, health=2)
            ],
            expected_final_state={
                'hero_health': 200,  # takes 2 from on play
                'gold': 14,  # Initial (8) + income (3) + start of turn (3) = 14
                'income': 7,# Initial (3) + start of turn (4) = 7
            }
        )

        # Complex sequence of turns and actions, always have end turn be the last one, and start_turn triggers each turn
        actions = [
            # Turn 1 (Player 1)
            [
                {"type": "end_turn"}
            ],
            [ # triggers start of turn
                {"type": "end_turn"}
            ]
        ]

        # Run the scenario
        run_scenario(
            test_case=self,
            player1=player1,
            player2=player2,
            actions=actions,
            message="Template scenario failed"
        )
