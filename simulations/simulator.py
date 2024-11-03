from game_engine.game import GameManager, GameLogger
from pprint import pprint
import time

def run_simulation(num_games: int = 1000):
    logger = GameManager.run_simulation(num_games=num_games, log_file="simulation_results.jsonl")
    
    # Get statistics across all games
    stats = logger.get_summary_stats()
    pprint(stats)

def main():
    NUM_GAMES = 1000
    print(f"Running simulation with {NUM_GAMES} games...")
    start_time = time.time()
    run_simulation(NUM_GAMES)
    end_time = time.time()
    print(f"Simulation took {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()