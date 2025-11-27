from utils.undo_manager import Command
from typing import Optional, List, Dict, Any
import sqlite3

class AddComparisonCommand(Command):
    def __init__(self, db_manager, project_id: int, expert_id: int, 
                 c1_id: int, c2_id: int, l: float, m: float, u: float):
        self.db = db_manager
        self.project_id = project_id
        self.expert_id = expert_id
        self.c1_id = c1_id
        self.c2_id = c2_id
        self.l = l
        self.m = m
        self.u = u
        self.old_comparison = None
        
    def execute(self) -> bool:
        with self.db as database:
            # Check if comparison exists to save state
            cursor = database.conn.cursor()
            cursor.execute(
                "SELECT * FROM ahp_comparisons WHERE project_id=? AND expert_id=? AND criterion1_id=? AND criterion2_id=?",
                (self.project_id, self.expert_id, self.c1_id, self.c2_id)
            )
            row = cursor.fetchone()
            if row:
                self.old_comparison = dict(row)
            
            database.add_ahp_comparison(
                self.project_id, self.expert_id, self.c1_id, self.c2_id,
                self.l, self.m, self.u
            )
        return True
    
    def undo(self) -> bool:
        with self.db as database:
            if self.old_comparison:
                # Restore old value
                database.add_ahp_comparison(
                    self.project_id, self.expert_id, self.c1_id, self.c2_id,
                    self.old_comparison['fuzzy_l'], 
                    self.old_comparison['fuzzy_m'], 
                    self.old_comparison['fuzzy_u']
                )
            else:
                # Delete if it was new
                cursor = database.conn.cursor()
                cursor.execute(
                    "DELETE FROM ahp_comparisons WHERE project_id=? AND expert_id=? AND criterion1_id=? AND criterion2_id=?",
                    (self.project_id, self.expert_id, self.c1_id, self.c2_id)
                )
                database.conn.commit()
        return True
    
    def description(self) -> str:
        return "Update Comparison"

class ImportExpertCommand(Command):
    def __init__(self, db_manager, project_id: int, experts_data: List[Dict], comparisons_data: List[Dict], topsis_ratings_data: List[Dict] = None):
        self.db = db_manager
        self.project_id = project_id
        self.experts_data = experts_data # List of {name, weight, external_id}
        self.comparisons_data = comparisons_data # List of comparison dicts with mapped IDs
        self.topsis_ratings_data = topsis_ratings_data or [] # List of TOPSIS ratings to import
        self.imported_expert_ids = []
        
    def execute(self) -> bool:
        self.imported_expert_ids = []
        with self.db as database:
            # Map external ID to new local ID
            expert_id_map = {}
            
            for expert in self.experts_data:
                # Check name collision
                name = expert['name']
                # Logic to handle name collision should be passed in or handled here?
                # For simplicity, let's assume the name passed in is already resolved or we resolve it here
                # But wait, if we resolve it here, we need to know existing names.
                # Let's assume the caller handles name resolution and passes unique names if possible,
                # or we do simple check.
                
                # Actually, the command should probably receive the FINAL names to use.
                # But let's replicate the logic: check DB for existing names.
                cursor = database.conn.cursor()
                cursor.execute("SELECT name FROM experts WHERE project_id=?", (self.project_id,))
                existing_names = {row[0] for row in cursor.fetchall()}
                
                # Handle name collision with incremental suffix
                final_name = name
                if final_name in existing_names:
                    counter = 1
                    while f"{name} (Imported {counter})" in existing_names:
                        counter += 1
                    final_name = f"{name} (Imported {counter})"
                
                new_id = database.add_expert(self.project_id, final_name, weight=expert.get('weight'))
                self.imported_expert_ids.append(new_id)
                expert_id_map[expert['external_id']] = new_id
            
            # Import comparisons
            for comp in self.comparisons_data:
                ext_expert_id = comp['external_expert_id']
                if ext_expert_id in expert_id_map:
                    new_expert_id = expert_id_map[ext_expert_id]
                    database.add_ahp_comparison(
                        self.project_id, new_expert_id,
                        comp['c1_id'], comp['c2_id'],
                        comp['l'], comp['m'], comp['u']
                    )
            
            # Import TOPSIS ratings with error handling
            topsis_import_count = 0
            topsis_skip_count = 0
            
            for rating in self.topsis_ratings_data:
                ext_expert_id = rating['external_expert_id']
                if ext_expert_id in expert_id_map:
                    new_expert_id = expert_id_map[ext_expert_id]
                    try:
                        database.add_topsis_rating(
                            project_id=self.project_id,
                            alternative_id=rating['alternative_id'],
                            criterion_id=rating['criterion_id'],
                            rating_lower=rating['rating_lower'],
                            rating_upper=rating['rating_upper'],
                            expert_id=new_expert_id,
                            scenario_id=rating.get('scenario_id', 1)
                        )
                        topsis_import_count += 1
                    except Exception as e:
                        # Skip invalid TOPSIS ratings (e.g., foreign key mismatch)
                        topsis_skip_count += 1
                        print(f"[Import] Skipped TOPSIS rating: {e}")
            
            # Store counts for user feedback
            self.topsis_import_count = topsis_import_count
            self.topsis_skip_count = topsis_skip_count
        return True
    
    def undo(self) -> bool:
        with self.db as database:
            cursor = database.conn.cursor()
            for expert_id in self.imported_expert_ids:
                # Delete AHP comparisons
                database.delete_ahp_comparisons_by_expert(expert_id)
                # Delete TOPSIS ratings
                cursor.execute(
                    "DELETE FROM topsis_ratings WHERE project_id=? AND expert_id=?",
                    (self.project_id, expert_id)
                )
                database.conn.commit()
                # Delete expert
                database.delete_expert(expert_id)
        return True
    
    def description(self) -> str:
        return f"Import {len(self.experts_data)} Experts"

