from abc import ABC, abstractmethod
import json
import time
from typing import Optional

class OutputHandler(ABC):
    @abstractmethod
    def display_action(self, action, game_state):
        pass

    @abstractmethod
    def display_state(self, game_state):
        pass

class TerminalOutputHandler(OutputHandler):
    def display_action(self, action, game_state):
        current_player = game_state.current_player
        if action['type'] == 'play_card':
            card = current_player._hand[action['card_index']]
            print(f"{current_player._name} played {card._name}")
        elif action['type'] == 'attack':
            attacker = current_player.all_characters()[action['attacker_index']]
            target = game_state.opponent_player.all_characters()[action['target_index']]
            print(f"{current_player._name}'s {attacker._name} attacked {target._name}")
    
    def display_state(self, game_state):
        # Get Player 1's status
        player1_hero_status = game_state.p1.get_hero_status()
        player1_army_status = game_state.p1.get_army_status()
        player1_hand_status = game_state.p1.get_hand_status()

        # Get Player 2's status
        player2_hero_status = game_state.p2.get_hero_status()
        player2_army_status = game_state.p2.get_army_status()
        player2_hand_status = game_state.p2.get_hand_status()

        # Display Player 1's Status
        print("\nPlayer 1:")
        print(f"\tGold: {game_state.p1.gold} | Income: {game_state.p1.income}")

        print("Hero:")
        print(f"\tHero: {player1_hero_status['name']} | Attack: {player1_hero_status['attack']} | Health: {player1_hero_status['health']}")
        
        print("Army:")
        if player1_army_status:
            for i, ally in enumerate(player1_army_status):
                print(f"\tAlly {i+1}: {ally['name']} | Attack: {ally['attack']} | Health: {ally['health']} | Cost: {ally['cost']}")
        else:
            print("No allies on the field.")

        print("\tHand:")
        if player1_hand_status:
            for i, card in enumerate(player1_hand_status):
                print(f"\tCard {i+1}: {card['name']} | Attack: {card['attack']} | Health: {card['health']} | Cost: {card['cost']}")
        else:
            print("\tNo cards in hand.")

        # Display Player 2's Status
        print("\nPlayer 2:")
        print(f"\tGold: {game_state.p2.gold} | Income: {game_state.p2.income}")

        print("Hero:")
        print(f"\tHero: {player2_hero_status['name']} | Attack: {player2_hero_status['attack']} | Health: {player2_hero_status['health']}")
        
        print("Army:")
        if player2_army_status:
            for i, ally in enumerate(player2_army_status):
                print(f"\tAlly {i+1}: {ally['name']} | Attack: {ally['attack']} | Health: {ally['health']} | Cost: {ally['cost']}")
        else:
            print("\tNo allies on the field.")

        print("Hand:")
        if player2_hand_status:
            for i, card in enumerate(player2_hand_status):
                print(f"\tCard {i+1}: {card['name']} | Attack: {card['attack']} | Health: {card['health']} | Cost: {card['cost']}")
        else:
            print("\tNo cards in hand.")

class ActionHistoryFileHandler(OutputHandler):
    """Human-readable, concise action history written to a text file.
    Each call writes one line so you can tail the file while the game runs.
    """
    def __init__(self, path: str):
        self.path = path

    def display_action(self, action, game_state):
        p = game_state.current_player
        line = None
        if action['type'] == 'play_card':
            card = p._hand[action['card_index']]
            line = f"{p._name} played {card._name} (cost {card._cost})"
        elif action['type'] == 'attack':
            attacker = p.all_characters()[action['attacker_index']]
            target = game_state.opponent_player.all_characters()[action['target_index']]
            line = f"{p._name}'s {attacker._name} attacked {target._name} ({attacker.attack_value}/{attacker.health} -> {target.attack_value}/{target.health})"
        elif action['type'] == 'end_turn':
            line = f"{p._name} ended their turn"

        if line:
            with open(self.path, 'a', encoding='utf-8') as f:
                f.write(line + "\n")

    def display_state(self, game_state):
        # Optional: write a compact summary of the full state (call at turn boundaries)
        p1 = game_state.p1
        p2 = game_state.p2
        summary = (
            f"Round {game_state.current_round}, Turn {game_state.total_turns}: "
            f"P1 {p1._name} HP {p1.hero.health} Gold {p1.gold}/{p1.income} | "
            f"P2 {p2._name} HP {p2.hero.health} Gold {p2.gold}/{p2.income}\n"
        )
        with open(self.path, 'a', encoding='utf-8') as f:
            f.write(summary)


class JSONLGameLogHandler(OutputHandler):
    """Machine-readable JSON Lines (one JSON object per action).
    Keep payloads compact; consumers can reconstruct details if needed.
    """
    def __init__(self, path: str):
        self.path = path
        # write a header line to help with tooling (optional)
        with open(self.path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"type": "log_session", "ts": self._ts(), "version": 1}) + "\n")

    def _ts(self):
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def _write(self, obj: dict):
        with open(self.path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(obj, separators=(',', ':')) + "\n")

    def display_action(self, action, game_state):
        p = game_state.current_player
        evt = {"type": action['type'], "actor": getattr(p, '_name', 'unknown'), "ts": self._ts()}

        if action['type'] == 'play_card':
            card = p._hand[action['card_index']]
            evt.update({
                "card": getattr(card, '_name', None),
                "cost": getattr(card, '_cost', None),
                "hand_size": len(p._hand)
            })
        elif action['type'] == 'attack':
            att_idx = action['attacker_index']
            tgt_idx = action['target_index']
            attacker = p.all_characters()[att_idx]
            target = game_state.opponent_player.all_characters()[tgt_idx]
            evt.update({
                "attacker": getattr(attacker, '_name', None),
                "target": getattr(target, '_name', None),
                "attacker_stats": {"atk": attacker.attack_value, "hp": attacker.health},
                "target_stats": {"atk": target.attack_value, "hp": target.health}
            })
        elif action['type'] == 'end_turn':
            pass

        # Minimal post-state summary for debugging
        evt.update({
            "round": game_state.current_round,
            "turn": game_state.total_turns,
            "p1_hp": game_state.p1.hero.health,
            "p2_hp": game_state.p2.hero.health,
            "p1_gold": game_state.p1.gold,
            "p2_gold": game_state.p2.gold,
        })

        self._write(evt)

    def display_state(self, game_state):
        # Optional: record a periodic snapshot marker (e.g., on turn boundaries)
        self._write({
            "type": "state_marker",
            "ts": self._ts(),
            "round": game_state.current_round,
            "turn": game_state.total_turns,
            "p1": {
                "name": getattr(game_state.p1, '_name', 'p1'),
                "hp": game_state.p1.hero.health,
                "gold": game_state.p1.gold,
                "income": game_state.p1.income,
            },
            "p2": {
                "name": getattr(game_state.p2, '_name', 'p2'),
                "hp": game_state.p2.hero.health,
                "gold": game_state.p2.gold,
                "income": game_state.p2.income,
            },
        })

class NoOutputHandler(OutputHandler):
    def display_action(self, action, game_state):
        pass  # Do nothing
    
    def display_state(self, game_state):
        pass  # Do nothing
