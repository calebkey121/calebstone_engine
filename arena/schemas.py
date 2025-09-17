from dataclasses import dataclass
from typing import List, Optional
from calebstone_engine.game.player_config import PlayerConfig

@dataclass(frozen=True)
class RoundRobinSpec:
    experiment_id: str
    players: List[PlayerConfig]
    games_per_pair: int = 100 # total across both directions
    mirror_first_player: bool = True
    base_seed: Optional[int] = 12345
    log_file: str = "arena_round_robin.jsonl"