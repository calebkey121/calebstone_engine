from abc import ABC, abstractmethod
import random

class Controller(ABC):
    @abstractmethod
    def get_action(self, game_state):
        pass

class RandomController(Controller):
    def get_action(self, game_state):
        possible_actions = game_state.possible_actions()
        return random.choice(possible_actions)

class WebController(Controller):
    def __init__(self):
        self.pending_action = None

    def get_action(self, game_state):
        action = self.pending_action
        self.pending_action = None  # Clear after use
        return action
    
    def set_action(self, action):
        self.pending_action = action

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
