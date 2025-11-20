"""
Test Script for MCDM Algorithms
Verifies Fuzzy AHP and Interval TOPSIS implementations
"""

import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from algorithms.fuzzy_ahp import FuzzyAHP
from algorithms.interval_topsis import IntervalTOPSIS


def test_fuzzy_ahp():
    """Test Fuzzy AHP implementation"""
    print("=" * 60)
    print("Testing Fuzzy AHP Algorithm")
    print("=" * 60)
    
    # Example: 3 criteria, 2 experts
    n_criteria = 3
    n_experts = 2
    
    # Create sample fuzzy comparison matrices
    # Expert 1's matrix
    matrix1 = np.zeros((n_criteria, n_criteria, 3))
    matrix1[0, 0] = [1, 1, 1]
    matrix1[1, 1] = [1, 1, 1]
    matrix1[2, 2] = [1, 1, 1]
    
    # C1 vs C2: C1 is moderately more important (3)
    matrix1[0, 1] = FuzzyAHP.get_fuzzy_number(3)
    matrix1[1, 0] = [1/4, 1/3, 1/2]  # Reciprocal
    
    # C1 vs C3: C1 is strongly more important (5)
    matrix1[0, 2] = FuzzyAHP.get_fuzzy_number(5)
    matrix1[2, 0] = [1/6, 1/5, 1/4]  # Reciprocal
    
    # C2 vs C3: C2 is weakly more important (2)
    matrix1[1, 2] = FuzzyAHP.get_fuzzy_number(2)
    matrix1[2, 1] = [1/3, 1/2, 1]  # Reciprocal
    
    # Expert 2's matrix (similar but slightly different)
    matrix2 = np.zeros((n_criteria, n_criteria, 3))
    matrix2[0, 0] = [1, 1, 1]
    matrix2[1, 1] = [1, 1, 1]
    matrix2[2, 2] = [1, 1, 1]
    
    matrix2[0, 1] = FuzzyAHP.get_fuzzy_number(4)
    matrix2[1, 0] = [1/5, 1/4, 1/3]
    
    matrix2[0, 2] = FuzzyAHP.get_fuzzy_number(6)
    matrix2[2, 0] = [1/7, 1/6, 1/5]
    
    matrix2[1, 2] = FuzzyAHP.get_fuzzy_number(3)
    matrix2[2, 1] = [1/4, 1/3, 1/2]
    
    fuzzy_matrices = [matrix1, matrix2]
    
    # Calculate weights
    crisp_weights, fuzzy_weights, cr = FuzzyAHP.calculate_weights(fuzzy_matrices)
    
    print("\nResults:")
    print(f"Crisp Weights: {crisp_weights}")
    print(f"Sum of weights: {np.sum(crisp_weights):.6f}")
    print(f"Consistency Ratio (CR): {cr:.4f}")
    
    if cr < 0.1:
        print("✓ CR is acceptable (< 0.1)")
    else:
        print("✗ CR needs review (>= 0.1)")
    
    print("\nFuzzy Weights (L, M, U):")
    for i, fw in enumerate(fuzzy_weights):
        print(f"  Criterion {i+1}: ({fw[0]:.4f}, {fw[1]:.4f}, {fw[2]:.4f})")
    
    return crisp_weights


def test_interval_topsis(weights):
    """Test Interval TOPSIS implementation"""
    print("\n" + "=" * 60)
    print("Testing Interval TOPSIS Algorithm")
    print("=" * 60)
    
    # Example: 4 alternatives, 3 criteria
    n_alternatives = 4
    n_criteria = 3
    
    # Create sample decision matrix with interval ratings
    decision_matrix = np.array([
        # Alternative 1
        [[7, 9], [5, 7], [3, 5]],  # Excellent, Good, Fair
        # Alternative 2
        [[5, 7], [7, 9], [5, 7]],  # Good, Excellent, Good
        # Alternative 3
        [[3, 5], [5, 7], [7, 9]],  # Fair, Good, Excellent
        # Alternative 4
        [[5, 7], [3, 5], [5, 7]]   # Good, Fair, Good
    ])
    
    # All criteria are benefit type
    is_benefit = np.array([True, True, True])
    
    # Calculate TOPSIS ranking
    CC, results = IntervalTOPSIS.rank_alternatives(decision_matrix, weights, is_benefit)
    
    print("\nResults:")
    print("Closeness Coefficients (CCi):")
    for i, cc in enumerate(CC):
        print(f"  Alternative {i+1}: {cc:.4f}")
    
    print("\nRanking (Best to Worst):")
    for rank, alt_idx in enumerate(results['ranking']):
        print(f"  Rank {rank+1}: Alternative {alt_idx+1} (CCi = {CC[alt_idx]:.4f})")
    
    print("\nDistances:")
    print("Distance to PIS:", results['distances_to_PIS'])
    print("Distance to NIS:", results['distances_to_NIS'])
    
    return results


def test_linguistic_scales():
    """Test linguistic scale conversions"""
    print("\n" + "=" * 60)
    print("Testing Linguistic Scales")
    print("=" * 60)
    
    print("\nFuzzy AHP Scale (sample values):")
    test_values = [1, 3, 5, 7, 9, -3, -5, -9]
    for val in test_values:
        fuzzy = FuzzyAHP.get_fuzzy_number(val)
        desc = FuzzyAHP.LINGUISTIC_SCALE[val][3]
        print(f"  {val:2d}: {fuzzy} - {desc}")
    
    print("\nInterval TOPSIS Ratings:")
    for rating, interval in IntervalTOPSIS.LINGUISTIC_RATINGS.items():
        print(f"  {rating:15s}: {interval}")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("MCDM Algorithm Test Suite")
    print("=" * 60)
    
    try:
        # Test linguistic scales
        test_linguistic_scales()
        
        # Test Fuzzy AHP
        weights = test_fuzzy_ahp()
        
        # Test Interval TOPSIS
        test_interval_topsis(weights)
        
        print("\n" + "=" * 60)
        print("✓ All tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
