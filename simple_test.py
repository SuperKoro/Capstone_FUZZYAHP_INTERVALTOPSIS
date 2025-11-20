import numpy as np
import sys
sys.path.append('g:/anti/supplier_selection_app')

from algorithms.interval_topsis import IntervalTOPSIS

# Test case: Supplier A vs Supplier B
decision_matrix = np.array([
    [[7, 9], [5, 7], [1, 3]],  # A: Very Good, Good, Poor
    [[3, 5], [3, 5], [3, 5]]   # B: Fair, Fair, Fair
])

weights = np.array([0.33, 0.33, 0.34])
is_benefit = np.array([True, True, True])

CC, results = IntervalTOPSIS.rank_alternatives(decision_matrix, weights, is_benefit)

print(f"Supplier A CC: {CC[0]:.4f}")
print(f"Supplier B CC: {CC[1]:.4f}")
print(f"Ranking: {results['ranking']}")
print(f"Winner: Supplier {'A' if CC[0] > CC[1] else 'B'}")

print("\nDetailed:")
print(f"PIS: {results['PIS']}")
print(f"NIS: {results['NIS']}")
print(f"Dist to PIS: {results['distances_to_PIS']}")
print(f"Dist to NIS: {results['distances_to_NIS']}")
