from game_engine.effects import *
from tests.TestFramework import GameTestCase
from tests.TestScenario import *
from game_engine.Ally import Ally

class TemplateTest(GameTestCase):
    def test_template(self):
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
        draw_2 = DrawCardsEffect(
            amount=[2],
            timing=TimingWindow.ON_PLAY,
            text="When played, draw 2 cards"
        )
        deal_2_all_enemies = DamageAllEnemiesEffect(
            amount=[2],
            timing=TimingWindow.ON_PLAY,
            text="When played, deal 2 damage to all enemies"
        )
        deal_4_enemy_hero = DamageEnemyHeroEffect(
            amount=[4],
            timing=TimingWindow.ON_DEATH,
            text="When this dies, deal 4 damage to enemy hero"
        )
        heal_3_all_allies = HealAllAlliesEffect(
            amount=[3],
            timing=TimingWindow.ON_PLAY,
            text="When played, heal all allies for 3"
        )

        # Create deck cards to test drawing
        # deck_cards = [
        #     Ally(name="Deck Card 1", cost=1, attack=1, health=1),
        #     Ally(name="Deck Card 2", cost=2, attack=2, health=2),
        #     Ally(name="Deck Card 3", cost=3, attack=3, health=3),
        #     Ally(name="Deck Card 4", cost=4, attack=4, health=4)
        # ]

        # Define initial player states
        player1 = PlayerScenario(
            player_name="Test Player 1",
            hero_name="Test Hero 1",
            hero_health=200,
            gold=10,
            income=2,
            # Start with a mix of utility cards
            hand = [
                Ally(name="Hand1 1", cost=1, attack=1, health=1, effect=draw_2),
                Ally(name="Hand1 2", cost=2, attack=2, health=2, effect=deal_2_all_enemies),
            ],
            # Start with some board presence
            board = [
                Ally(name="Board1 1", cost=5, attack=6, health=4, effect=deal_4_enemy_hero),
                Ally(name="Board1 2", cost=3, attack=2, health=5, effect=heal_3_all_allies),
            ],
            # Deck for drawing
            deck_list = [
                Ally(name="Deck1 1", cost=1, attack=1, health=1),
                Ally(name="Deck1 2", cost=2, attack=2, health=2),
                Ally(name="Deck1 3", cost=3, attack=3, health=3),
            ].copy(),
            # Expected end state after all actions
            expected_final_state={
                'hero_health': 200,  # Takes some combat damage
                'gold': 9,  # Initial 10 + 2 (income) - 1 (play) - 2 (play)
                'income': 2,
                # 'hand': [  # since deck is shuffled we don't know, can fix later
                #     # Cards drawn during turn
                #     {'name': "Deck Card 1", 'attack': 1, 'health': 1, 'cost': 1},
                #     {'name': "Deck Card 2", 'attack': 2, 'health': 2, 'cost': 2},
                #     {'name': "Deck Card 3", 'attack': 3, 'health': 3, 'cost': 3}
                # ],
                'board': [
                    # Survived units with updated stats
                    {'name': "Board1 2", 'attack': 2, 'health': 2, 'ready': False},
                    # Newly played units
                    {'name': "Hand1 1", 'attack': 1, 'health': 1, 'ready': False},
                    {'name': "Hand1 2", 'attack': 2, 'health': 2, 'ready': False}
                ]
            }
        )

        player2 = PlayerScenario(
            player_name="Test Player 2",
            hero_name="Test Hero 2",
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
                Ally(name="Board2 1", cost=5, attack=4, health=8),
                Ally(name="Board2 2", cost=3, attack=3, health=4)
            ],
            # Use different deck cards
            deck_list=[
                Ally(name="Deck2 1", cost=1, attack=1, health=1),
                Ally(name="Deck2 2", cost=2, attack=2, health=2)
            ],
            expected_final_state={
                'hero_health': 198,  # takes 2 from on play
                'gold': 8,  # Initial + income - costs
                'income': 3,
                # 'hand': [ # since deck is shuffled we don't know, can fix later
                #     {'name': "Guardian", 'attack': 4, 'health': 7, 'cost': 4},
                #     {'name': "Deck2 1", 'attack': 1, 'health': 1, 'cost': 1} # since deck is shuffled we don't know, can fix later
                # ],
                'board': [
                    {'name': "Hand2 1", 'attack': 3, 'health': 6, 'ready': False}
                ]
            }
        )

        # Complex sequence of turns and actions, always have end turn be the last one, and start_turn triggers each turn
        actions = [
            # Turn 1 (Player 1)
            [
                {"type": "play_card", "card_index": 0},  # Play first card, draw 2
                {"type": "play_card", "card_index": 0},  # Play second card, deals 2 to all enemies : 4/8, 3/4 -> 4/6, 3/2 | hand1 = [Deck Card 1, Deck Card 2]
                # Attack with board
                {"type": "attack", "attacker_index": 1, "target_index": 1},  # 6/4 attacks 4/6 -> both die
                {"type": "attack", "attacker_index": 1, "target_index": 1},  # 2/5 attacks 3/2 -> board1 = [2/2], board2=[]
                {"type": "end_turn"}
            ],
            # Turn 2 (Player 2)
            [
                # Develop board
                {"type": "play_card", "card_index": 0},  # board2 = [4/6], gold: 8(start) + 3(income) - 3(play) = 9
                # Counter-attack
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
