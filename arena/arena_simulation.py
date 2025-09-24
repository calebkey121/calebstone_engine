

from tqdm import tqdm
from calebstone_engine.game.game_manager import GameManager
from calebstone_engine.tracking import SimulationRecord
from .scheduler import round_robin_pairs
from ..config.arena_config import ArenaConfig


def seed_for(experiment_id: str, a_id: str, b_id: str, rep: int) -> int:
    # simple deterministic hash; swap ids changes seed
    return abs(hash((experiment_id, a_id, b_id, rep))) & 0xffffffff

class Arena:
    def run(self, spec: ArenaConfig):
        logger = SimulationRecord()
        # Compute total number of games for tqdm progress bar
        pairs = list(round_robin_pairs(spec.players))
        total_pairs = len(pairs)
        per_pair_games = spec.games_per_pair * 2 if spec.mirror_first_player else spec.games_per_pair
        total_games = total_pairs * per_pair_games

        per_dir = per_pair_games // 2 if spec.mirror_first_player else per_pair_games

        with tqdm(total=total_games, desc="Running Round Robin", unit="game") as pbar:
            for a, b in pairs:
                # choose which side gets the extra start if odd
                extra_for_a = (spec.games_per_pair % 2 == 1) and (hash((spec.experiment_id, a.player_id, b.player_id)) % 2 == 0)
                g_a_starts = per_dir + (1 if extra_for_a else 0)
                g_b_starts = per_dir + (0 if extra_for_a else 1) if spec.mirror_first_player else 0

                # A starts
                for rep in range(g_a_starts):
                    seed = seed_for(spec.experiment_id, a.player_id, b.player_id, rep)
                    game = GameManager(game_config=spec.game_config, p1_config=a, p2_config=b, seed=seed)
                    game.run_game()
                    logger.record(game.game_record)
                    pbar.update(1)

                # B starts (mirror)
                if spec.mirror_first_player:
                    for rep in range(g_b_starts):
                        seed = seed_for(spec.experiment_id, b.player_id, a.player_id, rep)
                        game = GameManager(game_config=spec.game_config, p1_config=b, p2_config=a, seed=seed)
                        game.run_game()
                        logger.record(game.game_record)
                        pbar.update(1)

        return logger
    