class BatchSaveComparisonsCommand(Command):
    def __init__(self, db_manager, project_id: int, expert_id: int, comparisons: List[Dict]):
        self.db = db_manager
        self.project_id = project_id
        self.expert_id = expert_id
        self.comparisons = comparisons # List of {c1_id, c2_id, l, m, u}
        self.old_comparisons = {} # Map (c1, c2) -> {l, m, u}
        
    def execute(self) -> bool:
        with self.db as database:
            cursor = database.conn.cursor()
            
            # Save old state for all comparisons being updated
            for comp in self.comparisons:
                c1, c2 = comp['c1_id'], comp['c2_id']
                cursor.execute(
                    "SELECT * FROM ahp_comparisons WHERE project_id=? AND expert_id=? AND criterion1_id=? AND criterion2_id=?",
                    (self.project_id, self.expert_id, c1, c2)
                )
                row = cursor.fetchone()
                if row:
                    self.old_comparisons[(c1, c2)] = dict(row)
            
            # Update/Insert new comparisons
            for comp in self.comparisons:
                database.add_ahp_comparison(
                    self.project_id, self.expert_id, 
                    comp['c1_id'], comp['c2_id'],
                    comp['l'], comp['m'], comp['u']
                )
        return True
    
    def undo(self) -> bool:
        with self.db as database:
            cursor = database.conn.cursor()
            
            for comp in self.comparisons:
                c1, c2 = comp['c1_id'], comp['c2_id']
                
                if (c1, c2) in self.old_comparisons:
                    # Restore old
                    old = self.old_comparisons[(c1, c2)]
                    database.add_ahp_comparison(
                        self.project_id, self.expert_id, c1, c2,
                        old['fuzzy_l'], old['fuzzy_m'], old['fuzzy_u']
                    )
                else:
                    # Delete new
                    cursor.execute(
                        "DELETE FROM ahp_comparisons WHERE project_id=? AND expert_id=? AND criterion1_id=? AND criterion2_id=?",
                        (self.project_id, self.expert_id, c1, c2)
                    )
            database.conn.commit()
        return True
    
    def description(self) -> str:
        return f"Save {len(self.comparisons)} Comparisons"
