from abc import ABC, abstractmethod
import random
"""
Purpose:
    The controller takes in input from the player or AI and passes that information to the GameManager to process it. This class could also handle AI logic or reinforcement learning input depending on how the game is being played.
Responsibilities:
    Capture player input: Whether from A human or AI, the controller gathers actions (e.g., “play card X,” “attack with ally Y”).
    Pass actions to the GameManager for resolution.
    Can be extended to handle input from different sources (human player, AI agent, or RL agent).
Notes:
    This class should be extensible so that it can handle different types of inputs (e.g., human input, AI input, or input from A reinforcement learning algorithm).
    You can extend it later to handle multiple types of controllers (e.g., a human controller, an AI controller).
"""

class Controller(ABC):
    @abstractmethod
    def get_action(self, game_state):
        pass

class RandomController(Controller):
    def get_action(self, game_state):
        possible_actions = game_state.possible_actions()
        return random.choice(possible_actions)

class TerminalController(Controller):
    def get_action(self, game_state):
        current_player = game_state.current_player

        while (action_type := input(f"Player {current_player._name}'s turn! Choose an action (0: play_card, 1: attack, 2: end_turn): ").strip()):

            if action_type == '0':  # Play card
                possible_cards = game_state.possible_cards_to_play()
                if possible_cards:
                    self._display_options("cards", possible_cards)
                    card_index = self._choose_option(possible_cards)
                    return {'type': 'play_card', 'card_index': card_index}
                else:
                    print("No cards available to play. Try another action.")

            elif action_type == '1':  # Attack
                attackers = current_player.available_attackers()
                if attackers:
                    self._display_options("attackers", attackers)
                    attacker_index = self._choose_option(attackers)

                    targets = game_state.opponent_player.available_targets()
                    if targets:
                        self._display_options("targets", targets)
                        target_index = self._choose_option(targets)
                        return {
                            'type': 'attack',
                            'attacker_index': attacker_index,
                            'target_index': target_index
                        }
                    else:
                        print("No valid targets available. Try another action.")
                else:
                    print("No attackers available. Try another action.")

            elif action_type == '2':  # End turn
                return {'type': 'end_turn'}

            else:
                print("Invalid choice. Please choose 0, 1, or 2.")

    def _display_options(self, option_type, options):
        """Display options with indices for user selection."""
        print(f"Choose {option_type}:")
        for i, option in enumerate(options):
            print(f"{i}: {option}")
        print("Choose an option by entering the corresponding number.")

    def _choose_option(self, options):
        """Get user selection for a list of options."""
        while True:
            try:
                choice = int(input("Enter choice: ").strip())
                if 0 <= choice < len(options):
                    return choice
                else:
                    print(f"Invalid choice. Please select a number between 0 and {len(options) - 1}.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")
