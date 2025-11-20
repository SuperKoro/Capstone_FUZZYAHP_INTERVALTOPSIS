"""
Fuzzy AHP (Analytic Hierarchy Process) Module
Implements Fuzzy AHP using Triangular Fuzzy Numbers and Geometric Mean
"""

import numpy as np
from typing import List, Dict, Tuple, Optional


class FuzzyAHP:
    """Fuzzy AHP implementation for criteria weighting"""
    
    # Comprehensive 17-level fuzzy linguistic scale
    LINGUISTIC_SCALE = {
        -9: (1/9, 1/9, 1/8, "Absolutely less important"),
        -8: (1/9, 1/8, 1/7, "Very, very strongly less important"),
        -7: (1/8, 1/7, 1/6, "Strongly very less important"),
        -6: (1/7, 1/6, 1/5, "Strongly plus less important"),
        -5: (1/6, 1/5, 1/4, "Strongly less important"),
        -4: (1/5, 1/4, 1/3, "Moderately plus less important"),
        -3: (1/4, 1/3, 1/2, "Moderately less important"),
        -2: (1/3, 1/2, 1, "Weakly or slightly less important"),
        1: (1, 1, 1, "Equally important"),
        2: (1, 2, 3, "Weakly or slightly more important"),
        3: (2, 3, 4, "Moderately more important"),
        4: (3, 4, 5, "Moderately plus more important"),
        5: (4, 5, 6, "Strongly more important"),
        6: (5, 6, 7, "Strongly plus more important"),
        7: (6, 7, 8, "Strongly very more important"),
        8: (7, 8, 9, "Very, very strongly more important"),
        9: (8, 9, 9, "Absolutely more important")
    }
    
    @staticmethod
    def get_fuzzy_number(scale_value: int) -> Tuple[float, float, float]:
        """
        Get triangular fuzzy number for a linguistic scale value
        
        Args:
            scale_value: Integer from -9 to 9 (excluding 0)
            
        Returns:
            Tuple of (lower, middle, upper) fuzzy values
        """
        if scale_value not in FuzzyAHP.LINGUISTIC_SCALE:
            raise ValueError(f"Invalid scale value: {scale_value}. Must be -9 to 9 (excluding 0)")
        return FuzzyAHP.LINGUISTIC_SCALE[scale_value][:3]
    
    
    @staticmethod
    def fuzzy_geometric_mean(fuzzy_matrices: List[np.ndarray], expert_weights: Optional[List[float]] = None) -> np.ndarray:
        """
        Calculate fuzzy geometric mean of multiple fuzzy comparison matrices (Step 1)
        Aggregates expert judgments using weighted geometric mean for each TFN component
        
        Args:
            fuzzy_matrices: List of fuzzy matrices, each is (n, n, 3) where last dim is (l, m, u)
            expert_weights: Optional list of expert weights (must sum to 1.0)
                          If None or all equal, uses standard geometric mean (1/K)
            
        Returns:
            Aggregated fuzzy matrix (n, n, 3)
        """
        if not fuzzy_matrices:
            raise ValueError("No matrices provided")
        
        n_experts = len(fuzzy_matrices)
        n_criteria = fuzzy_matrices[0].shape[0]
        
        # Handle weights
        if expert_weights is None or len(expert_weights) != n_experts:
            # Equal weights: standard geometric mean
            weights = [1.0 / n_experts] * n_experts
        else:
            weights = expert_weights
        
        # Initialize aggregated matrix
        aggregated = np.zeros((n_criteria, n_criteria, 3))
        
        for i in range(n_criteria):
            for j in range(n_criteria):
                if i == j:
                    aggregated[i, j] = [1, 1, 1]
                else:
                    # Collect all fuzzy values for this comparison across experts
                    l_values = [matrix[i, j, 0] for matrix in fuzzy_matrices]
                    m_values = [matrix[i, j, 1] for matrix in fuzzy_matrices]
                    u_values = [matrix[i, j, 2] for matrix in fuzzy_matrices]
                    
                    # Weighted geometric mean: ∏(x_k^ω_k)
                    # l_ij = (l_1^ω_1) × (l_2^ω_2) × ... × (l_K^ω_K)
                    aggregated[i, j, 0] = np.prod([l ** w for l, w in zip(l_values, weights)])
                    aggregated[i, j, 1] = np.prod([m ** w for m, w in zip(m_values, weights)])
                    aggregated[i, j, 2] = np.prod([u ** w for u, w in zip(u_values, weights)])
        
        return aggregated
    
    @staticmethod
    def calculate_fuzzy_weights(fuzzy_matrix: np.ndarray) -> np.ndarray:
        """
        Calculate fuzzy weights from aggregated fuzzy comparison matrix
        Using Buckley's method: Steps 2, 3
        
        Args:
            fuzzy_matrix: Fuzzy comparison matrix (n, n, 3)
            
        Returns:
            Fuzzy weights (n, 3) where each row is (l, m, u) for a criterion
        """
        n = fuzzy_matrix.shape[0]
        
        # Step 2: Calculate fuzzy geometric mean per row (r_i)
        fuzzy_r = np.zeros((n, 3))
        
        for i in range(n):
            # Geometric mean of row i for each fuzzy component
            row_l = fuzzy_matrix[i, :, 0]
            row_m = fuzzy_matrix[i, :, 1]
            row_u = fuzzy_matrix[i, :, 2]
            
            fuzzy_r[i, 0] = np.prod(row_l) ** (1/n)
            fuzzy_r[i, 1] = np.prod(row_m) ** (1/n)
            fuzzy_r[i, 2] = np.prod(row_u) ** (1/n)
        
        # Step 3: Calculate fuzzy weights (w_i = r_i ⊗ (r_1 ⊕ r_2 ⊕ ... ⊕ r_n)^-1)
        # First, sum all r_i (addition of TFNs)
        sum_r_l = np.sum(fuzzy_r[:, 0])
        sum_r_m = np.sum(fuzzy_r[:, 1])
        sum_r_u = np.sum(fuzzy_r[:, 2])
        
        # Inverse of sum: (l, m, u)^-1 = (1/u, 1/m, 1/l)
        inv_sum_l = 1 / sum_r_u
        inv_sum_m = 1 / sum_r_m
        inv_sum_u = 1 / sum_r_l
        
        # Multiply each r_i by inverse of sum
        fuzzy_weights = np.zeros((n, 3))
        for i in range(n):
            fuzzy_weights[i, 0] = fuzzy_r[i, 0] * inv_sum_l
            fuzzy_weights[i, 1] = fuzzy_r[i, 1] * inv_sum_m
            fuzzy_weights[i, 2] = fuzzy_r[i, 2] * inv_sum_u
        
        return fuzzy_weights
    
    @staticmethod
    def defuzzify(fuzzy_weights: np.ndarray) -> np.ndarray:
        """
        Defuzzify fuzzy weights using Center of Area (CoA) method (Step 4)
        Then normalize to sum to 1 (Step 5)
        
        Args:
            fuzzy_weights: Fuzzy weights (n, 3)
            
        Returns:
            Crisp normalized weights (n,)
        """
        n = fuzzy_weights.shape[0]
        crisp_weights = np.zeros(n)
        
        # Step 4: Defuzzification - Center of Area
        for i in range(n):
            l, m, u = fuzzy_weights[i]
            crisp_weights[i] = (l + m + u) / 3
        
        # Step 5: Normalization
        total = np.sum(crisp_weights)
        if total > 0:
            crisp_weights = crisp_weights / total
        
        return crisp_weights
    
    @staticmethod
    def calculate_consistency_ratio(comparison_matrix: np.ndarray) -> Tuple[float, float, float]:
        """
        Calculate Consistency Ratio (CR) for a crisp comparison matrix
        
        Args:
            comparison_matrix: Crisp pairwise comparison matrix (n, n)
            
        Returns:
            Tuple of (CR, CI, lambda_max)
        """
        n = comparison_matrix.shape[0]
        
        # Random Index (RI) values for different matrix sizes
        RI = {1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 
              8: 1.41, 9: 1.45, 10: 1.49, 11: 1.51, 12: 1.48, 13: 1.56, 
              14: 1.57, 15: 1.59}
        
        if n < 3:
            return 0.0, 0.0, float(n)  # CR is not applicable for n < 3
        
        # Calculate eigenvalues
        eigenvalues = np.linalg.eigvals(comparison_matrix)
        lambda_max = np.max(np.real(eigenvalues))
        
        # Calculate Consistency Index (CI)
        CI = (lambda_max - n) / (n - 1)
        
        # Calculate Consistency Ratio (CR)
        CR = CI / RI.get(n, 1.49)
        
        return CR, CI, lambda_max
    
    @classmethod
    def calculate_weights(cls, fuzzy_matrices: List[np.ndarray], expert_weights: Optional[List[float]] = None) -> Tuple[np.ndarray, np.ndarray, float, float, float]:
        """
        Complete workflow: aggregate matrices, calculate fuzzy weights, defuzzify, and check consistency
        
        Args:
            fuzzy_matrices: List of fuzzy comparison matrices from multiple experts
            expert_weights: Optional list of expert weights (must sum to 1.0)
            
        Returns:
            Tuple of (crisp_weights, fuzzy_weights, cr, ci, lambda_max)
        """
        # Step 1: Aggregate expert judgments using weighted fuzzy geometric mean
        aggregated_matrix = cls.fuzzy_geometric_mean(fuzzy_matrices, expert_weights)
        
        # Step 2: Calculate fuzzy weights
        fuzzy_weights = cls.calculate_fuzzy_weights(aggregated_matrix)
        
        # Step 3: Defuzzify to get crisp weights
        crisp_weights = cls.defuzzify(fuzzy_weights)
        
        # Step 4: Calculate consistency ratio using middle values
        crisp_matrix = aggregated_matrix[:, :, 1]  # Use middle values for CR calculation
        cr, ci, lambda_max = cls.calculate_consistency_ratio(crisp_matrix)
        
        return crisp_weights, fuzzy_weights, cr, ci, lambda_max

    @staticmethod
    def analyze_inconsistency(comparison_matrix: np.ndarray, weights: np.ndarray, criteria_names: List[str] = None) -> str:
        """
        Analyze the comparison matrix to find the most inconsistent pair
        
        Args:
            comparison_matrix: Crisp pairwise comparison matrix (n, n)
            weights: Calculated weights (n,)
            criteria_names: Optional list of criteria names for better message
            
        Returns:
            Suggestion string explaining the inconsistency
        """
        n = comparison_matrix.shape[0]
        max_diff = 0
        worst_pair = None
        
        # Find the pair (i, j) where a_ij differs most from w_i / w_j
        for i in range(n):
            for j in range(i + 1, n):
                ratio = weights[i] / weights[j] if weights[j] != 0 else 0
                judgment = comparison_matrix[i, j]
                
                # Calculate relative difference
                if judgment > 0:
                    diff = abs(np.log(judgment) - np.log(ratio))
                    if diff > max_diff:
                        max_diff = diff
                        worst_pair = (i, j)
        
        if worst_pair:
            i, j = worst_pair
            judgment = comparison_matrix[i, j]
            ratio = weights[i] / weights[j]
            
            name_i = criteria_names[i] if criteria_names else f"Criterion {i+1}"
            name_j = criteria_names[j] if criteria_names else f"Criterion {j+1}"
            
            if judgment > ratio:
                # Judgment is too high -> i is less important than stated relative to j
                return (f"Inconsistency found between '{name_i}' and '{name_j}'.\n"
                        f"You rated '{name_i}' as {judgment:.2f} times more important than '{name_j}',\n"
                        f"but the overall weights suggest it should be closer to {ratio:.2f}.\n"
                        f"Suggestion: Reduce the importance of '{name_i}' relative to '{name_j}'.")
            else:
                # Judgment is too low -> i is more important than stated relative to j
                return (f"Inconsistency found between '{name_i}' and '{name_j}'.\n"
                        f"You rated '{name_i}' as {judgment:.2f} times more important than '{name_j}',\n"
                        f"but the overall weights suggest it should be closer to {ratio:.2f}.\n"
                        f"Suggestion: Increase the importance of '{name_i}' relative to '{name_j}'.")
        
        return "No significant inconsistency found."
    
    @staticmethod
    def create_fuzzy_matrix_from_comparisons(n_criteria: int, comparisons: List[Dict], 
                                            criteria_ids: List[int] = None) -> np.ndarray:
        """
        Create a fuzzy comparison matrix from pairwise comparison data
        
        Args:
            n_criteria: Number of criteria
            comparisons: List of comparison dictionaries with keys:
                        'criterion1_id', 'criterion2_id', 'fuzzy_l', 'fuzzy_m', 'fuzzy_u'
            criteria_ids: List of criterion IDs in order (optional, for ID mapping)
            
        Returns:
            Fuzzy comparison matrix (n, n, 3)
        """
        matrix = np.zeros((n_criteria, n_criteria, 3))
        
        # Set diagonal to (1, 1, 1)
        for i in range(n_criteria):
            matrix[i, i] = [1, 1, 1]
        
        # Create ID to index mapping if criteria_ids provided
        if criteria_ids:
            id_to_idx = {cid: idx for idx, cid in enumerate(criteria_ids)}
        else:
            # Assume IDs are 0-indexed already
            id_to_idx = {i: i for i in range(n_criteria)}
        
        # Fill matrix from comparisons
        for comp in comparisons:
            c1_id = comp['criterion1_id']
            c2_id = comp['criterion2_id']
            
            # Map IDs to indices
            i = id_to_idx.get(c1_id, c1_id)
            j = id_to_idx.get(c2_id, c2_id)
            
            matrix[i, j] = [comp['fuzzy_l'], comp['fuzzy_m'], comp['fuzzy_u']]
            
            # Reciprocal for symmetric position
            matrix[j, i] = [1/comp['fuzzy_u'], 1/comp['fuzzy_m'], 1/comp['fuzzy_l']]
        
        return matrix
