"""
Sensitivity Analysis Module - Weight Perturbation with Proper Normalization
Implements mathematically sound weight perturbation for TOPSIS sensitivity analysis
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from algorithms.interval_topsis import IntervalTOPSIS


class SensitivityAnalysis:
    """
    Sensitivity analysis for MCDM results
    
    Note: This analysis perturbs weights at the TOPSIS aggregation phase,
    not by modifying AHP comparison matrices. This is a "what-if" analysis
    on final weights.
    """
    
    @staticmethod
    def normalize_weights_after_perturbation(
        weights: np.ndarray, 
        perturbed_index: int, 
        delta: float
    ) -> np.ndarray:
        """
        Properly normalize weights after perturbing one criterion
        
        Uses NumPy vectorization for efficiency. Handles edge cases:
        - Division by zero when original weight is ~1.0
        - Over-perturbation beyond [0, 1] bounds
        - Floating point precision errors
        
        When increasing w_i by delta, decrease other weights proportionally
        to maintain sum = 1.0
        
        Formula:
            w_i' = w_i + delta (clamped to [0, 1])
            w_j' = w_j * (1 - w_i') / (1 - w_i)  for all j ≠ i
        
        Args:
            weights: Original weights (n,) summing to 1.0
            perturbed_index: Index of weight to perturb
            delta: Absolute change amount (can be negative)
            
        Returns:
            Normalized weights (n,) summing to 1.0
            
        Example:
            >>> weights = np.array([0.5, 0.3, 0.2])
            >>> new_weights = normalize_weights_after_perturbation(weights, 0, 0.1)
            >>> # w_0: 0.5 + 0.1 = 0.6
            >>> # w_1: 0.3 * (1 - 0.6) / (1 - 0.5) = 0.24
            >>> # w_2: 0.2 * (1 - 0.6) / (1 - 0.5) = 0.16
            >>> # Sum: 0.6 + 0.24 + 0.16 = 1.0 ✓
        """
        n = len(weights)
        new_weights = weights.copy()
        
        # 1. Get original target weight
        w_target_old = weights[perturbed_index]
        
        # 2. Calculate new target weight with bounds checking
        # Edge Case C: Over-perturbation handled
        w_target_new = w_target_old + delta
        w_target_new = np.clip(w_target_new, 0.0, 1.0 - 1e-9)
        
        # 3. Handle Division by Zero Edge Case
        # Edge Case A: When original weight was ~1.0
        if (1.0 - w_target_old) < 1e-9:
            # Original weight was 100%, others were 0
            # Can't scale zeros - just return with target at 1.0
            new_weights[:] = 0.0
            new_weights[perturbed_index] = 1.0
            return new_weights
        
        # 4. Calculate scaling factor using vectorization
        # Formula: w_j' = w_j * (remaining_new / remaining_old)
        remaining_space_new = 1.0 - w_target_new
        remaining_space_old = 1.0 - w_target_old
        scale_factor = remaining_space_new / remaining_space_old
        
        # 5. Apply scaling to ALL weights (vectorized operation)
        new_weights = weights * scale_factor
        
        # 6. Override the target weight to its specific new value
        # (Scaling would affect it too, so we force-set it)
        new_weights[perturbed_index] = w_target_new
        
        # 7. Final safeguard for floating point precision errors
        weight_sum = np.sum(new_weights)
        if abs(weight_sum - 1.0) > 1e-10:
            new_weights = new_weights / weight_sum
        
        return new_weights
    
    @staticmethod
    def weight_perturbation_analysis(
        decision_matrix: np.ndarray,
        base_weights: np.ndarray,
        is_benefit: np.ndarray,
        criterion_names: List[str],
        alternative_names: List[str],
        perturbation_range: float = 0.2,
        n_steps: int = 41,  # -20%, -19%, ..., 0%, ..., +19%, +20%
        top_n_alternatives: Optional[int] = None  # NEW: Limit displayed alternatives
    ) -> Dict:
        """
        Analyze sensitivity of rankings to weight changes
        
        Args:
            decision_matrix: Interval decision matrix (m, n, 2)
            base_weights: Original criterion weights (n,) from AHP
            is_benefit: Boolean array (n,)
            criterion_names: List of criterion names
            alternative_names: List of alternative names
            perturbation_range: ±% to perturb (0.2 = ±20%)
            n_steps: Number of perturbation points
            top_n_alternatives: If set, only analyze top N alternatives with most variation
                               (Edge Case B: Prevents "spaghetti chart" with 20+ lines)
            
        Returns:
            Dict with structure:
            {
                'criterion_name': {
                    'perturbations': [...],  # % values: [-20, -19, ..., 0, ..., 20]
                    'weights_at_perturbations': [...],  # Weight values at each step
                    'closeness_coefficients': np.array (m, n_steps),  # CC for each alt at each step
                    'rankings': [...],  # Ranking at each step
                    'rank_reversal_points': [...],  # Where rankings change
                    'critical_perturbation': float,  # First point where rank changes
                    'analyzed_alternatives': [...]  # Which alternatives are included in visualization
                }
            }
        """
        n_alternatives, n_criteria, _ = decision_matrix.shape
        
        # Generate perturbation points from -range to +range
        perturbations = np.linspace(-perturbation_range, perturbation_range, n_steps)
        
        # Edge Case B: Identify top N most variable alternatives
        # First, do a quick analysis to find which alternatives vary most
        if top_n_alternatives is not None and top_n_alternatives < n_alternatives:
            # Run quick analysis on first criterion to identify variable alternatives
            quick_CCs = np.zeros((n_alternatives, n_steps))
            for step_idx, perturbation_pct in enumerate(perturbations):
                delta = base_weights[0] * perturbation_pct
                perturbed_weights = SensitivityAnalysis.normalize_weights_after_perturbation(
                    base_weights, 0, delta
                )
                quick_CC, _ = IntervalTOPSIS.rank_alternatives(
                    decision_matrix, perturbed_weights, is_benefit
                )
                quick_CCs[:, step_idx] = quick_CC
            
            # Calculate variance for each alternative
            variances = np.var(quick_CCs, axis=1)
            # Get indices of top N most variable alternatives
            most_variable_indices = np.argsort(-variances)[:top_n_alternatives]
            analyzed_alternatives = sorted(most_variable_indices.tolist())
        else:
            analyzed_alternatives = list(range(n_alternatives))
        
        results = {}
        
        # Perturb each criterion one at a time
        for crit_idx, crit_name in enumerate(criterion_names):
            crit_results = {
                'perturbations': (perturbations * 100).tolist(),  # Convert to %
                'weights_at_perturbations': [],
                'closeness_coefficients': np.zeros((n_alternatives, n_steps)),
                'rankings': [],
                'rank_reversal_points': [],
                'critical_perturbation': None,
                'analyzed_alternatives': analyzed_alternatives  # For UI filtering
            }
            
            base_ranking = None
            
            # Test each perturbation level
            for step_idx, perturbation_pct in enumerate(perturbations):
                # Calculate absolute delta
                delta = base_weights[crit_idx] * perturbation_pct
                
                # Get normalized weights
                perturbed_weights = SensitivityAnalysis.normalize_weights_after_perturbation(
                    base_weights, crit_idx, delta
                )
                
                crit_results['weights_at_perturbations'].append(perturbed_weights[crit_idx])
                
                # Run TOPSIS with perturbed weights
                CC, _ = IntervalTOPSIS.rank_alternatives(
                    decision_matrix, 
                    perturbed_weights, 
                    is_benefit
                )
                
                crit_results['closeness_coefficients'][:, step_idx] = CC
                
                # Get ranking (argsort in descending order)
                ranking = np.argsort(-CC).tolist()
                crit_results['rankings'].append(ranking)
                
                # Detect rank reversal
                if base_ranking is None and abs(perturbation_pct) < 1e-6:
                    # This is the base (0% perturbation)
                    base_ranking = ranking
                elif base_ranking is not None:
                    if ranking != base_ranking:
                        # Rank reversal detected
                        if crit_results['critical_perturbation'] is None:
                            crit_results['critical_perturbation'] = perturbation_pct * 100
                        
                        crit_results['rank_reversal_points'].append({
                            'perturbation_pct': perturbation_pct * 100,
                            'new_ranking': ranking,
                            'changes': SensitivityAnalysis._detect_ranking_changes(
                                base_ranking, ranking, alternative_names
                            )
                        })
            
            results[crit_name] = crit_results
        
        # Calculate overall stability index
        results['stability_index'] = SensitivityAnalysis._calculate_stability_index(results)
        
        return results
    
    @staticmethod
    def _detect_ranking_changes(
        base_ranking: List[int], 
        new_ranking: List[int],
        alternative_names: List[str]
    ) -> List[str]:
        """
        Identify which alternatives switched positions
        
        Returns:
            List of human-readable change descriptions
        """
        changes = []
        for i, (base_pos, new_pos) in enumerate(zip(base_ranking, new_ranking)):
            if base_pos != new_pos:
                base_rank = base_ranking.index(i) + 1
                new_rank = new_ranking.index(i) + 1
                if new_rank < base_rank:
                    changes.append(
                        f"{alternative_names[i]}: Rank {base_rank} → {new_rank} (↑)"
                    )
                else:
                    changes.append(
                        f"{alternative_names[i]}: Rank {base_rank} → {new_rank} (↓)"
                    )
        return changes
    
    @staticmethod
    def _calculate_stability_index(results: Dict) -> float:
        """
        Calculate overall stability index (0-1, higher = more stable)
        
        Based on proportion of criteria that cause rank reversals
        and magnitude of reversals
        """
        n_criteria = len([k for k in results.keys() if k != 'stability_index'])
        
        unstable_count = 0
        for crit_name, crit_data in results.items():
            if crit_name == 'stability_index':
                continue
            if len(crit_data['rank_reversal_points']) > 0:
                unstable_count += 1
        
        # Simple metric: % of stable criteria
        stability = 1.0 - (unstable_count / n_criteria)
        
        return stability
    
    @staticmethod
    def monte_carlo_simulation(
        decision_matrix: np.ndarray,
        base_weights: np.ndarray,
        is_benefit: np.ndarray,
        n_iterations: int = 1000,
        perturbation_std: float = 0.05
    ) -> Dict:
        """
        Monte Carlo simulation for robustness analysis
        
        Randomly perturb ALL weights simultaneously (using Dirichlet distribution)
        and measure ranking stability
        
        Args:
            decision_matrix: Interval decision matrix (m, n, 2)
            base_weights: Original weights (n,)
            is_benefit: Boolean array (n,)
            n_iterations: Number of random samples
            perturbation_std: Standard deviation for perturbation
            
        Returns:
            {
                'ranking_frequencies': np.array,  # How often each ranking occurred
                'most_common_ranking': List[int],
                'ranking_probability': float,  # Prob of most common ranking
                'alternative_rank_distributions': Dict  # Rank distribution per alt
            }
        """
        n_alternatives, n_criteria, _ = decision_matrix.shape
        
        # Store all rankings
        all_rankings = []
        
        # Run Monte Carlo iterations
        for _ in range(n_iterations):
            # Perturb weights using Dirichlet distribution
            # Dirichlet ensures weights sum to 1 and all are positive
            concentration = base_weights / perturbation_std
            perturbed_weights = np.random.dirichlet(concentration)
            
            # Run TOPSIS
            CC, _ = IntervalTOPSIS.rank_alternatives(
                decision_matrix, 
                perturbed_weights, 
                is_benefit
            )
            
            # Get ranking
            ranking = tuple(np.argsort(-CC).tolist())
            all_rankings.append(ranking)
        
        # Count ranking frequencies
        from collections import Counter
        ranking_counts = Counter(all_rankings)
        most_common_ranking, frequency = ranking_counts.most_common(1)[0]
        
        # Calculate rank distribution for each alternative
        rank_distributions = {}
        for alt_idx in range(n_alternatives):
            ranks = [ranking.index(alt_idx) + 1 for ranking in all_rankings]
            rank_distributions[alt_idx] = {
                'mean_rank': np.mean(ranks),
                'std_rank': np.std(ranks),
                'rank_histogram': np.bincount(ranks)[1:]  # 1-indexed
            }
        
        return {
            'ranking_frequencies': dict(ranking_counts),
            'most_common_ranking': list(most_common_ranking),
            'ranking_probability': frequency / n_iterations,
            'alternative_rank_distributions': rank_distributions,
            'n_iterations': n_iterations
        }


# ============================================================================
# TESTING & VALIDATION
# ============================================================================

def test_normalization():
    """Test weight normalization logic"""
    print("=" * 60)
    print("Testing Weight Normalization")
    print("=" * 60)
    
    # Test case 1: Basic perturbation
    weights = np.array([0.5, 0.3, 0.2])
    print(f"\nOriginal weights: {weights}")
    print(f"Sum: {np.sum(weights):.10f}")
    
    # Increase first weight by 0.1 (from 0.5 to 0.6)
    new_weights = SensitivityAnalysis.normalize_weights_after_perturbation(
        weights, 0, 0.1
    )
    print(f"\nAfter +0.1 to w[0]: {new_weights}")
    print(f"Sum: {np.sum(new_weights):.10f}")
    print(f"Expected: [0.6, 0.24, 0.16]")
    
    # Test case 2: Negative perturbation
    new_weights = SensitivityAnalysis.normalize_weights_after_perturbation(
        weights, 1, -0.1
    )
    print(f"\nAfter -0.1 to w[1]: {new_weights}")
    print(f"Sum: {np.sum(new_weights):.10f}")
    
    # Test case 3: Edge case - weight becomes ~1.0
    weights = np.array([0.8, 0.15, 0.05])
    new_weights = SensitivityAnalysis.normalize_weights_after_perturbation(
        weights, 0, 0.15
    )
    print(f"\nOriginal: {weights}")
    print(f"After +0.15 to w[0]: {new_weights}")
    print(f"Sum: {np.sum(new_weights):.10f}")
    

def test_perturbation_analysis():
    """Test full perturbation analysis"""
    print("\n" + "=" * 60)
    print("Testing Perturbation Analysis")
    print("=" * 60)
    
    # Create sample data
    decision_matrix = np.array([
        [[7, 9], [5, 7], [3, 5]],  # Supplier A
        [[5, 7], [7, 9], [5, 7]],  # Supplier B
        [[3, 5], [5, 7], [7, 9]],  # Supplier C
    ])
    
    weights = np.array([0.5, 0.3, 0.2])  # Price, Quality, Delivery
    is_benefit = np.array([False, True, True])
    
    criterion_names = ["Price (Cost)", "Quality", "Delivery Time"]
    alternative_names = ["Supplier A", "Supplier B", "Supplier C"]
    
    results = SensitivityAnalysis.weight_perturbation_analysis(
        decision_matrix,
        weights,
        is_benefit,
        criterion_names,
        alternative_names,
        perturbation_range=0.3,  # ±30%
        n_steps=21
    )
    
    # Display results
    for crit_name, crit_data in results.items():
        if crit_name == 'stability_index':
            continue
            
        print(f"\n{crit_name}:")
        print(f"  Critical perturbation: {crit_data['critical_perturbation']}")
        print(f"  Rank reversals: {len(crit_data['rank_reversal_points'])}")
        
        if crit_data['rank_reversal_points']:
            print(f"  First reversal at: {crit_data['rank_reversal_points'][0]['perturbation_pct']:.1f}%")
    
    print(f"\nOverall Stability Index: {results['stability_index']:.2f}")


if __name__ == "__main__":
    test_normalization()
    test_perturbation_analysis()
