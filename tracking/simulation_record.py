from dataclasses import dataclass
from .game_record import GameRecord

@dataclass
class GameStats:
    total_games: int = 0
    total_turns: int = 0
    total_rounds: int = 0
    games_won_by_first: int = 0
    def get_stats(self) -> dict:
        if self.total_games == 0:
            return {"message": "No games played yet"}
        first_win_rate = (self.games_won_by_first / self.total_games * 100)
        return {
            "total_games": self.total_games,
            "average_length": {
                "turns": f"{self.total_turns / self.total_games:.1f}",
                "rounds": f"{self.total_rounds / self.total_games:.1f}",
            },
            "first_player_advantage": {
                "wins_going_first": self.games_won_by_first,
                "wins_going_second": self.total_games - self.games_won_by_first,
                "first_win_rate": f"{first_win_rate:.1f}%",
                "second_win_rate": f"{(100-first_win_rate):.1f}%",
            }
        }

@dataclass
class PlayerStats:
    games_won: int = 0
    games_first: int = 0
    wins_when_first: int = 0
    total_winning_health: int = 0
    def get_stats(self, total_games: int) -> dict:
        wins_second = self.games_won - self.wins_when_first
        games_second = max(0, total_games - self.games_first)
        return {
            "total_wins": self.games_won,
            "overall_win_rate": f"{(self.games_won / total_games * 100) if total_games else 0:.1f}%",
            "position_breakdown": {
                "games_first": self.games_first,
                "wins_when_first": self.wins_when_first,
                "win_rate_first": f"{(self.wins_when_first / self.games_first * 100) if self.games_first else 0:.1f}%",
                "games_second": games_second,
                "wins_when_second": wins_second,
                "win_rate_second": f"{(wins_second / games_second * 100) if games_second else 0:.1f}%",
            },
            "avg_winning_health": f"{(self.total_winning_health / self.games_won) if self.games_won else 0:.1f}",
        }
from dataclasses import dataclass, field
from collections import defaultdict

# Assumes you already have:
# - @dataclass class GameStats: total_games, total_turns, total_rounds, games_won_by_first, get_stats()
# - @dataclass class PlayerStats: games_first, games_won, wins_when_first, total_winning_health, get_stats(total_games)
# - class GameRecord: p1_id, p2_id, first_player in {"p1","p2"}, winner in {"p1","p2", None}, winning_hero_health, turns, rounds

@dataclass
class _PlayerAgg:
    # exposure
    games: int = 0
    games_as_first: int = 0
    # wins
    wins: int = 0
    wins_as_first: int = 0
    # quality metrics
    total_winning_health: int = 0
    # opponent breakdowns (per opponent id)
    vs: dict = field(default_factory=lambda: defaultdict(lambda: {
        "games": 0,
        "games_as_first": 0,
        "wins": 0,
        "wins_as_first": 0,
        "total_winning_health": 0,
    }))

    def to_public(self):
        # derived
        losses = self.games - self.wins
        wr = (self.wins / self.games * 100) if self.games else 0.0
        wr_first = (self.wins_as_first / self.games_as_first * 100) if self.games_as_first else 0.0
        second_games = self.games - self.games_as_first
        wins_second = self.wins - self.wins_as_first
        wr_second = (wins_second / second_games * 100) if second_games else 0.0
        avg_whp = (self.total_winning_health / self.wins) if self.wins else 0.0

        vs_out = {}
        for opp, d in self.vs.items():
            opp_losses = d["games"] - d["wins"]
            opp_wr = (d["wins"] / d["games"] * 100) if d["games"] else 0.0
            og = d["games_as_first"]
            owf = d["wins_as_first"]
            osg = d["games"] - og
            osw = d["wins"] - owf
            opp_wr_first = (owf / og * 100) if og else 0.0
            opp_wr_second = (osw / osg * 100) if osg else 0.0
            opp_avg_whp = (d["total_winning_health"] / d["wins"]) if d["wins"] else 0.0
            vs_out[opp] = {
                "games": d["games"],
                "wins": d["wins"],
                "losses": opp_losses,
                "win_rate": round(opp_wr, 1),
                "first_player": {"games": og, "wins": owf, "win_rate": round(opp_wr_first, 1)},
                "second_player": {"games": osg, "wins": osw, "win_rate": round(opp_wr_second, 1)},
                "avg_winning_health": round(opp_avg_whp, 1),
            }

        return {
            "games": self.games,
            "wins": self.wins,
            "losses": losses,
            "win_rate": round(wr, 1),
            "first_player": {"games": self.games_as_first, "wins": self.wins_as_first, "win_rate": round(wr_first, 1)},
            "second_player": {"games": second_games, "wins": wins_second, "win_rate": round(wr_second, 1)},
            "avg_winning_health": round(avg_whp, 1),
            "vs": vs_out,
        }


