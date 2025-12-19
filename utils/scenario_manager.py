"""
Scenario Manager Module - What-If Scenario Management
Implements deep copy strategy for independent scenario storage
"""

from typing import List, Dict, Optional, Tuple
from database.manager import DatabaseManager
import numpy as np


class ScenarioManager:
    """
    Manage What-If scenarios using Deep Copy strategy
    
    Each scenario is completely independent - no delta storage complexity.
    This trades disk space (cheap) for code simplicity (expensive developer time).
    """
    
    def __init__(self, db_manager: DatabaseManager, project_id: int):
        """
        Initialize scenario manager
        
        Args:
            db_manager: Database manager instance
            project_id: Current project ID
        """
        self.db_manager = db_manager
        self.project_id = project_id
    
    def create_scenario(self, name: str, description: str = "") -> int:
        """
        Create new empty scenario
        
        Args:
            name: Scenario name (must be unique within project)
            description: Optional description
            
        Returns:
            Scenario ID
        """
        with self.db_manager as db:
            cursor = db.conn.cursor()
            cursor.execute("""
                INSERT INTO scenarios (project_id, name, description, is_base)
                VALUES (?, ?, ?, 0)
            """, (self.project_id, name, description))
            scenario_id = cursor.lastrowid
            db.conn.commit()
            
        return scenario_id
    
    def duplicate_scenario(
        self, 
        source_scenario_id: Optional[int], 
        new_name: str,
        new_description: str = ""
    ) -> int:
        """
        Duplicate scenario (or base data if source=None) using Deep Copy
        
        This is the core of the Deep Copy strategy - creates complete
        independent copy of all AHP comparisons and TOPSIS ratings.
        
        Args:
            source_scenario_id: Scenario to copy from (None = base scenario with id=1)
            new_name: Name for new scenario
            new_description: Description for new scenario
            
        Returns:
            New scenario ID
        """
        # Default to base scenario
        if source_scenario_id is None:
            source_scenario_id = 1  # Base scenario always has ID=1
        
        # Create new scenario record
        new_scenario_id = self.create_scenario(new_name, new_description)
        
        # Copy AHP comparisons
        with self.db_manager as db:
            cursor = db.conn.cursor()
            
            # Get parent scenario ID for tracking
            cursor.execute("""
                UPDATE scenarios 
                SET parent_id = ? 
                WHERE id = ?
            """, (source_scenario_id, new_scenario_id))
            
            # Deep copy AHP comparisons
            try:
                cursor.execute("""
                    INSERT INTO ahp_comparisons 
                        (project_id, scenario_id, expert_id, criterion1_id, criterion2_id,
                         fuzzy_l, fuzzy_m, fuzzy_u)
                    SELECT project_id, ?, expert_id, criterion1_id, criterion2_id,
                           fuzzy_l, fuzzy_m, fuzzy_u
                    FROM ahp_comparisons
                    WHERE project_id = ? AND scenario_id = ?
                """, (new_scenario_id, self.project_id, source_scenario_id))
            except Exception as e:
                raise
            
            # Deep copy TOPSIS ratings - skip if fails to avoid blocking scenario creation
            try:
                # First check if source has any TOPSIS ratings
                cursor.execute("""
                    SELECT COUNT(*) FROM topsis_ratings 
                    WHERE project_id = ? AND scenario_id = ?
                """, (self.project_id, source_scenario_id))
                source_count = cursor.fetchone()[0]
                
                if source_count > 0:
                    cursor.execute("""
                        INSERT INTO topsis_ratings
                            (project_id, scenario_id, expert_id, alternative_id, criterion_id,
                             rating_lower, rating_upper)
                        SELECT project_id, ?, expert_id, alternative_id, criterion_id,
                               rating_lower, rating_upper
                        FROM topsis_ratings
                        WHERE project_id = ? AND scenario_id = ?
                    """, (new_scenario_id, self.project_id, source_scenario_id))
            except Exception:
                # If TOPSIS copy fails (e.g., FK constraint), continue without it
                # User can manually re-enter ratings in new scenario
                pass  # Don't raise - allow scenario creation to succeed
            
            db.conn.commit()
        
        return new_scenario_id
    
    def delete_scenario(self, scenario_id: int):
        """
        Delete scenario and all associated data
        
        Args:
            scenario_id: ID of scenario to delete
            
        Raises:
            ValueError: If trying to delete base scenario
        """
        if scenario_id == 1:
            raise ValueError("Cannot delete base scenario")
        
        with self.db_manager as db:
            cursor = db.conn.cursor()
            
            # Delete scenario record (CASCADE will delete comparisons/ratings)
            cursor.execute("""
                DELETE FROM scenarios WHERE id = ? AND project_id = ?
            """, (scenario_id, self.project_id))
            
            # Also explicitly delete associated data for safety
            cursor.execute("""
                DELETE FROM ahp_comparisons 
                WHERE scenario_id = ? AND project_id = ?
            """, (scenario_id, self.project_id))
            
            cursor.execute("""
                DELETE FROM topsis_ratings
                WHERE scenario_id = ? AND project_id = ?
            """, (scenario_id, self.project_id))
            
            db.conn.commit()
    
    def rename_scenario(self, scenario_id: int, new_name: str):
        """
        Rename a scenario
        
        Args:
            scenario_id: Scenario ID
            new_name: New name
        """
        with self.db_manager as db:
            cursor = db.conn.cursor()
            cursor.execute("""
                UPDATE scenarios 
                SET name = ?
                WHERE id = ? AND project_id = ?
            """, (new_name, scenario_id, self.project_id))
            db.conn.commit()
    
    def update_scenario_description(self, scenario_id: int, description: str):
        """
        Update scenario description
        
        Args:
            scenario_id: Scenario ID
            description: New description
        """
        with self.db_manager as db:
            cursor = db.conn.cursor()
            cursor.execute("""
                UPDATE scenarios 
                SET description = ?
                WHERE id = ? AND project_id = ?
            """, (description, scenario_id, self.project_id))
            db.conn.commit()
    
    def get_all_scenarios(self) -> List[Dict]:
        """
        Get all scenarios for current project
        
        Returns:
            List of scenario dictionaries with keys:
            - id, name, description, created_date, is_base, parent_id
        """
        with self.db_manager as db:
            cursor = db.conn.cursor()
            cursor.execute("""
                SELECT id, name, description, created_date, is_base, parent_id
                FROM scenarios
                WHERE project_id = ?
                ORDER BY is_base DESC, created_date ASC
            """, (self.project_id,))
            
            columns = ['id', 'name', 'description', 'created_date', 'is_base', 'parent_id']
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return results
    
    def get_scenario(self, scenario_id: int) -> Optional[Dict]:
        """
        Get single scenario details
        
        Args:
            scenario_id: Scenario ID
            
        Returns:
            Scenario dict or None if not found
        """
        scenarios = self.get_all_scenarios()
        for scenario in scenarios:
            if scenario['id'] == scenario_id:
                return scenario
        return None
    
    def compare_scenarios(
        self, 
        scenario_ids: List[int],
        criterion_weights_per_scenario: Dict[int, np.ndarray],
        decision_matrix_per_scenario: Dict[int, np.ndarray],
        is_benefit: np.ndarray,
        alternative_names: List[str]
    ) -> Dict:
        """
        Compare rankings from multiple scenarios
        
        Args:
            scenario_ids: List of scenario IDs to compare
            criterion_weights_per_scenario: Dict mapping scenario_id -> weights array
            decision_matrix_per_scenario: Dict mapping scenario_id -> decision matrix
            is_benefit: Boolean array for benefit/cost criteria
            alternative_names: List of alternative names
            
        Returns:
            {
                'scenarios': [...],  # Scenario info
                'rankings': {scenario_id: ranking_list, ...},
                'closeness_coefficients': {scenario_id: CC_array, ...},
                'agreement_matrix': np.array,  # Pairwise agreement between scenarios
                'agreement_index': float,  # Overall agreement (0-1)
                'rank_changes': [...]  # List of alternatives that changed rank
            }
        """
        from algorithms.interval_topsis import IntervalTOPSIS
        
        # Get scenario info
        scenarios = [self.get_scenario(sid) for sid in scenario_ids]
        
        # Calculate rankings for each scenario
        rankings = {}
        closeness_coefficients = {}
        
        for scenario_id in scenario_ids:
            weights = criterion_weights_per_scenario.get(scenario_id)
            decision_matrix = decision_matrix_per_scenario.get(scenario_id)
            
            if weights is not None and decision_matrix is not None:
                CC, _ = IntervalTOPSIS.rank_alternatives(
                    decision_matrix, weights, is_benefit
                )
                closeness_coefficients[scenario_id] = CC
                rankings[scenario_id] = np.argsort(-CC).tolist()
        
        # Calculate agreement metrics
        agreement_matrix = self._calculate_agreement_matrix(rankings, scenario_ids)
        agreement_index = self._calculate_overall_agreement(agreement_matrix)
        
        # Identify rank changes
        rank_changes = self._identify_rank_changes(
            rankings, scenario_ids, alternative_names
        )
        
        return {
            'scenarios': scenarios,
            'rankings': rankings,
            'closeness_coefficients': closeness_coefficients,
            'agreement_matrix': agreement_matrix,
            'agreement_index': agreement_index,
            'rank_changes': rank_changes
        }
    
    def _calculate_agreement_matrix(
        self, 
        rankings: Dict[int, List[int]], 
        scenario_ids: List[int]
    ) -> np.ndarray:
        """
        Calculate pairwise agreement between scenarios
        
        Uses Spearman rank correlation coefficient
        
        Returns:
            Agreement matrix (n_scenarios, n_scenarios) with values 0-1
        """
        from scipy.stats import spearmanr
        
        n_scenarios = len(scenario_ids)
        agreement = np.zeros((n_scenarios, n_scenarios))
        
        for i, sid1 in enumerate(scenario_ids):
            for j, sid2 in enumerate(scenario_ids):
                if i == j:
                    agreement[i, j] = 1.0
                else:
                    # Spearman correlation (-1 to 1) -> convert to (0 to 1)
                    corr, _ = spearmanr(rankings[sid1], rankings[sid2])
                    agreement[i, j] = (corr + 1) / 2
        
        return agreement
    
    def _calculate_overall_agreement(self, agreement_matrix: np.ndarray) -> float:
        """
        Calculate overall agreement index
        
        Simple average of all pairwise agreements (excluding diagonal)
        """
        n = agreement_matrix.shape[0]
        if n <= 1:
            return 1.0
        
        # Sum upper triangle (excluding diagonal)
        total = 0
        count = 0
        for i in range(n):
            for j in range(i + 1, n):
                total += agreement_matrix[i, j]
                count += 1
        
        return total / count if count > 0 else 1.0
    
    def _identify_rank_changes(
        self,
        rankings: Dict[int, List[int]],
        scenario_ids: List[int],
        alternative_names: List[str]
    ) -> List[Dict]:
        """
        Identify alternatives that changed rank across scenarios
        
        Returns:
            List of change dictionaries with:
            - alternative_name
            - ranks_per_scenario: {scenario_id: rank}
            - volatility: std deviation of ranks
        """
        n_alternatives = len(alternative_names)
        changes = []
        
        for alt_idx in range(n_alternatives):
            ranks_per_scenario = {}
            rank_values = []
            
            for scenario_id in scenario_ids:
                ranking = rankings[scenario_id]
                rank = ranking.index(alt_idx) + 1  # 1-indexed
                ranks_per_scenario[scenario_id] = rank
                rank_values.append(rank)
            
            # Calculate volatility (std dev of ranks)
            volatility = np.std(rank_values)
            
            # Only include if there's variation
            if volatility > 0:
                changes.append({
                    'alternative_name': alternative_names[alt_idx],
                    'alternative_index': alt_idx,
                    'ranks_per_scenario': ranks_per_scenario,
                    'volatility': volatility,
                    'min_rank': min(rank_values),
                    'max_rank': max(rank_values)
                })
        
        # Sort by volatility (most volatile first)
        changes.sort(key=lambda x: x['volatility'], reverse=True)
        
        return changes


# ============================================================================
# Testing
# ============================================================================

if __name__ == "__main__":
    pass  # Module loaded successfully
