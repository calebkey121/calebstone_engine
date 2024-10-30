from game_engine.effects import *
from tests.TestFramework import *
from game_engine.GameLogic import GameLogic

class CombatTest(GameTestCase):
    def test_attack_scenarios(self):
        """Test various attack scenarios:
        1. Ally attacks enemy hero
        2. Ally attacks enemy ally (both survive)
        3. Ally attacks and kills enemy ally
        4. Ally attacks and dies to enemy ally
        """
        self.setUp()
        
        # Create attackers with different stats
        hero_attacker = Ally(
            name="Hero Attacker",
            cost=2,
            attack=5,
            health=5
        )
        
        surviving_attacker = Ally(
            name="Surviving Attacker",
            cost=2,
            attack=2,
            health=4
        )
        
        killing_attacker = Ally(
            name="Killing Attacker",
            cost=3,
            attack=6,
            health=6
        )
        
        dying_attacker = Ally(
            name="Dying Attacker",
            cost=1,
            attack=2,
            health=2
        )
        
        # Create defenders
        surviving_defender = Ally(
            name="Surviving Defender",
            cost=2,
            attack=1,
            health=5
        )
        
        dying_defender = Ally(
            name="Dying Defender",
            cost=2,
            attack=2,
            health=4
        )
        
        strong_defender = Ally(
            name="Strong Defender",
            cost=4,
            attack=4,
            health=8
        )
        
        # Set up players with all attackers/defenders
        test_player1, expected_player1 = self.create_player(
            hero_health=200,
            gold=10,
            board=[hero_attacker, surviving_attacker, killing_attacker, dying_attacker]
        )
        
        test_player2, expected_player2 = self.create_player(
            hero_health=200,
            gold=10,
            board=[surviving_defender, dying_defender, strong_defender]
        )
        
        # Set up game state
        self.game_state.player1 = test_player1
        self.game_state.player2 = test_player2
        self.game_state.current_player, self.game_state.opponent_player = test_player1, test_player2
        
        # 1. Attack enemy hero
        GameLogic.process_turn(self.game_state, {
            "type": "attack",
            "attacker_index": 1,  # hero_attacker
            "target_index": 0     # enemy hero
        })
        
        # 2. Attack with surviving attacker vs surviving defender
        GameLogic.process_turn(self.game_state, {
            "type": "attack",
            "attacker_index": 2,  # surviving_attacker
            "target_index": 1     # surviving_defender
        })
        
        # 3. Attack and kill defender
        GameLogic.process_turn(self.game_state, {
            "type": "attack",
            "attacker_index": 3,  # killing_attacker
            "target_index": 2     # dying_defender
        })
        
        # 4. Attack and die to strong defender
        GameLogic.process_turn(self.game_state, {
            "type": "attack",
            "attacker_index": 4,  # dying_attacker
            "target_index": 2     # strong_defender
        })
        
        # Set up expected end state
        # First create survivors with updated health
        hero_attacker.ready_down()  # Used for attack
        surviving_attacker.health = 3  # Took 1 damage
        surviving_attacker.ready_down()
        killing_attacker.health = 4  # Took 2 damage
        killing_attacker.ready_down()
        # dying_attacker died
        
        surviving_defender.health = 3  # Took 2 damage
        # dying_defender died
        strong_defender.health = 6  # Took 2 damage
        
        # Set expected player states
        expected_player1._gold = 10
        expected_player1._army._army = [hero_attacker, surviving_attacker, killing_attacker]
        
        expected_player2._gold = 10
        expected_player2._hero._health = 195  # Took 5 damage from .Hero_attacker
        expected_player2._army._army = [surviving_defender, strong_defender]
        
        # Verify final state
        self.assert_gamestate(
            expected_player1=expected_player1,
            expected_player2=expected_player2,
            message="After all attacks"
        )
