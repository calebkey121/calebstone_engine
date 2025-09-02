from calebstone_engine.game import GameManager, GameLogger, PlayerConfig
from pprint import pprint
import time

def run_simulation(p1: PlayerConfig, p2: PlayerConfig, num_games = 1000):
    logger = GameManager.run_simulation(p1, p2, num_games, log_file="simulation_results.jsonl")
    
    # Get statistics across all games
    stats = logger.get_summary_stats()
    pprint(stats)

def main():
    p1 = PlayerConfig('random', 'Caleb', 'standard')
    p2 = PlayerConfig('random', 'Dio', 'standard')
    NUM_GAMES = 1
    print(f"Running simulation with {NUM_GAMES} games...")
    start_time = time.time()
    run_simulation(p1, p2, NUM_GAMES)
    end_time = time.time()
    print(f"Simulation took {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()