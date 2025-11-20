"""
Test script to verify and debug Interval TOPSIS normalization
"""

import numpy as np
import sys
sys.path.append('g:/anti/supplier_selection_app')

from algorithms.interval_topsis import IntervalTOPSIS

# Test case from screenshot:
# Supplier A: Price=Very Good [7,9], Quality=Good [5,7], Delivery=Poor [1,3]
# Supplier B: Price=Fair [3,5], Quality=Fair [3,5], Delivery=Fair [3,5]

# Create decision matrix
decision_matrix = np.array([
    [[7, 9], [5, 7], [1, 3]],  # Supplier A
    [[3, 5], [3, 5], [3, 5]]   # Supplier B
])

# Assume equal weights for simplicity
weights = np.array([0.33, 0.33, 0.34])

# Criteria types: Price=benefit, Quality=benefit, Delivery=benefit
is_benefit = np.array([True, True, True])

print("=" * 60)
print("TESTING INTERVAL TOPSIS")
print("=" * 60)

print("\n1. INPUT DECISION MATRIX:")
print(f"Supplier A: Price={decision_matrix[0,0]}, Quality={decision_matrix[0,1]}, Delivery={decision_matrix[0,2]}")
print(f"Supplier B: Price={decision_matrix[1,0]}, Quality={decision_matrix[1,1]}, Delivery={decision_matrix[1,2]}")

# Test current normalization
print("\n2. CURRENT NORMALIZATION:")
normalized_current = IntervalTOPSIS.normalize_interval_matrix(decision_matrix, is_benefit)
print(f"Normalized A: {normalized_current[0]}")
print(f"Normalized B: {normalized_current[1]}")

# Manual calculation - Method 1 (current implementation)
print("\n3. MANUAL CALCULATION - CURRENT METHOD:")
for j in range(3):
    sum_squares = 0
    for i in range(2):
        sum_squares += decision_matrix[i, j, 0] ** 2 + decision_matrix[i, j, 1] ** 2
    
    norm_factor = np.sqrt(sum_squares)
    print(f"Criterion {j}: sum_squares={sum_squares}, norm_factor={norm_factor:.4f}")
    
    for i in range(2):
        n_L = decision_matrix[i, j, 0] / norm_factor
        n_U = decision_matrix[i, j, 1] / norm_factor
        print(f"  Alt {i}: [{decision_matrix[i,j,0]:.1f}, {decision_matrix[i,j,1]:.1f}] -> [{n_L:.4f}, {n_U:.4f}]")

# Manual calculation - Method 2 (separate normalization)
print("\n4. MANUAL CALCULATION - SEPARATE NORMALIZATION:")
for j in range(3):
    sum_L = np.sum(decision_matrix[:, j, 0] ** 2)
    sum_U = np.sum(decision_matrix[:, j, 1] ** 2)
    
    norm_L = np.sqrt(sum_L)
    norm_U = np.sqrt(sum_U)
    print(f"Criterion {j}: norm_L={norm_L:.4f}, norm_U={norm_U:.4f}")
    
    for i in range(2):
        n_L = decision_matrix[i, j, 0] / norm_L
        n_U = decision_matrix[i, j, 1] / norm_U
        print(f"  Alt {i}: [{decision_matrix[i,j,0]:.1f}, {decision_matrix[i,j,1]:.1f}] -> [{n_L:.4f}, {n_U:.4f}]")

# Full TOPSIS workflow
print("\n5. FULL TOPSIS RESULTS:")
CC, results = IntervalTOPSIS.rank_alternatives(decision_matrix, weights, is_benefit)
print(f"\nCloseness Coefficients:")
print(f"Supplier A: {CC[0]:.4f}")
print(f"Supplier B: {CC[1]:.4f}")
print(f"\nRanking: {results['ranking']}")

if CC[0] > CC[1]:
    print("Winner: Supplier A")
else:
    print("Winner: Supplier B")

print("\n6. EXPECTED RESULT:")
print("Based on the ratings:")
print("- Supplier A: Very Good price, Good quality, Poor delivery")
print("- Supplier B: Fair price, Fair quality, Fair delivery")
print("Supplier A has higher values in Price and Quality (2 out of 3 criteria)")
print("Expected: Supplier A should rank HIGHER (but might be close due to poor delivery)")
