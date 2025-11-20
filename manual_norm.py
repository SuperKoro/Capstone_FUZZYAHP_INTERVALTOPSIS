import numpy as np

# Manual test of normalization
decision_matrix = np.array([
    [[7, 9], [5, 7], [1, 3]],  
    [[3, 5], [3, 5], [3, 5]]   
], dtype=float)

m, n, _ = decision_matrix.shape
normalized = np.zeros_like(decision_matrix)

print("MANUAL NORMALIZATION TEST")
print(f"Input matrix dtype: {decision_matrix.dtype}")
print(f"Input matrix:\n{decision_matrix}\n")

for j in range(n):
    print(f"\nCriterion {j}:")
    sum_squares = 0
    for i in range(m):
        print(f"  Alt {i}: L={decision_matrix[i, j, 0]}, U={decision_matrix[i, j, 1]}")
        print(f"    L^2={decision_matrix[i, j, 0]**2}, U^2={decision_matrix[i, j, 1]**2}")
        sum_squares += decision_matrix[i, j, 0] ** 2 + decision_matrix[i, j, 1] ** 2
    
    print(f"  sum_squares = {sum_squares}")
    norm_factor = np.sqrt(sum_squares)
    print(f"  norm_factor = {norm_factor}")
    
    for i in range(m):
        normalized[i, j, 0] = decision_matrix[i, j, 0] / norm_factor
        normalized[i, j, 1] = decision_matrix[i, j, 1] / norm_factor
        print(f"  Alt {i} normalized: [{normalized[i, j, 0]:.4f}, {normalized[i, j, 1]:.4f}]")

print(f"\nFinal normalized matrix:\n{normalized}")
