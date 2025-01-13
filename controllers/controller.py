from abc import ABC, abstractmethod
from random import choice

class Controller(ABC):
    @abstractmethod
    def get_action(self, game_state):
        """Abstract method to get an action for the current turn."""
        pass

    @staticmethod
    def create_controller(controller_type):
        controller_type = controller_type.lower()
        if controller_type in [ "human", "h" ]:
            return HumanController()
        elif controller_type in [ "random", "rand", "r" ]:
            return RandomController()
        elif controller_type in [ "ai", "cpu" ]:
            return AIController()  # Placeholder for future AI controller
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

class AIController(Controller):
    def __init__(self):
        self.type = "AI"
    
    def get_action(self, game_state):
        possible_actions = game_state.possible_actions()
        return choice(possible_actions)
