"""
Test script to debug AHP calc weight calculation bug
Reproduce the issue where one criterion gets 100% weight
"""
import sys
sys.path.insert(0, 'G:/anti/supplier_selection_app')

import numpy as np
from algorithms.fuzzy_ahp import FuzzyAHP

# Reproduce user's comparisons from the screenshot:
# 4 criteria: 1, 2, 3, 4
# Comparisons:
# 1 vs 2: 2 (Weakly more important) → (1, 2, 3)
# 1 vs 3: 2 (Weakly more important) → (1, 2, 3)
# 1 vs 4: 1 (Equally important) → (1, 1, 1)
# 2 vs 3: 3 (Moderately more important) → (2, 3, 4)

print("Creating fuzzy comparison matrix...")
print("Comparisons:")
print("  1 vs 2: 2 (Weakly more important)")
print("  1 vs 3: 2 (Weakly more important)")
print("  1 vs 4: 1 (Equally important)")
print("  2 vs 3: 3 (Moderately more important)")
print()

# Create the matrix
n = 4
matrix = np.zeros((n, n, 3))

# Diagonal = (1, 1, 1)
for i in range(n):
    matrix[i, i] = [1, 1, 1]

# Fill comparisons (using 0-indexed: 0=criterion1, 1=criterion2, etc.)
# 1 vs 2: (1, 2, 3)
matrix[0, 1] = [1, 2, 3]
matrix[1, 0] = [1/3, 1/2, 1/1]

# 1 vs 3: (1, 2, 3)
matrix[0, 2] = [1, 2, 3]
matrix[2, 0] = [1/3, 1/2, 1/1]

# 1 vs 4: (1, 1, 1)
matrix[0, 3] = [1, 1, 1]
matrix[3, 0] = [1/1, 1/1, 1/1]

# 2 vs 3: (2, 3, 4)
matrix[1, 2] = [2, 3, 4]
matrix[2, 1] = [1/4, 1/3, 1/2]

# Missing comparisons (will use defaults or incomplete matrix handling)
# 2 vs 4: should be filled by reciprocity or assumed equal
# 3 vs 4: should be filled by reciprocity or assumed equal

print("Matrix constructed. Checking for missing comparisons...")
print(f"Matrix shape: {matrix.shape}")
print()

# Calculate weights using single expert (no aggregation)
print("Calculating weights...")
weights, fuzzy_weights, cr, ci, lambda_max = FuzzyAHP.calculate_weights([matrix])

print("\n" + "="*60)
print("RESULTS:")
print("="*60)
print(f"Crisp weights: {weights}")
print(f"Sum: {weights.sum()}")
print(f"Percentages: {weights * 100}")
print()
print(f"Lambda max: {lambda_max:.4f}")
print(f"CI: {ci:.4f}")
print(f"CR: {cr:.4f}")
print()

# Expected: weights should be distributed, NOT 100% to one criterion
if weights[0] > 0.9:
    print("❌ BUG CONFIRMED: Criterion 1 has > 90% weight!")
    print("This is INCORRECT based on the comparisons.")
else:
    print("✓ Weights appear distributed correctly")

print("\n" + "="*60)
print("DETAILED ANALYSIS:")
print("="*60)

# Print the fuzzy matrix
print("\nFuzzy comparison matrix (middle values):")
print(matrix[:, :, 1])

# Calculate fuzzy weights manually to debug
print("\nStep-by-step calculation:")
fuzzy_r = np.zeros((n, 3))
for i in range(n):
    row_l = matrix[i, :, 0]
    row_m = matrix[i, :, 1] 
    row_u = matrix[i, :, 2]
    
    fuzzy_r[i, 0] = np.prod(row_l) ** (1/n)
    fuzzy_r[i, 1] = np.prod(row_m) ** (1/n)
    fuzzy_r[i, 2] = np.prod(row_u) ** (1/n)
    
    print(f"  r_{i+1} = ({fuzzy_r[i, 0]:.4f}, {fuzzy_r[i, 1]:.4f}, {fuzzy_r[i, 2]:.4f})")

print(f"\nSum of r: ({np.sum(fuzzy_r[:, 0]):.4f}, {np.sum(fuzzy_r[:, 1]):.4f}, {np.sum(fuzzy_r[:, 2]):.4f})")

# Fuzzy weights
sum_r_l = np.sum(fuzzy_r[:, 0])
sum_r_m = np.sum(fuzzy_r[:, 1])
sum_r_u = np.sum(fuzzy_r[:, 2])

inv_sum_l = 1 / sum_r_u
inv_sum_m = 1 / sum_r_m
inv_sum_u = 1 / sum_r_l

print(f"\nInverse of sum: ({inv_sum_l:.4f}, {inv_sum_m:.4f}, {inv_sum_u:.4f})")

fuzzy_weights_manual = np.zeros((n, 3))
for i in range(n):
    fuzzy_weights_manual[i, 0] = fuzzy_r[i, 0] * inv_sum_l
    fuzzy_weights_manual[i, 1] = fuzzy_r[i, 1] * inv_sum_m
    fuzzy_weights_manual[i, 2] = fuzzy_r[i, 2] * inv_sum_u
    print(f"  w_{i+1} (fuzzy) = ({fuzzy_weights_manual[i, 0]:.4f}, {fuzzy_weights_manual[i, 1]:.4f}, {fuzzy_weights_manual[i, 2]:.4f})")

# Defuzzify
crisp_manual = np.array([(l + m + u) / 3 for l, m, u in fuzzy_weights_manual])
crisp_manual = crisp_manual / crisp_manual.sum()

print(f"\nDefuzzified weights: {crisp_manual}")
print(f"Percentages: {crisp_manual * 100}")
