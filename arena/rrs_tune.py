import random, time, json
from sklearn.model_selection import ParameterSampler
from scipy.stats import uniform
from math import sqrt
from .arena_simulation import Arena
from calebstone_engine.config import ArenaConfig, PlayerConfig, GameConfig
from calebstone_engine.controllers.heuristic_controllers import HeuristicControllerB

# ---- sampling space ----
RANGES = {
    "w_face":        (0.0, 5.0),
    "doom_face_mult":(0.0, 5.0),
    "w_rm_enemy_atk":(0.0, 5.0),
    "w_lose_own_atk":(0.0, 5.0),
    "w_eff":         (0.0, 5.0),
    "w_overkill":    (0.0, 5.0),
    "survive_bonus": (0.0, 5.0),
}

# ---- tuning constants ----
BASE_SEED = 12345
SAMPLES = 1000
KEEP1 = 100
KEEP2 = 20
G1 = 200      # games_per_pair stage 1
G2 = 400     # games_per_pair stage 2
G3 = 1000    # games_per_pair stage 3
OBJECTIVE = "mean"  # "mean" or "min"
OUT_PATH = "tune_results.jsonl"
ROUND_DECIMALS = 3

with open('calebstone_league/exports/elite_bundle.json', 'r') as file:
    data = json.load(file)

elite_decks = [ (name, deck) for name, deck in data.items() ]
decks = []#[('standard', 'standard')]
decks.extend(elite_decks)
deck = decks[0][1]

# ---- opponents to optimize against ----
OPPONENTS = [
    {
        "id": "Heuristic Best",
        "controller": "heuristicb:w_face=0.033,doom_face_mult=7.905,w_rm_enemy_atk=4.564,w_lose_own_atk=4.808,w_eff=1.221,w_overkill=8.365,survive_bonus=6.94",
    },
    #{"id": "Heuristic A", "controller": "heuristica"},
    #{"id": "Random", "controller": "random"},
]

def get_pair(pairs, a, b):
    return pairs.get((a,b)) or pairs.get((b,a))

def eval_candidate(params, games_per_pair, base_seed, experiment_tag, objective):
    CAND_ID = "Heuristic Tune"

    # Build players: candidate + opponents
    players = [
        PlayerConfig(player_id=CAND_ID, controller=HeuristicControllerB.heurb_spec(params), hero="Caleb", deck=deck),
    ]
    for opp in OPPONENTS:
        players.append(PlayerConfig(player_id=opp["id"], controller=opp["controller"], hero="Caleb", deck=deck))

    spec = ArenaConfig(
        experiment_id=f"{experiment_tag}-{int(time.time())}",
        game_config=GameConfig(deck_start_size=40),
        players=players,
        games_per_pair=games_per_pair,
        mirror_first_player=True,
        base_seed=base_seed,
        log_file=None,
    )
    logger = Arena().run(spec)
    pairs = logger._pairs

    # Win rates for candidate vs each opponent
    wrs = {}
    for opp in OPPONENTS:
        p = get_pair(pairs, CAND_ID, opp["id"])  # handles either ordering
        wins = p["wins"][CAND_ID] if CAND_ID in p['wins'] else 0
        games = p["games"]
        wrs[opp["id"]] = wins / games

    # Aggregate score across opponents
    scores = list(wrs.values())
    if objective == "min":
        score = min(scores) if scores else 0.0
    else:  # mean
        score = sum(scores) / len(scores) if scores else 0.0

    return {
        "score": score,
        "wrs": wrs,
        "games_per_pair": games_per_pair,
        "params": params,
    }

def main():
    random.seed(BASE_SEED)
    all_results = []

    # ---- Stage 1: draw random candidates with scikit-learn ----
    # Convert (low, high) to scipy.stats.uniform(loc=low, scale=high-low)
    param_dists = {k: uniform(loc=rng[0], scale=(rng[1] - rng[0])) for k, rng in RANGES.items()}
    sampler = ParameterSampler(param_distributions=param_dists,
                               n_iter=SAMPLES,
                               random_state=BASE_SEED)
    cands = list(sampler)
    # Round to fixed decimals for stable logging
    cands = [{k: (round(v, ROUND_DECIMALS) if isinstance(v, float) else v) for k, v in cand.items()} for cand in cands]

    stage1 = []
    for i, c in enumerate(cands, 1):
        r = eval_candidate(c, G1, BASE_SEED + i, "tune-s1", OBJECTIVE)
        stage1.append(r)
        all_results.append({"stage": 1, **r})
        print(f"[S1 {i}/{len(cands)}] score={r['score']:.3f} params={r['params']} wrs={r['wrs']}")
    stage1.sort(key=lambda x: x["score"], reverse=True)
    cands = [r["params"] for r in stage1[:KEEP1]]

    # ---- Stage 2 ----
    stage2 = []
    for i, c in enumerate(cands, 1):
        r = eval_candidate(c, G2, BASE_SEED + 1000 + i, "tune-s2", OBJECTIVE)
        stage2.append(r)
        all_results.append({"stage": 2, **r})
        print(f"[S2 {i}/{len(cands)}] score={r['score']:.3f} params={r['params']} wrs={r['wrs']}")
    stage2.sort(key=lambda x: x["score"], reverse=True)
    cands = [r["params"] for r in stage2[:KEEP2]]

    # ---- Stage 3 (final) ----
    best = None
    for i, c in enumerate(cands, 1):
        r = eval_candidate(c, G3, BASE_SEED + 2000 + i, "tune-s3", OBJECTIVE)
        all_results.append({"stage": 3, **r})
        print(f"[S3 {i}/{len(cands)}] score={r['score']:.3f} params={r['params']} wrs={r['wrs']}")
        best = r if (best is None or r["score"] > best["score"]) else best

    # Persist results
    with open(OUT_PATH, "w") as f:
        for r in all_results:
            f.write(json.dumps(r) + "\n")

    print("\n=== BEST ===")
    print(best)
    print("Use with:", HeuristicControllerB.heurb_spec(best["params"]))

if __name__ == "__main__":
    main()