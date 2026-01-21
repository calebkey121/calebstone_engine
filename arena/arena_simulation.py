from tqdm import tqdm
from calebstone_engine.game.game_manager import GameManager
from calebstone_engine.tracking import SimulationRecord
from .scheduler import round_robin_pairs
from calebstone_engine.config import ArenaConfig
import hashlib


def seed_for(experiment_id: str, a_id: str, b_id: str, rep: int, base_seed: int | None = None) -> int:
    """
    Deterministic per-game seed. Uses a stable hash (BLAKE2b-64) so results
    are identical across Python processes. If base_seed is provided (e.g., ArenaConfig.seed),
    it is included so different base seeds produce different game streams.
    """
    if base_seed is None:
        return None
    payload = f"{base_seed}|{experiment_id}|{a_id}|{b_id}|{rep}"
    return int.from_bytes(hashlib.blake2b(payload.encode('utf-8'), digest_size=8).digest(), 'big')

class Arena:
    def run(self, spec: ArenaConfig):
        logger = SimulationRecord()
        base_seed = getattr(spec, "base_seed", None)
        # Compute total number of games for tqdm progress bar
        pairs = list(round_robin_pairs(spec.players))
        total_pairs = len(pairs)
        per_pair_games = spec.games_per_pair * 2 if spec.mirror_first_player else spec.games_per_pair
        total_games = total_pairs * per_pair_games

        per_dir = per_pair_games // 2 if spec.mirror_first_player else per_pair_games

        with tqdm(total=total_games, desc="Running Round Robin", unit="game") as pbar:
            for a, b in pairs:
                # choose which side gets the extra start if odd
                extra_for_a = (
                    spec.games_per_pair % 2 == 1
                    and (
                        int.from_bytes(
                            hashlib.blake2b(
                                f"{'none' if base_seed is None else base_seed}|extra|{spec.experiment_id}|{a.player_id}|{b.player_id}".encode('utf-8'),
                                digest_size=8
                            ).digest(),
                            'big'
                        ) & 1
                    ) == 0
                )
                g_a_starts = per_dir + (1 if extra_for_a else 0)
                g_b_starts = per_dir + (0 if extra_for_a else 1) if spec.mirror_first_player else 0

                # A starts
                for rep in range(g_a_starts):
                    seed = seed_for(spec.experiment_id, a.player_id, b.player_id, rep, base_seed=base_seed)
                    game = GameManager(game_config=spec.game_config, p1_config=a, p2_config=b, seed=seed)
                    game.run_game()
                    logger.record(game.game_record)
                    pbar.update(1)

                # B starts (mirror)
                if spec.mirror_first_player:
                    for rep in range(g_b_starts):
                        seed = seed_for(spec.experiment_id, b.player_id, a.player_id, rep, base_seed=base_seed)
                        game = GameManager(game_config=spec.game_config, p1_config=b, p2_config=a, seed=seed)
                        game.run_game()
                        logger.record(game.game_record)
                        pbar.update(1)

        return logger