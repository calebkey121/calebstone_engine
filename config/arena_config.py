from dataclasses import dataclass
from typing import List, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from .player_config import PlayerConfig
    from .game_config import GameConfig

@dataclass(frozen=True)
class ArenaConfig:
    experiment_id: str
    game_config: 'GameConfig'
    players: List['PlayerConfig']
    games_per_pair: int = 100 # total across both directions
    mirror_first_player: bool = True
    base_seed: Optional[int] = None
    log_file: str = "arena.jsonl"