class SimulationRecord:
    """
    Backward-compatible aggregation:
      - preserves legacy p1/p2 counters and game_stats (so existing callers keep working)
      - adds extended per-player and head-to-head analytics in result["extended"]
    """
    def __init__(self):
        # legacy
        self.game_stats = GameStats()
        self.p1_stats = PlayerStats()
        self.p2_stats = PlayerStats()
        # new
        self._players: dict[str, _PlayerAgg] = defaultdict(_PlayerAgg)
        # keyed by ordered tuple (a,b) with a<b for consistency
        self._pairs = defaultdict(lambda: {"games": 0, "first_wins": 0, "wins": {}})

    def record(self, rec):
        # --- legacy tallies (unchanged externally) ---
        self.game_stats.total_games += 1
        self.game_stats.total_turns += rec.turns
        self.game_stats.total_rounds += rec.rounds

        if rec.first_player == "p1":
            self.p1_stats.games_first += 1
        else:
            self.p2_stats.games_first += 1

        if rec.winner == "p1":
            self.p1_stats.games_won += 1
            self.p1_stats.total_winning_health += rec.winning_hero_health
        elif rec.winner == "p2":
            self.p2_stats.games_won += 1
            self.p2_stats.total_winning_health += rec.winning_hero_health

        if rec.winner and rec.winner == rec.first_player:
            if rec.winner == "p1":
                self.p1_stats.wins_when_first += 1
            else:
                self.p2_stats.wins_when_first += 1
            self.game_stats.games_won_by_first += 1

        # --- new: attribute to actual player ids ---
        a, b = rec.p1_id, rec.p2_id
        fp_id = a if rec.first_player == "p1" else b
        winner_id = a if rec.winner == "p1" else (b if rec.winner == "p2" else None)

        A = self._players[a]
        B = self._players[b]
        # exposure
        A.games += 1
        B.games += 1
        if fp_id == a:
            A.games_as_first += 1
        else:
            B.games_as_first += 1

        # per-opponent exposure
        A.vs[b]["games"] += 1
        B.vs[a]["games"] += 1
        if fp_id == a:
            A.vs[b]["games_as_first"] += 1
        else:
            B.vs[a]["games_as_first"] += 1

        # winner updates
        if winner_id is not None:
            W = self._players[winner_id]
            L_id = b if winner_id == a else a
            W.wins += 1
            W.total_winning_health += rec.winning_hero_health
            if fp_id == winner_id:
                W.wins_as_first += 1
                W.vs[L_id]["wins_as_first"] += 1
            W.vs[L_id]["wins"] += 1
            W.vs[L_id]["total_winning_health"] += rec.winning_hero_health

        # pair rollup
        k = tuple(sorted((a, b)))
        d = self._pairs[k]
        d["games"] += 1
        if winner_id is not None:
            d["wins"][winner_id] = d["wins"].get(winner_id, 0) + 1
            if winner_id == fp_id:
                d["first_wins"] += 1

    # ---- helpers for the extended report ----
    @staticmethod
    def _rate(n, d):
        return round((n / d * 100) if d else 0.0, 1)

    def _leaderboards(self):
        # build simple leaderboards (min 1 game)
        rows = []
        for pid, agg in self._players.items():
            if agg.games == 0:
                continue
            rows.append({
                "player": pid,
                "games": agg.games,
                "wins": agg.wins,
                "win_rate": self._rate(agg.wins, agg.games),
                "avg_winning_health": round((agg.total_winning_health / agg.wins) if agg.wins else 0.0, 1),
            })
        # sort by win_rate desc, then wins desc, then games desc
        top_by_wr = sorted(rows, key=lambda r: (r["win_rate"], r["wins"], r["games"]), reverse=True)
        top_by_whp = sorted(rows, key=lambda r: r["avg_winning_health"], reverse=True)
        return {
            "top_win_rate": top_by_wr[:10],
            "top_avg_winning_health": top_by_whp[:10],
        }

    def _pairs_public(self):
        out = {}
        for (a, b), d in self._pairs.items():
            aw = d["wins"].get(a, 0)
            bw = d["wins"].get(b, 0)
            out[f"{a} vs {b}"] = {
                "games": d["games"],
                a: aw,
                b: bw,
                "first_player_wins": d["first_wins"],
                "win_rate": {a: self._rate(aw, d["games"]), b: self._rate(bw, d["games"])},
            }
        return out
    
    def get_pairwise_winrate_matrix(self) -> dict[str, dict[str, float]]:
        """
        Returns a matrix of win rates: matrix[A][B] = A's win rate vs B (0-100 scale)
        Missing values are treated as 0.
        """
        players = list(self._players.keys())
        matrix = {a: {} for a in players}

        for (a, b), data in self._pairs.items():
            games = data["games"]
            if games == 0:
                continue
            wins_a = data["wins"].get(a, 0)
            wins_b = data["wins"].get(b, 0)
            wr_a = round((wins_a / games) * 100, 1)
            wr_b = round((wins_b / games) * 100, 1)

            matrix[a][b] = wr_a
            matrix[b][a] = wr_b

        return matrix
    
    def get_winrate_table(self, *, min_games: int = 1):
        """
        Return per-player rows sorted by win_rate desc.
        Each row: {player, games, wins, losses, win_rate}
        """
        rows = []
        for pid, agg in self._players.items():
            g = agg.games
            if g < min_games:
                continue
            w = agg.wins
            rows.append({
                "player": pid,
                "games": g,
                "wins": w,
                "losses": g - w,
                "win_rate": round((w / g * 100) if g else 0.0, 2),
            })
        rows.sort(key=lambda r: (r["win_rate"], r["wins"], r["games"]), reverse=True)
        return rows

    # ---- public API (unchanged) ----
    def get_summary_stats(self) -> dict:
        if self.game_stats.total_games == 0:
            return {"message": "No games played yet"}

        # legacy unchanged keys
        result = {
            "game_stats": self.game_stats.get_stats(),
            "player_stats": {  # keep existing shape p1/p2
                "p1": self.p1_stats.get_stats(self.game_stats.total_games),
                "p2": self.p2_stats.get_stats(self.game_stats.total_games),
            },
        }

        # NEW: rich analytics live under "extended" so old code ignores them safely
        result["extended"] = {
            "players": {pid: agg.to_public() for pid, agg in self._players.items()},
            "pairs": self._pairs_public(),
            "leaderboards": self._leaderboards(),
        }
        return result