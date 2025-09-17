# simulations/arena_rr_small.py
from calebstone_engine.arena.arena_simulation import RoundRobinArena
from calebstone_engine.arena.schemas import RoundRobinSpec
from calebstone_engine.game.player_config import PlayerConfig
from pprint import pprint
from calebstone_engine.tracking.plotting import plot_rr_graphs

N = 4
players = [
    PlayerConfig(player_id=f"Random 1", controller="random", hero="Caleb", deck="standard"),
    PlayerConfig(player_id=f"Random 2", controller="random", hero="Caleb", deck="standard"),
    PlayerConfig(player_id=f"Heuristic ChatGPT1", controller="heuristica", hero="Caleb", deck="standard"),
    PlayerConfig(player_id=f"Heuristic ChatGPT2", controller="heuristica", hero="Caleb", deck="standard"),
    PlayerConfig(player_id=f"Heuristic Mine1", controller="heuristicb", hero="Caleb", deck="standard"),
    PlayerConfig(player_id=f"Heuristic Mine2", controller="heuristicb", hero="Caleb", deck="standard"),
]

spec = RoundRobinSpec(
    experiment_id="rr-2025-09-16-a",
    players=players,
    games_per_pair=200,
    mirror_first_player=True,
    base_seed=12345,
    log_file="arena_rr_small.jsonl",
)

logger = RoundRobinArena().run(spec)
plot_rr_graphs(logger)
