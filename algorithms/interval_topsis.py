"""
Interval TOPSIS Module
Implements Interval TOPSIS for alternative ranking
"""

import numpy as np
from typing import List, Dict, Tuple, Optional


class IntervalTOPSIS:
    """Interval TOPSIS implementation for ranking alternatives"""
    
    # Linguistic rating scale for performance evaluation
    LINGUISTIC_RATINGS = {
        "Very Poor": (0, 1),
        "Poor": (1, 3),
        "Fair": (3, 5),
        "Good": (5, 7),
        "Very Good": (7, 9),
        "Excellent": (9, 10)
    }
    @staticmethod
    def aggregate_expert_ratings(expert_matrices: List[np.ndarray]) -> np.ndarray:
        """
        Aggregate ratings from multiple experts using Arithmetic Mean
        
        Args:
            expert_matrices: List of decision matrices (one per expert)
                             Each matrix is (m, n, 2)
                             
        Returns:
            Aggregated decision matrix (m, n, 2)
        """
        if not expert_matrices:
            raise ValueError("No expert matrices to aggregate")
            
        # Stack matrices along a new axis: (k, m, n, 2)
        stacked = np.stack(expert_matrices)
        
        # Calculate mean along the first axis (experts)
        aggregated = np.mean(stacked, axis=0)
        
        return aggregated
    
    @staticmethod
    def get_interval_rating(rating_name: str) -> Tuple[float, float]:
        """
        Get interval values for a linguistic rating
        
        Args:
            rating_name: Name of the linguistic rating
            
        Returns:
            Tuple of (lower, upper) interval values
        """
        if rating_name not in IntervalTOPSIS.LINGUISTIC_RATINGS:
            raise ValueError(f"Invalid rating: {rating_name}")
        return IntervalTOPSIS.LINGUISTIC_RATINGS[rating_name]
    
    @staticmethod
    def normalize_interval_matrix(decision_matrix: np.ndarray, is_benefit: np.ndarray) -> np.ndarray:
        """
        Normalize interval decision matrix using vector normalization (Step 2)
        
        Formula:
        n_ij^L = l_ij / sqrt(sum((l_ij)^2 + (u_ij)^2))
        n_ij^U = u_ij / sqrt(sum((l_ij)^2 + (u_ij)^2))
        
        Args:
            decision_matrix: Decision matrix (m alternatives, n criteria, 2 for interval)
            is_benefit: Boolean array indicating if criterion is benefit (True) or cost (False)
            
        Returns:
            Normalized matrix (m, n, 2)
        """
        m, n, _ = decision_matrix.shape
        normalized = np.zeros_like(decision_matrix, dtype=float)
        
        for j in range(n):
            # Calculate normalization factor for criterion j
            # sqrt(sum of (l_ij^2 + u_ij^2) for all alternatives)
            sum_squares = 0
            for i in range(m):
                sum_squares += decision_matrix[i, j, 0] ** 2  # l^2
                sum_squares += decision_matrix[i, j, 1] ** 2  # u^2
            
            norm_factor = np.sqrt(sum_squares)
            
            if norm_factor == 0:
                norm_factor = 1  # Avoid division by zero
            
            # Normalize each alternative for this criterion
            for i in range(m):
                normalized[i, j, 0] = decision_matrix[i, j, 0] / norm_factor
                normalized[i, j, 1] = decision_matrix[i, j, 1] / norm_factor
        
        return normalized
    
    @staticmethod
    def apply_weights(normalized_matrix: np.ndarray, weights: np.ndarray) -> np.ndarray:
        """
        Apply criterion weights to normalized matrix
        
        Args:
            normalized_matrix: Normalized decision matrix (m, n, 2)
            weights: Criterion weights (n,)
            
        Returns:
            Weighted normalized matrix (m, n, 2)
        """
        m, n, _ = normalized_matrix.shape
        weighted = np.zeros_like(normalized_matrix)
        
        for i in range(m):
            for j in range(n):
                weighted[i, j, 0] = normalized_matrix[i, j, 0] * weights[j]
                weighted[i, j, 1] = normalized_matrix[i, j, 1] * weights[j]
        
        return weighted
    
    @staticmethod
    def calculate_ideal_solutions(weighted_matrix: np.ndarray, is_benefit: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate Positive Ideal Solution (PIS) and Negative Ideal Solution (NIS) (Step 4)
        
        For Benefit criteria:
        - PIS: maximum values
        - NIS: minimum values
        
        For Cost criteria:
        - PIS: minimum values  
        - NIS: maximum values
        
        Args:
            weighted_matrix: Weighted normalized matrix (m, n, 2)
            is_benefit: Boolean array for benefit/cost classification
            
        Returns:
            Tuple of (PIS, NIS), each is (n, 2)
        """
        m, n, _ = weighted_matrix.shape
        
        PIS = np.zeros((n, 2))
        NIS = np.zeros((n, 2))
        
        for j in range(n):
            if is_benefit[j]:
                # Benefit criterion: PIS = max, NIS = min
                PIS[j, 0] = np.max(weighted_matrix[:, j, 0])
                PIS[j, 1] = np.max(weighted_matrix[:, j, 1])
                
                NIS[j, 0] = np.min(weighted_matrix[:, j, 0])
                NIS[j, 1] = np.min(weighted_matrix[:, j, 1])
            else:
                # Cost criterion: PIS = min, NIS = max
                PIS[j, 0] = np.min(weighted_matrix[:, j, 0])
                PIS[j, 1] = np.min(weighted_matrix[:, j, 1])
                
                NIS[j, 0] = np.max(weighted_matrix[:, j, 0])
                NIS[j, 1] = np.max(weighted_matrix[:, j, 1])
        
        return PIS, NIS
    
    @staticmethod
    def interval_distance(interval1: np.ndarray, interval2: np.ndarray) -> float:
        """
        Calculate distance between two interval numbers (Step 5)
        
        Formula: D(A, B) = sqrt((a^L - b^L)^2 + (a^U - b^U)^2)
        
        Args:
            interval1: First interval [lower, upper]
            interval2: Second interval [lower, upper]
            
        Returns:
            Distance value
        """
        dist_lower = (interval1[0] - interval2[0]) ** 2
        dist_upper = (interval1[1] - interval2[1]) ** 2
        return np.sqrt(dist_lower + dist_upper)
    
    @staticmethod
    def calculate_distances(weighted_matrix: np.ndarray, PIS: np.ndarray, 
                          NIS: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate distances from each alternative to PIS and NIS
        
        Args:
            weighted_matrix: Weighted normalized matrix (m, n, 2)
            PIS: Positive Ideal Solution (n, 2)
            NIS: Negative Ideal Solution (n, 2)
            
        Returns:
            Tuple of (distances_to_PIS, distances_to_NIS), each is (m,)
        """
        m, n, _ = weighted_matrix.shape
        
        dist_to_PIS = np.zeros(m)
        dist_to_NIS = np.zeros(m)
        
        for i in range(m):
            # Calculate distance to PIS
            sum_pis = 0
            for j in range(n):
                sum_pis += IntervalTOPSIS.interval_distance(weighted_matrix[i, j], PIS[j]) ** 2
            dist_to_PIS[i] = np.sqrt(sum_pis)
            
            # Calculate distance to NIS
            sum_nis = 0
            for j in range(n):
                sum_nis += IntervalTOPSIS.interval_distance(weighted_matrix[i, j], NIS[j]) ** 2
            dist_to_NIS[i] = np.sqrt(sum_nis)
        
        return dist_to_PIS, dist_to_NIS
    
    @staticmethod
    def calculate_closeness_coefficient(dist_to_PIS: np.ndarray, 
                                       dist_to_NIS: np.ndarray) -> np.ndarray:
        """
        Calculate Closeness Coefficient (CCi) for each alternative
        
        Args:
            dist_to_PIS: Distances to Positive Ideal Solution (m,)
            dist_to_NIS: Distances to Negative Ideal Solution (m,)
            
        Returns:
            Closeness coefficients (m,)
        """
        m = len(dist_to_PIS)
        CC = np.zeros(m)
        
        for i in range(m):
            denominator = dist_to_PIS[i] + dist_to_NIS[i]
            if denominator == 0:
                CC[i] = 0
            else:
                CC[i] = dist_to_NIS[i] / denominator
        
        return CC
    
    @classmethod
    def rank_alternatives(cls, decision_matrix: np.ndarray, weights: np.ndarray,
                         is_benefit: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """
        Complete TOPSIS workflow to rank alternatives
        
        Args:
            decision_matrix: Interval decision matrix (m alternatives, n criteria, 2)
            weights: Criterion weights from AHP (n,)
            is_benefit: Boolean array for benefit/cost criteria (n,)
            
        Returns:
            Tuple of (closeness_coefficients, detailed_results_dict)
        """
        # Convert to float to avoid integer division issues
        decision_matrix = decision_matrix.astype(float)
        
        # DEBUG: Commented out for production
        # print("\n--- TOPSIS DEBUG LOG ---")
        # print(f"Input Matrix:\n{decision_matrix}")
        # print(f"Weights: {weights}")
        # print(f"Is Benefit: {is_benefit}")
        
        # Step 1: Normalize the decision matrix
        normalized = cls.normalize_interval_matrix(decision_matrix, is_benefit)
        # print(f"Normalized:\n{normalized}")
        
        # Step 2: Apply weights
        weighted = cls.apply_weights(normalized, weights)
        # print(f"Weighted:\n{weighted}")
        
        # Step 3: Calculate ideal solutions (needs is_benefit)
        PIS, NIS = cls.calculate_ideal_solutions(weighted, is_benefit)
        # print(f"PIS: {PIS}")
        # print(f"NIS: {NIS}")
        
        # Step 4: Calculate distances
        dist_to_PIS, dist_to_NIS = cls.calculate_distances(weighted, PIS, NIS)
        # print(f"Dist to PIS: {dist_to_PIS}")
        # print(f"Dist to NIS: {dist_to_NIS}")
        
        # Step 5: Calculate closeness coefficients
        CC = cls.calculate_closeness_coefficient(dist_to_PIS, dist_to_NIS)
        # print(f"CC: {CC}")
        # print("------------------------\n")
        
        # Prepare detailed results
        results = {
            'normalized_matrix': normalized,
            'weighted_matrix': weighted,
            'PIS': PIS,
            'NIS': NIS,
            'distances_to_PIS': dist_to_PIS,
            'distances_to_NIS': dist_to_NIS,
            'closeness_coefficients': CC,
            'ranking': np.argsort(-CC)  # Descending order (highest CC is best)
        }
        
        return CC, results
