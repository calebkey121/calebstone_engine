from abc import ABC, abstractmethod
from random import choice

# lightweight parser for controller params like "heurb:w_face=8,doom_face_mult=3"
def _parse_controller_params(spec: str):
    if ":" not in spec:
        return spec.lower(), {}
    base, params_str = spec.split(":", 1)
    base = base.lower()
    params = {}
    for kv in params_str.split(","):
        kv = kv.strip()
        if not kv or "=" not in kv:
            continue
        k, v = kv.split("=", 1)
        k = k.strip().lower().replace("-", "_")
        # parse value; keep floats as float, otherwise keep raw string
        try:
            val = float(v)
        except ValueError:
            val = v
        # accept common aliases -> canonical arg names (include 'model' for RL inference)
        alias = {
            "w_face": "w_face",
            "face": "w_face",
            "w_rm_enemy_atk": "w_rm_enemy_atk",
            "rm_enemy": "w_rm_enemy_atk",
            "remove_enemy": "w_rm_enemy_atk",
            "w_lose_own_atk": "w_lose_own_atk",
            "lose_own": "w_lose_own_atk",
            "w_eff": "w_eff",
            "eff": "w_eff",
            "w_overkill": "w_overkill",
            "overkill": "w_overkill",
            "survive_bonus": "survive_bonus",
            "doom_face_mult": "doom_face_mult",
            "doom": "doom_face_mult",
            "model": "model",
        }.get(k)
        if alias:
            params[alias] = val
        else:
            params[k] = val
    return base, params

class Controller(ABC):
    @abstractmethod
    def get_action(self, game_state):
        """Abstract method to get an action for the current turn."""
        pass

    @staticmethod
    def create_controller(controller_type):
        base, params = _parse_controller_params(controller_type)

        if base in ["human"]:
            return HumanController()

        elif base in ["random", "rand", "r"]:
            return RandomController()

        elif base in ["heuristica", "heura", "ha"]:
            from .heuristic_controllers import HeuristicControllerA
            return HeuristicControllerA()

        elif base in ["heuristicb", "heurb", "hb"]:
            from .heuristic_controllers import HeuristicControllerB
            return HeuristicControllerB(**params)
        
        elif base in ["rl"]:
            return ReinforcementLearningController()

        elif base in ["rlinference", "rlinfer", "rli"]:
            model_path = params.get("model", "models/ppo_mask_b1.zip")
            return RLInferenceController(model=str(model_path))
        
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


HAND_SIZE = 10
BOARD_SIZE = 7
OBS_GLOBAL = 3
OBS_CARD = 4
OBS_ALLY = 4
OBS_OPP = 3
OBS_LEN = OBS_GLOBAL + OBS_CARD * HAND_SIZE + OBS_ALLY * BOARD_SIZE + OBS_OPP * BOARD_SIZE
import numpy as np

class ReinforcementLearningController(Controller):
    def __init__(self):
        self.type = "RL"
        self.pending_action = None

    def set_action(self, action):
        self.pending_action = action

    def get_action(self, game_state):
        action = self.pending_action
        self.pending_action = None  # Reset after use
        return action

