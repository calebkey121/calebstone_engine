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
        try:
            v_parsed = float(v)
        except ValueError:
            continue
        # accept common aliases -> canonical arg names
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
        }.get(k)
        if alias:
            params[alias] = v_parsed
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
