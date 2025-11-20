"""
Hierarchical Fuzzy AHP Module
Extends Fuzzy AHP to handle hierarchical criteria with global weight calculation
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from algorithms.fuzzy_ahp import FuzzyAHP


class HierarchicalFuzzyAHP:
    """Handles hierarchical AHP with global weight calculation"""
    
    @staticmethod
    def calculate_hierarchical_weights(criteria_hierarchy: List[Dict], 
                                      comparisons_by_group: Dict[str, List]) -> Tuple[Dict[int, float], Dict[str, Dict]]:
        """
        Calculate global weights for hierarchical criteria structure
        
        Args:
            criteria_hierarchy: List of criteria with hierarchy info
            comparisons_by_group: Dictionary mapping group keys to comparison data
            
        Returns:
            Tuple of:
            - Dictionary mapping criterion_id to global_weight
            - Dictionary mapping group_key to consistency info {'cr', 'ci', 'lambda_max'}
        """
        global_weights = {}
        consistency_info = {}
        
        # Step 1: Calculate weights for main criteria (level 0)
        main_criteria = [c for c in criteria_hierarchy if c['parent_id'] is None]
        
        if 'main' in comparisons_by_group and comparisons_by_group['main']:
            # Calculate local weights for main criteria
            main_weights, metrics = HierarchicalFuzzyAHP._calculate_group_weights(
                comparisons_by_group['main'],
                len(main_criteria)
            )
            consistency_info['main'] = metrics
            
            # Assign global weights (same as local for main criteria)
            for i, criterion in enumerate(main_criteria):
                global_weights[criterion['id']] = main_weights[i]
        else:
            # Equal weights if no comparisons
            equal_weight = 1.0 / len(main_criteria) if main_criteria else 0
            for criterion in main_criteria:
                global_weights[criterion['id']] = equal_weight
        
        # Step 2: Calculate weights for sub-criteria
        for main_criterion in main_criteria:
            main_id = main_criterion['id']
            main_weight = global_weights.get(main_id, 0)
            
            # Find sub-criteria of this main criterion
            sub_criteria = [c for c in criteria_hierarchy if c['parent_id'] == main_id]
            
            if not sub_criteria:
                continue
            
            group_key = f'sub_{main_id}'
            
            if group_key in comparisons_by_group and comparisons_by_group[group_key]:
                # Calculate local weights for sub-criteria
                sub_weights, metrics = HierarchicalFuzzyAHP._calculate_group_weights(
                    comparisons_by_group[group_key],
                    len(sub_criteria)
                )
                consistency_info[group_key] = metrics
                
                # Calculate global weights: W_global = W_local × W_parent
                for i, sub_criterion in enumerate(sub_criteria):
                    global_weights[sub_criterion['id']] = sub_weights[i] * main_weight
            else:
                # Equal distribution if no comparisons
                equal_weight = main_weight / len(sub_criteria)
                for sub_criterion in sub_criteria:
                    global_weights[sub_criterion['id']] = equal_weight
        
        # Normalize to ensure sum = 1.0 (for leaf criteria only)
        leaf_criteria_ids = HierarchicalFuzzyAHP._get_leaf_criteria_ids(criteria_hierarchy)
        leaf_weights_sum = sum(global_weights.get(cid, 0) for cid in leaf_criteria_ids)
        
        if leaf_weights_sum > 0:
            for cid in leaf_criteria_ids:
                if cid in global_weights:
                    global_weights[cid] = global_weights[cid] / leaf_weights_sum
        
        return global_weights, consistency_info
    
    
    @staticmethod
    def _calculate_group_weights(fuzzy_matrices: List[np.ndarray], n_criteria: int, expert_weights: Optional[List[float]] = None) -> Tuple[np.ndarray, Dict]:
        """
        Calculate weights for a group of criteria using Fuzzy AHP
        
        Args:
            fuzzy_matrices: List of fuzzy comparison matrices from experts
            n_criteria: Number of criteria in this group
            expert_weights: Optional list of expert weights
            
        Returns:
            Tuple of (crisp_weights, metrics_dict)
        """
        if not fuzzy_matrices:
            # Equal weights if no data
            return np.ones(n_criteria) / n_criteria, {}
        
        # Use weighted Fuzzy AHP calculation
        crisp_weights, _, cr, ci, lambda_max = FuzzyAHP.calculate_weights(fuzzy_matrices, expert_weights)
        
        metrics = {
            'cr': cr,
            'ci': ci,
            'lambda_max': lambda_max,
            'matrix': fuzzy_matrices[0] if fuzzy_matrices else None # Store a matrix for analysis if needed
        }
        
        return crisp_weights, metrics
    
    @staticmethod
    def _get_leaf_criteria_ids(criteria_hierarchy: List[Dict]) -> List[int]:
        """
        Get IDs of leaf criteria (criteria without children)
        
        Args:
            criteria_hierarchy: List of criteria with hierarchy info
            
        Returns:
            List of criterion IDs that are leaves
        """
        all_ids = set(c['id'] for c in criteria_hierarchy)
        parent_ids = set(c['parent_id'] for c in criteria_hierarchy if c['parent_id'] is not None)
        
        # Leaf criteria are those that are not parents
        leaf_ids = list(all_ids - parent_ids)
        return leaf_ids
    
    @staticmethod
    def organize_comparisons_by_group(all_comparisons: List[Dict], 
                                     criteria_hierarchy: List[Dict]) -> Dict[str, List[np.ndarray]]:
        """
        Organize comparisons into groups based on hierarchy
        
        Args:
            all_comparisons: All pairwise comparisons from database
            criteria_hierarchy: Criteria hierarchy information
            
        Returns:
            Dictionary mapping group keys to lists of fuzzy matrices
        """
        # Create mapping of criterion_id to its info
        criteria_map = {c['id']: c for c in criteria_hierarchy}
        
        # Group comparisons by expert and by hierarchy level
        comparisons_by_expert_and_group = {}
        
        for comp in all_comparisons:
            expert_id = comp['expert_id']
            c1_id = comp['criterion1_id']
            c2_id = comp['criterion2_id']
            
            # Determine which group this comparison belongs to
            if c1_id in criteria_map and c2_id in criteria_map:
                c1_parent = criteria_map[c1_id].get('parent_id')
                c2_parent = criteria_map[c2_id].get('parent_id')
                
                # Both should have same parent for valid comparison
                if c1_parent == c2_parent:
                    if c1_parent is None:
                        group_key = 'main'
                    else:
                        group_key = f'sub_{c1_parent}'
                    
                    key = (expert_id, group_key)
                    if key not in comparisons_by_expert_and_group:
                        comparisons_by_expert_and_group[key] = []
                    
                    comparisons_by_expert_and_group[key].append(comp)
        
        # Convert to fuzzy matrices by group
        result = {}
        
        # Get unique groups
        groups = set(group_key for (_, group_key) in comparisons_by_expert_and_group.keys())
        
        for group_key in groups:
            # Get all experts for this group
            experts_in_group = set(expert_id for (expert_id, gk) in comparisons_by_expert_and_group.keys() 
                                  if gk == group_key)
            
            matrices = []
            for expert_id in experts_in_group:
                key = (expert_id, group_key)
                if key in comparisons_by_expert_and_group:
                    comps = comparisons_by_expert_and_group[key]
                    
                    # Determine number of criteria in this group
                    if group_key == 'main':
                        n_criteria = len([c for c in criteria_hierarchy if c['parent_id'] is None])
                        criteria_ids = [c['id'] for c in criteria_hierarchy if c['parent_id'] is None]
                    else:
                        parent_id = int(group_key.split('_')[1])
                        n_criteria = len([c for c in criteria_hierarchy if c['parent_id'] == parent_id])
                        criteria_ids = [c['id'] for c in criteria_hierarchy if c['parent_id'] == parent_id]
                    
                    # Create fuzzy matrix
                    matrix = FuzzyAHP.create_fuzzy_matrix_from_comparisons(
                        n_criteria, comps, criteria_ids
                    )
                    matrices.append(matrix)
            
            if matrices:
                result[group_key] = matrices
        
        return result
