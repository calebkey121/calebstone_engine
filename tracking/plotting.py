# calebstone_engine/tools/plotting.py
from typing import Iterable, Mapping, Any, List, Dict, Optional
import math
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

def _wilson_interval(wins: int, n: int, z: float = 1.96) -> (float, float):
    """Wilson score interval for binomial proportion. Returns (low, high) in PERCENT."""
    if n == 0:
        return (0.0, 0.0)
    p = wins / n
    denom = 1 + (z**2)/n
    center = (p + (z**2)/(2*n)) / denom
    half = z * math.sqrt((p*(1-p)/n) + (z**2)/(4*n**2)) / denom
    lo, hi = max(0.0, center - half), min(1.0, center + half)
    return lo*100.0, hi*100.0

def _rows_from_result(result: Mapping[str, Any]) -> List[Dict[str, Any]]:
    players = result.get("extended", {}).get("players", {})
    rows = []
    for pid, d in players.items():
        g = int(d.get("games", 0))
        w = int(d.get("wins", 0))
        if g <= 0:
            continue
        rows.append({
            "player": pid,
            "games": g,
            "wins": w,
            "losses": g - w,
            "win_rate": (w / g) * 100.0,
        })
    rows.sort(key=lambda r: (r["win_rate"], r["wins"], r["games"]), reverse=True)
    return rows

def plot_winrates(
    logger,
    *,
    min_games: int = 1,
    top_n: Optional[int] = None,
    show_values: bool = True,
    error_bars: bool = False,
    ax=None,
) -> None:
    rows = logger.get_winrate_table(min_games=min_games)
    _plot_winrates_core(rows, top_n=top_n, show_values=show_values, error_bars=error_bars, ax=ax)

def plot_winrates_from_result(
    result: Mapping[str, Any],
    *,
    min_games: int = 1,
    top_n: Optional[int] = None,
    show_values: bool = True,
    error_bars: bool = False,
    ax=None,
) -> None:
    rows = _rows_from_result(result)
    rows = [r for r in rows if r["games"] >= min_games]
    _plot_winrates_core(rows, top_n=top_n, show_values=show_values, error_bars=error_bars, ax=ax)

def _plot_winrates_core(
    rows: Iterable[Mapping[str, Any]],
    *,
    top_n: Optional[int],
    show_values: bool,
    error_bars: bool,
    ax=None,
) -> None:
    rows = list(rows)
    if not rows:
        print("No data to plot.")
        return

    if top_n is not None:
        rows = rows[:top_n]

    labels = [r["player"] for r in rows]
    wrs = [r["win_rate"] for r in rows]

    ax = ax or plt.gca()
    bars = ax.bar(labels, wrs)

    if error_bars:
        # compute Wilson intervals
        eb_lo = []
        eb_hi = []
        for r in rows:
            lo, hi = _wilson_interval(r["wins"], r["games"])
            eb_lo.append(r["win_rate"] - lo)
            eb_hi.append(hi - r["win_rate"])
        ax.errorbar(
            range(len(labels)), wrs,
            yerr=[eb_lo, eb_hi],
            fmt="none", capsize=3,
        )

    if show_values:
        for rect, wr in zip(bars, wrs):
            ax.text(
                rect.get_x() + rect.get_width()/2,
                rect.get_height(),
                f"{wr:.1f}%",
                ha="center", va="bottom", fontsize=8, rotation=0,
            )

    ax.set_ylabel("Win rate (%)")
    ax.set_title("Per-player win rates")
    ax.set_ylim(0, 100)
    ax.tick_params(axis="x", rotation=30)
    
