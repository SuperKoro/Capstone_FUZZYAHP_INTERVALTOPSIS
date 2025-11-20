import numpy as np
import sys
sys.path.append('g:/anti/supplier_selection_app')

from algorithms.interval_topsis import IntervalTOPSIS

# Test case
decision_matrix = np.array([
    [[7, 9], [5, 7], [1, 3]],  
    [[3, 5], [3, 5], [3, 5]]   
])

weights = np.array([0.33, 0.33, 0.34])
is_benefit = np.array([True, True, True])

print("Step 1: Normalize")
normalized = IntervalTOPSIS.normalize_interval_matrix(decision_matrix, is_benefit)
print(f"Normalized:\n{normalized}\n")

print("Step 2: Apply weights")
weighted = IntervalTOPSIS.apply_weights(normalized, weights)
print(f"Weighted:\n{weighted}\n")

print("Step 3: Calculate ideal solutions")
PIS, NIS = IntervalTOPSIS.calculate_ideal_solutions(weighted, is_benefit)
print(f"PIS:\n{PIS}")
print(f"NIS:\n{NIS}\n")

print("Analysis:")
print(f"is_benefit: {is_benefit}")
print("For benefit criteria, PIS should be MAX and NIS should be MIN")
print(f"\nweighted[:, 0, :] (Price - benefit):\n{weighted[:, 0, :]}")
print(f"Max: {np.max(weighted[:, 0, 0])}, {np.max(weighted[:, 0, 1])}")
print(f"Min: {np.min(weighted[:, 0, 0])}, {np.min(weighted[:, 0, 1])}")
