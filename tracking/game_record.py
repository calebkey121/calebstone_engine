# calebstone_engine/tracking/game_record.py
from dataclasses import dataclass, asdict
from typing import Optional
import json

@dataclass
class GameRecord:
    winner: str                  # "p1" | "p2" | "draw"
    first_player: str            # "p1" | "p2"
    turns: int
    rounds: int
    winning_hero_health: int
    p1_id: str
    p2_id: str
    seed: Optional[int] = None
    # Add later as needed: life_diff, ruleset_id, controller_ids, etc.

class GameRecordEmitter:
    def __init__(self, log_file: Optional[str] = None):
        self._log_file = log_file
        self._first_player = None

    def start_game(self, game_state) -> None:
        self._first_player = "p1" if game_state.who_went_first == game_state.p1 else "p2"

    def end_game(self, game_state, p1_id: str, p2_id: str, seed: Optional[int] = None) -> GameRecord:
        if game_state.p1.is_dead() and game_state.p2.is_dead():
            winner, hp = "draw", 0
        elif game_state.p1.is_dead():
            winner, hp = "p2", game_state.p2.hero.health
        else:
            winner, hp = "p1", game_state.p1.hero.health

        rec = GameRecord(
            winner=winner,
            first_player=self._first_player or "p1",
            turns=game_state.total_turns,
            rounds=game_state.current_round,
            winning_hero_health=hp,
            p1_id=p1_id,
            p2_id=p2_id,
            seed=seed,
        )

        if self._log_file:
            with open(self._log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(rec), separators=(",", ":")) + "\n")
        return rec