def plot_winrate_heatmap(logger, ax=None):
    matrix = logger.get_pairwise_winrate_matrix()
    # Display pairwise winrate heatmap
    players = sorted(matrix.keys())
    df = pd.DataFrame(matrix, index=players, columns=players).fillna(0).T
    ax = ax or plt.gca()
    sns.heatmap(df, ax=ax, annot=True, fmt=".1f", cmap="Blues", cbar=True, cbar_kws={"label": "Win rate (%)"}, vmin=0, vmax=100, square=True, annot_kws={"fontsize": 8})
    ax.set_title("Pairwise Win Rates (%)")
    ax.set_xlabel("Opponent")
    ax.set_ylabel("Player")
    ax.tick_params(axis="x", rotation=45)
    ax.tick_params(axis="y", rotation=0)

def plot_first_player_advantage_heatmap(logger, ax=None):
    """
    Shows for each pair (A, B) what % of games were won by the first player.
    """
    pairs = logger._pairs  # assume access to raw pair data
    all_players = sorted(logger._players.keys())
    matrix = {a: {b: None for b in all_players} for a in all_players}

    for (a, b), data in pairs.items():
        total = data["games"]
        first_wins = data.get("first_wins", 0)
        if total > 0:
            matrix[a][b] = round((first_wins / total) * 100, 1)
            matrix[b][a] = round((first_wins / total) * 100, 1)

    df = pd.DataFrame(matrix, index=all_players, columns=all_players)
    ax = ax or plt.gca()
    sns.heatmap(
        df,
        ax=ax,
        annot=True,
        fmt=".1f",
        cmap="Purples",
        cbar=True,
        cbar_kws={"label": "Win rate (%)"},
        vmin=0,
        vmax=100,
        square=True,
        annot_kws={"fontsize": 8},
    )
    ax.set_title("First-Move Advantage: % of Games Won by Whoever Starts First")
    ax.set_xlabel("Opponent")
    ax.set_ylabel("Player")
    ax.tick_params(axis="x", rotation=45)
    ax.tick_params(axis="y", rotation=0)

def plot_player_first_winrate_heatmap(logger, ax=None):
    """
    For each player A vs B, show the % of games A won when A went first against B.
    Data source: logger._players[A].vs[B]["games_as_first"|"wins_as_first"].
    """
    # Collect players
    all_players = sorted(logger._players.keys())

    # Initialize matrix with NaNs so seaborn leaves missing cells blank
    matrix = {a: {b: np.nan for b in all_players} for a in all_players}

    # Fill from per-player opponent breakdowns
    for a in all_players:
        vs_map = logger._players[a].vs  # dict: opponent_id -> metrics
        for b in all_players:
            if a == b:
                continue
            d = vs_map.get(b)
            if not d:
                continue
            games_as_first = d.get("games_as_first", 0)
            wins_as_first = d.get("wins_as_first", 0)
            if games_as_first > 0:
                matrix[a][b] = round((wins_as_first / games_as_first) * 100, 1)

    df = pd.DataFrame(matrix, index=all_players, columns=all_players).T
    ax = ax or plt.gca()
    sns.heatmap(
        df,
        ax=ax,
        annot=True,
        fmt=".1f",
        cmap="Oranges",
        cbar=True,
        cbar_kws={"label": "Win rate (%)"},
        vmin=0,
        vmax=100,
        square=True,
        annot_kws={"fontsize": 8},
    )
    ax.set_title("A's Win Rate When A Starts First")
    ax.set_xlabel("Opponent (B)")
    ax.set_ylabel("Player Starting First (A)")
    ax.tick_params(axis="x", rotation=45)
    ax.tick_params(axis="y", rotation=0)

def plot_rr_graphs(logger):
    # Arrange as a 2x2 grid to prevent overlap and use constrained layout
    fig, axes = plt.subplots(2, 2, figsize=(20, 16), constrained_layout=True)
    (ax0, ax1), (ax2, ax3) = axes

    plot_winrate_heatmap(logger, ax=ax0)
    plot_winrates(logger, min_games=5, top_n=None, show_values=True, error_bars=False, ax=ax1)
    plot_first_player_advantage_heatmap(logger, ax=ax2)
    plot_player_first_winrate_heatmap(logger, ax=ax3)

    plt.show()