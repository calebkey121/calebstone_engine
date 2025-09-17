from abc import ABC, abstractmethod
from random import choice
from itertools import combinations

class Controller(ABC):
    @abstractmethod
    def get_action(self, game_state):
        """Abstract method to get an action for the current turn."""
        pass

    @staticmethod
    def create_controller(controller_type):
        controller_type = controller_type.lower()
        if controller_type in [ "human" ]:
            return HumanController()
        elif controller_type in [ "random", "rand", "r" ]:
            return RandomController()
        elif controller_type in [ "heuristica", "heura", "ha" ]:
            return HeuristicControllerA()
        elif controller_type in [ "heuristicb", "heurb", "hb" ]:
            return HeuristicControllerB()
        else:
            raise ValueError(f"Unknown controller type: {controller_type}")

class HumanController(Controller):
    def __init__(self):
        self.type = "Human"
        self.pending_action = None

    def set_action(self, action):
        self.pending_action = action

    def get_action(self, game_state):
        action = self.pending_action
        self.pending_action = None  # Reset after use
        return action

class RandomController(Controller):
    def __init__(self):
        self.type = "Random"

    def get_action(self, game_state):
        possible_actions = game_state.possible_actions()
        return choice(possible_actions)

class HeuristicControllerA(Controller):
    def __init__(self):
        self.type = "AI"
    
    def get_action(self, game_state):
        possible_actions = game_state.possible_actions()

        # 1. Play the cheapest playable card
        play_cards = [a for a in possible_actions if a["type"] == "play_card"]
        if play_cards:
            return min(play_cards, key=lambda x: game_state.current_player._hand[x["card_index"]].cost)

        # 2. Attack with highest attack ally
        attack_actions = [a for a in possible_actions if a["type"] == "attack"]
        if attack_actions:
            # Prefer attacker with highest attack
            def attacker_strength(action):
                attacker = game_state.current_player.all_characters()[action["attacker_index"]]
                return -attacker.attack_value  # negative for max()

            return min(attack_actions, key=attacker_strength)
        
        return choice(possible_actions)

class HeuristicControllerB(Controller):
    def __init__(self):
        self.type = "AI"
        # --- Action scoring ---
        # Tunable weights
        self.W_FACE = 5.0             # value of direct hero damage
        self.W_RM_ENEMY_ATK = 12.0     # value of removing enemy attack power
        self.W_LOSE_OWN_ATK = 6.0      # penalty for losing our attack power
        self.W_EFF = 2.0               # damage efficiency (deal vs take)
        self.W_OVERKILL = 0.15         # penalty for overkill when trading
        self.SURVIVE_BONUS = 3.0       # bonus: kill and live
        self.DOOM_FACE_MULT = 2.5      # if attacker likely dies next turn, face damage is worth more
    
    def get_action(self, game_state):
        possible_actions = game_state.possible_actions()

        # 1. Use the most gold in one turn
        play_cards = [a for a in possible_actions if a["type"] == "play_card"]
        if play_cards:
            total_gold = game_state.current_player.gold
            card_costs = [ game_state.current_player._hand[x["card_index"]].cost for x in play_cards]
            
            # if the total costs of hand is less than the gold you have, just play all cards
            if sum(card_costs) <= total_gold:
                return play_cards[0]

            # find the best combinations of cards to play
            best = None
            for k in range(1, len(card_costs) + 1):
                for combo in combinations(card_costs, k):
                    s = sum(combo)
                    if s > total_gold:
                        continue
                    if best is None:
                        best = combo
                    else:
                        diff = abs(sum(best) - total_gold)
                        new_diff = abs(sum(combo) - total_gold)
                        if new_diff < diff:
                            best = combo
            return play_cards[card_costs.index(best[0])]

        # 2. Win game if possible, else choose the highest-EV attack
        attack_actions = [a for a in possible_actions if a["type"] == "attack"]
        if attack_actions:
            player_chars = game_state.current_player.all_characters()
            opponent_chars = game_state.opponent_player.all_characters()

            # --- Lethal using only face attacks ---
            hero_actions = [a for a in attack_actions if a["target_index"] == 0]
            if hero_actions:
                hero_attackers = {a["attacker_index"] for a in hero_actions}
                total_face = sum(player_chars[i].attack_value for i in hero_attackers)
                enemy_hero = opponent_chars[0]
                if total_face >= enemy_hero.health:
                    # Use the biggest hitter first
                    return max(hero_actions, key=lambda x: player_chars[x["attacker_index"]].attack_value)

            # Pre-compute opponent threat next turn (rough): max enemy unit attack
            enemy_unit_attacks = [c.attack_value for c in opponent_chars[1:] if c.health > 0]
            max_enemy_attack_next = max(enemy_unit_attacks) if enemy_unit_attacks else 0

            def score_action(act):
                a = player_chars[act["attacker_index"]]
                t = opponent_chars[act["target_index"]]

                # Damage taken this action
                dmg_taken_now = 0
                attacker_dies_now = False
                defender_dies = False

                if act["target_index"] != 0:
                    dmg_taken_now = min(t.attack_value, a.health)
                    attacker_dies_now = t.attack_value >= a.health
                    defender_dies = a.attack_value >= t.health
                else:
                    defender_dies = False  # attacking face doesn't kill a unit now

                # Remaining HP after this action
                a_hp_after = a.health - dmg_taken_now

                # Rough "doomed next turn" check
                doomed_next = max_enemy_attack_next >= a_hp_after and a_hp_after > 0

                # Components
                face_value = 0.0
                if act["target_index"] == 0:
                    face_value = a.attack_value * (self.DOOM_FACE_MULT if doomed_next else 1.0) * self.W_FACE

                enemy_attack_removed = (t.attack_value if defender_dies and act["target_index"] != 0 else 0.0)
                own_attack_lost = (a.attack_value if attacker_dies_now else 0.0)

                dmg_dealt = a.attack_value if act["target_index"] == 0 else min(a.attack_value, t.health)
                overkill_penalty = (max(0, a.attack_value - t.health) if act["target_index"] != 0 else 0.0)

                value = 0.0
                value += face_value
                value += self.W_RM_ENEMY_ATK * enemy_attack_removed
                value -= self.W_LOSE_OWN_ATK * own_attack_lost
                value += self.W_EFF * (dmg_dealt - 0.5 * dmg_taken_now)
                value -= self.W_OVERKILL * overkill_penalty
                if defender_dies and not attacker_dies_now and act["target_index"] != 0:
                    value += self.SURVIVE_BONUS

                return value

            return max(attack_actions, key=score_action)
        
        return choice(possible_actions)
