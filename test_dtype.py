import numpy as np
import sys
sys.path.append('g:/anti/supplier_selection_app')

from algorithms.interval_topsis import IntervalTOPSIS

# Test with integer input
decision_matrix_int = np.array([
    [[7, 9], [5, 7], [1, 3]],  
    [[3, 5], [3, 5], [3, 5]]   
])

# Test with float input
decision_matrix_float = np.array([
    [[7.0, 9.0], [5.0, 7.0], [1.0, 3.0]],  
    [[3.0, 5.0], [3.0, 5.0], [3.0, 5.0]]   
])

is_benefit = np.array([True, True, True])

print("Test 1: Integer input")
print(f"Input dtype: {decision_matrix_int.dtype}")
normalized_int = IntervalTOPSIS.normalize_interval_matrix(decision_matrix_int, is_benefit)
print(f"Normalized dtype: {normalized_int.dtype}")
print(f"Normalized:\n{normalized_int}\n")

print("Test 2: Float input")
print(f"Input dtype: {decision_matrix_float.dtype}")
normalized_float = IntervalTOPSIS.normalize_interval_matrix(decision_matrix_float, is_benefit)
print(f"Normalized dtype: {normalized_float.dtype}")
print(f"Normalized:\n{normalized_float}\n")
