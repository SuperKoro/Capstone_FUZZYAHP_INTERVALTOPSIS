import numpy as np
import sys
sys.path.append('g:/anti/supplier_selection_app')

from algorithms.interval_topsis import IntervalTOPSIS

print("=" * 80)
print("DETAILED TOPSIS STEP-BY-STEP ANALYSIS")
print("=" * 80)

# Using simple test case
dm = np.array([
    [[7.0, 9.0], [5.0, 7.0], [1.0, 3.0]],  # A
    [[3.0, 5.0], [3.0, 5.0], [3.0, 5.0]]   # B
])

weights = np.array([0.33, 0.33, 0.34])
is_benefit = np.array([True, True, True])

print("\nINPUT:")
print(f"Decision Matrix:\n{dm}")
print(f"Weights: {weights}")
print(f"All criteria are BENEFIT\n")

# Step 1: Normalize
normalized = IntervalTOPSIS.normalize_interval_matrix(dm, is_benefit)
print("STEP 1: NORMALIZATION")
print("=" * 80)
for j in range(3):
    print(f"Criterion {j}:")
    sum_sq = sum(dm[i, j, 0]**2 + dm[i, j, 1]**2 for i in range(2))
    norm_factor = np.sqrt(sum_sq)
    print(f"  Sum of squares: {sum_sq:.2f}")
    print(f"  Norm factor: {norm_factor:.4f}")
    for i in range(2):
        print(f"  Alt {i}: [{dm[i,j,0]:.1f}, {dm[i,j,1]:.1f}] → [{normalized[i,j,0]:.4f}, {normalized[i,j,1]:.4f}]")
print()

# Step 2: Apply weights
weighted = IntervalTOPSIS.apply_weights(normalized, weights)
print("STEP 2: WEIGHTED MATRIX")
print("=" * 80)
print(f"Weighted:\n{weighted}\n")

# Step 3: Ideal solutions
PIS, NIS = IntervalTOPSIS.calculate_ideal_solutions(weighted, is_benefit)
print("STEP 3: IDEAL SOLUTIONS")
print("=" * 80)
print("For BENEFIT criteria: PIS = MAX, NIS = MIN")
for j in range(3):
    print(f"Criterion {j}:")
    print(f"  Min: [{np.min(weighted[:, j, 0]):.4f}, {np.min(weighted[:, j, 1]):.4f}]")
    print(f"  Max: [{np.max(weighted[:, j, 0]):.4f}, {np.max(weighted[:, j, 1]):.4f}]")
    print(f"  PIS: [{PIS[j, 0]:.4f}, {PIS[j, 1]:.4f}] (should be MAX)")
    print(f"  NIS: [{NIS[j, 0]:.4f}, {NIS[j, 1]:.4f}] (should be MIN)")
print()

# Step 4: Distances
print("STEP 4: DISTANCE CALCULATION")
print("=" * 80)
print("Distance formula: D(A,B) = sqrt((a^L - b^L)^2 + (a^U - b^U)^2)")

# Manual distance calculation
for i in range(2):
    print(f"\nAlternative {i}:")
    
    # Distance to PIS
    d_pis_manual = 0
    for j in range(3):
        d_L = (weighted[i, j, 0] - PIS[j, 0])**2
        d_U = (weighted[i, j, 1] - PIS[j, 1])**2
        d_j = np.sqrt(d_L + d_U)
        print(f"  Crit {j} to PIS: sqrt({d_L:.6f} + {d_U:.6f}) = {d_j:.6f}")
        d_pis_manual += d_j**2
    
    d_pis_manual = np.sqrt(d_pis_manual)
    print(f"  Total distance to PIS: {d_pis_manual:.6f}")
    
    # Distance to NIS
    d_nis_manual = 0
    for j in range(3):
        d_L = (weighted[i, j, 0] - NIS[j, 0])**2
        d_U = (weighted[i, j, 1] - NIS[j, 1])**2
        d_j = np.sqrt(d_L + d_U)
        print(f"  Crit {j} to NIS: sqrt({d_L:.6f} + {d_U:.6f}) = {d_j:.6f}")
        d_nis_manual += d_j**2
    
    d_nis_manual = np.sqrt(d_nis_manual)
    print(f"  Total distance to NIS: {d_nis_manual:.6f}")

dist_to_PIS, dist_to_NIS = IntervalTOPSIS.calculate_distances(weighted, PIS, NIS)
print(f"\nFunction results:")
print(f"  Dist to PIS: {dist_to_PIS}")
print(f"  Dist to NIS: {dist_to_NIS}")

# Step 5: Closeness
CC = IntervalTOPSIS.calculate_closeness_coefficient(dist_to_PIS, dist_to_NIS)
print("\nSTEP 5: CLOSENESS COEFFICIENT")
print("=" * 80)
print("Formula: CC = D_NIS / (D_PIS + D_NIS)")
for i in range(2):
    cc_manual = dist_to_NIS[i] / (dist_to_PIS[i] + dist_to_NIS[i])
    print(f"Alt {i}: {dist_to_NIS[i]:.4f} / ({dist_to_PIS[i]:.4f} + {dist_to_NIS[i]:.4f}) = {cc_manual:.4f}")

print(f"\nFinal CC: {CC}")
print(f"Winner: Alt {np.argmax(CC)}")

print("\n" + "=" * 80)
print("POTENTIAL ISSUE CHECK:")
print("=" * 80)
print("The issue might be in line 183:")
print("  sum_pis += IntervalTOPSIS.interval_distance(weighted[i, j], PIS[j]) ** 2")
print("This squares the interval_distance result!")
print("But interval_distance already returns sqrt(...)!")
print("So we're doing: sqrt(sum(sqrt(...)^2))")
print("This is CORRECT for Euclidean distance in n-dimensional space.")
