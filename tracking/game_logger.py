from dataclasses import dataclass
from typing import Dict

@dataclass
class GameStats:
    """Overall game statistics"""
    total_games: int = 0
    total_turns: int = 0
    total_rounds: int = 0
    games_won_by_first: int = 0

    def get_stats(self) -> dict:
        """Convert raw data into calculated stats"""
        if self.total_games == 0:
            return {"message": "No games played yet"}

        first_win_rate = (self.games_won_by_first / self.total_games * 100) if self.total_games > 0 else 0
        second_win_rate = ((self.total_games - self.games_won_by_first) / self.total_games * 100) if self.total_games > 0 else 0
        avg_turns = self.total_turns / self.total_games if self.total_games > 0 else 0
        avg_rounds = self.total_rounds / self.total_games if self.total_games > 0 else 0

        return {
            "total_games": self.total_games,
            "average_length": {
                "turns": f"{avg_turns:.1f}",
                "rounds": f"{avg_rounds:.1f}"
            },
            "first_player_advantage": {
                "wins_going_first": self.games_won_by_first,
                "wins_going_second": self.total_games - self.games_won_by_first,
                "first_win_rate": f"{first_win_rate:.1f}%",
                "second_win_rate": f"{second_win_rate:.1f}%"
            }
        }

@dataclass
class PlayerStats:
    """Stats specific to a player"""
    games_won: int = 0
    games_first: int = 0  # Number of games going first
    wins_when_first: int = 0  # Wins when going first
    total_winning_health: int = 0
    
    def get_stats(self, total_games: int) -> dict:
        """Convert raw data into calculated stats"""
        win_rate = (self.games_won / total_games * 100) if total_games > 0 else 0
        first_win_rate = (self.wins_when_first / self.games_first * 100) if self.games_first > 0 else 0
        games_second = total_games - self.games_first
        wins_second = self.games_won - self.wins_when_first
        second_win_rate = (wins_second / games_second * 100) if games_second > 0 else 0
        avg_health = (self.total_winning_health / self.games_won) if self.games_won > 0 else 0
        
        return {
            "total_wins": self.games_won,
            "overall_win_rate": f"{win_rate:.1f}%",
            "position_breakdown": {
                "games_first": self.games_first,
                "wins_when_first": self.wins_when_first,
                "win_rate_first": f"{first_win_rate:.1f}%",
                "games_second": games_second,
                "wins_when_second": wins_second,
                "win_rate_second": f"{second_win_rate:.1f}%"
            },
            "avg_winning_health": f"{avg_health:.1f}"
        }

class GameLogger:
    def __init__(self, log_file: str = "game_logs.jsonl"):
        self.game_stats = GameStats()
        self.player1_stats = PlayerStats()
        self.player2_stats = PlayerStats()
        self.current_first_player = None

    def start_game(self, game_state) -> None:
        """Record game start data"""
        self.current_first_player = game_state.who_went_first
        
        # Track who went first
        if self.current_first_player == game_state.player1:
            self.player1_stats.games_first += 1
        else:
            self.player2_stats.games_first += 1
            
        self.game_stats.total_games += 1

    def end_game(self, game_state) -> None:
        """Record game end data"""
        if game_state.player1.is_dead() and game_state.player2.is_dead():
            return  # No stats recorded for ties
        
        # Record turn and round counts
        self.game_stats.total_turns += game_state.total_turns
        self.game_stats.total_rounds += game_state.current_round
        
        # Determine winner and record stats
        winner = game_state.player2 if game_state.player1.is_dead() else game_state.player1
        winner_stats = self.player1_stats if winner == game_state.player1 else self.player2_stats
        
        winner_stats.games_won += 1
        winner_stats.total_winning_health += winner.hero.health
        
        # Record if they won going first
        if winner == self.current_first_player:
            winner_stats.wins_when_first += 1
            self.game_stats.games_won_by_first += 1

    def get_summary_stats(self) -> dict:
        """Generate summary statistics"""
        if self.game_stats.total_games == 0:
            return {"message": "No games played yet"}

        return {
            "game_stats": self.game_stats.get_stats(),
            "player_stats": {
                "player1": self.player1_stats.get_stats(self.game_stats.total_games),
                "player2": self.player2_stats.get_stats(self.game_stats.total_games)
            }
        }