class RLInferenceController(Controller):
    def __init__(self, model: str = "models/ppo_mask_b1.zip", deterministic: bool = True):
        # Lazy imports to avoid hard dep unless used
        import numpy as np
        from sb3_contrib.ppo_mask import MaskablePPO
        from calebstone_rl.environment import (
            OBS_LEN, HAND_SIZE, ARMY_SIZE, N_ACTIONS,
            # we only rely on the encoding interface; if your env exposes helpers, import them
        )
        self.type = "RL-Infer"
        self._np = np
        self._MaskablePPO = MaskablePPO
        self._model_path = model
        self._det = deterministic
        # load once
        self._model = self._MaskablePPO.load(self._model_path)

    # --- minimal, local encoders mirroring the env (kept here to avoid tight coupling) ---
    @staticmethod
    def _encode_play(hand_idx: int) -> int:
        return hand_idx  # PLAY_OFFSET = 0

    @staticmethod
    def _encode_attack(att_slot: int, tgt_slot: int) -> int:
        return HAND_SIZE + (att_slot - 1) * (BOARD_SIZE + 1) + tgt_slot

    @staticmethod
    def _end_turn_index() -> int:
        return HAND_SIZE + BOARD_SIZE * (BOARD_SIZE + 1)

    def _build_obs(self, gs) -> "np.ndarray":
        obs = self._np.zeros(OBS_LEN, dtype=self._np.float32)
        # globals
        obs[0] = float(gs.current_player.hero.health)
        obs[1] = float(getattr(gs.current_player, 'gold', 0))
        obs[2] = float(gs.opponent_player.hero.health)
        # hand
        hand_n = gs.current_player.num_cards_in_hand()
        o = 3
        for i in range(HAND_SIZE):
            if i < hand_n:
                c = gs.current_player.card_at(i)
                obs[o+0] = 1.0
                obs[o+1] = float(getattr(c,'cost',0))
                obs[o+2] = float(getattr(c,'attack_value', getattr(c,'attack',0)))
                obs[o+3] = float(getattr(c,'health', getattr(c,'hp',0)))
            o += 4
        # my board
        my_allies = list(gs.current_player.all_characters())[1:1+BOARD_SIZE]
        for j in range(BOARD_SIZE):
            if j < len(my_allies):
                u = my_allies[j]
                obs[o+0] = 1.0
                obs[o+1] = float(getattr(u,'attack_value', getattr(u,'attack',0)))
                obs[o+2] = float(getattr(u,'health', getattr(u,'hp',0)))
                ready = getattr(u,'_ready', getattr(u,'ready', False))
                obs[o+3] = 1.0 if bool(ready) else 0.0
            o += 4
        # opp board
        opp_allies = list(gs.opponent_player.all_characters())[1:1+BOARD_SIZE]
        for j in range(BOARD_SIZE):
            if j < len(opp_allies):
                u = opp_allies[j]
                obs[o+0] = 1.0
                obs[o+1] = float(getattr(u,'attack_value', getattr(u,'attack',0)))
                obs[o+2] = float(getattr(u,'health', getattr(u,'hp',0)))
            o += 3
        return obs

    def _build_mask(self, gs) -> "np.ndarray":
        mask = self._np.zeros(self._end_turn_index()+1, dtype=bool)
        # always allow end turn
        mask[self._end_turn_index()] = True
        for a in gs.possible_actions():
            t = a.get('type')
            if t == 'play_card':
                h = a.get('card_index', -1)
                if 0 <= h < HAND_SIZE:
                    mask[self._encode_play(h)] = True
            elif t == 'attack':
                att = a.get('attacker_index', a.get('attacker_index', 0))
                tgt = a.get('target_index',   a.get('target_index', 0))
                if 1 <= att <= BOARD_SIZE and 0 <= tgt <= BOARD_SIZE:
                    idx = self._encode_attack(att, tgt)
                    if 0 <= idx < mask.size:
                        mask[idx] = True
            elif t == 'end_turn':
                mask[self._end_turn_index()] = True
        return mask

    def get_action(self, game_state):
        obs = self._build_obs(game_state)
        mask = self._build_mask(game_state)
        # predict expects 2D obs
        act, _ = self._model.predict(obs, action_masks=mask, deterministic=self._det)
        aid = int(act)
        # map back to engine action dict
        if aid == self._end_turn_index():
            return {"type": "end_turn"}
        if aid < HAND_SIZE:
            return {"type": "play_card", "card_index": aid}
        # attack
        aid -= HAND_SIZE
        att = aid // (BOARD_SIZE + 1) + 1
        tgt = aid % (BOARD_SIZE + 1)
        return {"type": "attack", "attacker_index": att, "target_index": tgt}
