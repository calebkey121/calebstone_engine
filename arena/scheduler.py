from itertools import combinations

def round_robin_pairs(entries):
    # Unordered unique pairs
    for a, b in combinations(entries, 2):
        yield a, b
