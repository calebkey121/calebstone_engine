from .arena_simulation import Arena
from calebstone_engine.config import ArenaConfig, PlayerConfig, GameConfig
from pprint import pprint
from calebstone_engine.tracking.plotting import plot_rr_graphs

players = [
    PlayerConfig(player_id=f"early", controller="heuristicb:w_face=0.017,doom_face_mult=3.953,w_rm_enemy_atk=2.282,w_lose_own_atk=2.404,w_eff=0.611,w_overkill=4.182,survive_bonus=3.47", hero="Caleb", deck="early"),
    PlayerConfig(player_id=f"late", controller="heuristicb:w_face=0.017,doom_face_mult=3.953,w_rm_enemy_atk=2.282,w_lose_own_atk=2.404,w_eff=0.611,w_overkill=4.182,survive_bonus=3.47", hero="Caleb", deck="late"),
    #PlayerConfig(
    #    player_id=f"Heuristic Best2",
    #    controller="heuristicb:w_face=0.033,doom_face_mult=7.905,w_rm_enemy_atk=4.564,w_lose_own_atk=4.808,w_eff=1.221,w_overkill=8.365,survive_bonus=6.94",
    #    hero="Caleb", deck="standard",
    #),
    #PlayerConfig(
    #    player_id=f"Heuristic Best1",
    #    controller="heuristicb:w_face=0.017,doom_face_mult=3.953,w_rm_enemy_atk=2.282,w_lose_own_atk=2.404,w_eff=0.611,w_overkill=4.182,survive_bonus=3.47",
    #    hero="Caleb", deck="standard",
    #),
    #PlayerConfig(
    #    player_id=f"CalebRL",
    #    controller="rlinference",
    #    hero="Caleb", deck="standard",
    #),

]

spec = ArenaConfig(
    experiment_id="rr-2025-09-16-a",
    game_config=GameConfig(),
    players=players,
    games_per_pair=1500,
    mirror_first_player=True,
    base_seed=12345,
    log_file="arena_rr_small.jsonl",
)

logger = Arena().run(spec)
plot_rr_graphs(logger)
