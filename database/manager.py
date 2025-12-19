"""
Database Manager Module
Handles all database operations and CRUD functionality
"""

import sqlite3
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime


class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, db_path: str):
        """
        Initialize database manager
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        """Establish database connection (reuses existing if already connected)"""
        if self.conn is not None:
            # Already connected, reuse existing connection
            return
        
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        self.conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        
        # Auto-migrate if needed
        self._check_and_migrate()
    
    def _check_and_migrate(self):
        """Check and auto-migrate database schema if needed"""
        cursor = self.conn.cursor()
        
        try:
            # ============================================================
            # Migration 1: Add expert_id to topsis_ratings (legacy)
            # ============================================================
            cursor.execute("PRAGMA table_info(topsis_ratings)")
            columns = [info[1] for info in cursor.fetchall()]
            
            if 'expert_id' not in columns:
                print(f"Auto-migrating database: {self.db_path}")
                print("  Adding expert_id column to topsis_ratings...")
                cursor.execute("ALTER TABLE topsis_ratings ADD COLUMN expert_id INTEGER")
                self.conn.commit()
                print("  Migration complete!")
            
            # ============================================================
            # Migration 2: Add weight to experts (legacy)
            # ============================================================
            cursor.execute("PRAGMA table_info(experts)")
            expert_columns = [info[1] for info in cursor.fetchall()]
            
            if 'weight' not in expert_columns:
                print(f"Auto-migrating database: {self.db_path}")
                print("  Adding weight column to experts...")
                cursor.execute("ALTER TABLE experts ADD COLUMN weight REAL DEFAULT NULL")
                self.conn.commit()
                print("  Experts migration complete!")
            
            # ============================================================
            # Migration 3: Fix UNIQUE constraint for expert_id (legacy)
            # ============================================================
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='topsis_ratings'")
            result = cursor.fetchone()
            
            # If constraint doesn't include expert_id, we need to recreate the table
            if result and "UNIQUE(project_id, alternative_id, criterion_id, expert_id)" not in result[0]:
                print("  Fixing UNIQUE constraint...")
                
                cursor.execute("BEGIN TRANSACTION")
                
                # Rename old table
                cursor.execute("ALTER TABLE topsis_ratings RENAME TO topsis_ratings_old")
                
                # Create new table WITH scenario_id support
                cursor.execute("""
                    CREATE TABLE topsis_ratings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        project_id INTEGER NOT NULL,
                        scenario_id INTEGER NOT NULL DEFAULT 1,
                        expert_id INTEGER,
                        alternative_id INTEGER NOT NULL,
                        criterion_id INTEGER NOT NULL,
                        rating_lower REAL NOT NULL,
                        rating_upper REAL NOT NULL,
                        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                        FOREIGN KEY (scenario_id) REFERENCES scenarios(id) ON DELETE CASCADE,
                        FOREIGN KEY (expert_id) REFERENCES experts(id) ON DELETE CASCADE,
                        FOREIGN KEY (alternative_id) REFERENCES alternatives(id) ON DELETE CASCADE,
                        FOREIGN KEY (criterion_id) REFERENCES criteria(id) ON DELETE CASCADE,
                        UNIQUE(project_id, alternative_id, criterion_id, expert_id)
                    )
                """)
                
                # Copy data
                cursor.execute("PRAGMA table_info(topsis_ratings_old)")
                old_cols = [info[1] for info in cursor.fetchall()]
                
                # Check if old table has scenario_id already
                if 'scenario_id' in old_cols:
                    # Old table already has scenario_id
                    if 'expert_id' in old_cols:
                        cursor.execute("""
                            INSERT INTO topsis_ratings 
                            (id, project_id, scenario_id, expert_id, alternative_id, criterion_id, rating_lower, rating_upper)
                            SELECT id, project_id, scenario_id, expert_id, alternative_id, criterion_id, rating_lower, rating_upper
                            FROM topsis_ratings_old
                        """)
                    else:
                        cursor.execute("""
                            INSERT INTO topsis_ratings 
                            (id, project_id, scenario_id, alternative_id, criterion_id, rating_lower, rating_upper)
                            SELECT id, project_id, scenario_id, alternative_id, criterion_id, rating_lower, rating_upper
                            FROM topsis_ratings_old
                        """)
                else:
                    # Old table doesn't have scenario_id, default to 1 (base scenario)
                    if 'expert_id' in old_cols:
                        cursor.execute("""
                            INSERT INTO topsis_ratings 
                            (id, project_id, scenario_id, expert_id, alternative_id, criterion_id, rating_lower, rating_upper)
                            SELECT id, project_id, 1, expert_id, alternative_id, criterion_id, rating_lower, rating_upper
                            FROM topsis_ratings_old
                        """)
                    else:
                        cursor.execute("""
                            INSERT INTO topsis_ratings 
                            (id, project_id, scenario_id, alternative_id, criterion_id, rating_lower, rating_upper)
                            SELECT id, project_id, 1, alternative_id, criterion_id, rating_lower, rating_upper
                            FROM topsis_ratings_old
                        """)
                
                cursor.execute("DROP TABLE topsis_ratings_old")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_topsis_project ON topsis_ratings(project_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_topsis_scenario ON topsis_ratings(scenario_id)")
                
                self.conn.commit()
                print("  UNIQUE constraint fixed!")
            
            # ============================================================
            # Migration 4: Scenarios Feature (NEW)
            # ============================================================
            # Check if scenarios table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='scenarios'
            """)
            
            if cursor.fetchone() is None:
                # Scenarios migration needed
                print(f"[Scenarios Migration] Detected old schema version")
                print(f"[Scenarios Migration] Running migration for: {self.db_path}")
                
                try:
                    # Import and run migration
                    from database.database_migration import migrate_to_scenarios
                    
                    # Close current connection temporarily
                    self.conn.close()
                    
                    # Run migration
                    migrate_to_scenarios(self.db_path)
                    
                    # Reconnect
                    self.conn = sqlite3.connect(self.db_path)
                    self.conn.row_factory = sqlite3.Row
                    self.conn.execute("PRAGMA foreign_keys = ON")
                    
                    print("[Scenarios Migration] ✓ Migration completed!")
                    
                except Exception as migration_error:
                    print(f"[Scenarios Migration] ✗ Migration failed: {migration_error}")
                    print("[Scenarios Migration] Please run 'python run_migration.py' manually")
                    
                    # Reconnect even if migration failed
                    self.conn = sqlite3.connect(self.db_path)
                    self.conn.row_factory = sqlite3.Row
                    self.conn.execute("PRAGMA foreign_keys = ON")
                    
                    raise Exception(
                        f"Database migration failed. Please run 'python run_migration.py' "
                        f"to manually migrate your database file. Error: {migration_error}"
                    )
                
        except Exception as e:
            print(f"Migration error (non-fatal): {e}")
            self.conn.rollback()
    
    def disconnect(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
        self._ref_count = 0
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        self._ref_count = getattr(self, '_ref_count', 0) + 1
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self._ref_count = getattr(self, '_ref_count', 1) - 1
        # Only disconnect if this is the outermost context
        if self._ref_count <= 0:
            self.disconnect()
    
    # ==================== Project Operations ====================
    
    def get_project(self) -> Optional[Dict[str, Any]]:
        """Get project information (assumes single project per file)"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM projects LIMIT 1")
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def update_project(self, name: str, description: str) -> None:
        """Update project information"""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE projects SET name = ?, description = ?, modified_date = CURRENT_TIMESTAMP WHERE id = 1",
            (name, description)
        )
        self.conn.commit()
    
    # ==================== Criteria Operations ====================
    
    def add_criterion(self, project_id: int, name: str, parent_id: Optional[int] = None, 
                     is_benefit: bool = True) -> int:
        """Add a new criterion"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO criteria (project_id, name, parent_id, is_benefit) VALUES (?, ?, ?, ?)",
            (project_id, name, parent_id, is_benefit)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_criteria(self, project_id: int) -> List[Dict[str, Any]]:
        """Get all criteria for a project"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM criteria WHERE project_id = ? ORDER BY id", (project_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def update_criterion(self, criterion_id: int, name: str, parent_id: Optional[int] = None,
                        is_benefit: bool = True) -> None:
        """Update a criterion"""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE criteria SET name = ?, parent_id = ?, is_benefit = ? WHERE id = ?",
            (name, parent_id, is_benefit, criterion_id)
        )
        self.conn.commit()
    
    def delete_criterion(self, criterion_id: int) -> None:
        """Delete a criterion"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM criteria WHERE id = ?", (criterion_id,))
        self.conn.commit()
    
    def update_criterion_weight(self, criterion_id: int, weight: float) -> None:
        """Update criterion weight (from AHP calculation)"""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE criteria SET weight = ? WHERE id = ?", (weight, criterion_id))
        self.conn.commit()
    
    def get_leaf_criteria(self, project_id: int) -> List[Dict[str, Any]]:
        """
        Get only leaf criteria (criteria without children) for a project
        
        Leaf criteria are those that have no sub-criteria underneath them.
        These are the criteria that should be used in TOPSIS rating matrix
        to avoid double counting (parent criteria weights are already 
        incorporated into leaf criteria through hierarchical AHP).
        
        Returns:
            List of leaf criteria with full information (id, name, weight, is_benefit, etc.)
        """
        cursor = self.conn.cursor()
        
        # Get all criteria
        cursor.execute("SELECT * FROM criteria WHERE project_id = ? ORDER BY id", (project_id,))
        all_criteria = [dict(row) for row in cursor.fetchall()]
        
        # Find all criteria IDs that are parents (have children)
        parent_ids = set()
        for criterion in all_criteria:
            if criterion['parent_id'] is not None:
                parent_ids.add(criterion['parent_id'])
        
        # Return only criteria that are NOT parents (i.e., leaf criteria)
        leaf_criteria = [c for c in all_criteria if c['id'] not in parent_ids]
        
        return leaf_criteria

    
    # ==================== Alternative Operations ====================
    
    def add_alternative(self, project_id: int, name: str, description: str = "") -> int:
        """Add a new alternative"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO alternatives (project_id, name, description) VALUES (?, ?, ?)",
            (project_id, name, description)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_alternatives(self, project_id: int) -> List[Dict[str, Any]]:
        """Get all alternatives for a project"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM alternatives WHERE project_id = ? ORDER BY id", (project_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def update_alternative(self, alternative_id: int, name: str, description: str = "") -> None:
        """Update an alternative"""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE alternatives SET name = ?, description = ? WHERE id = ?",
            (name, description, alternative_id)
        )
        self.conn.commit()
    
    def delete_alternative(self, alternative_id: int) -> None:
        """Delete an alternative"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM alternatives WHERE id = ?", (alternative_id,))
        self.conn.commit()
    
    # ==================== Expert Operations ====================
    
    def add_expert(self, project_id: int, name: str, expertise_level: str = "", weight: Optional[float] = None) -> int:
        """Add a new expert"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO experts (project_id, name, expertise_level, weight) VALUES (?, ?, ?, ?)",
            (project_id, name, expertise_level, weight)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_experts(self, project_id: int) -> List[Dict[str, Any]]:
        """Get all experts for a project"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM experts WHERE project_id = ? ORDER BY id", (project_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def update_expert(self, expert_id: int, name: str, expertise_level: str = "", weight: Optional[float] = None) -> None:
        """Update an expert"""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE experts SET name = ?, expertise_level = ?, weight = ? WHERE id = ?",
            (name, expertise_level, weight, expert_id)
        )
        self.conn.commit()
    
    def update_expert_weight(self, expert_id: int, weight: Optional[float]) -> None:
        """Update expert weight only"""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE experts SET weight = ? WHERE id = ?", (weight, expert_id))
        self.conn.commit()
    
    def get_expert_weights(self, project_id: int) -> Dict[int, float]:
        """Get expert weights with auto-calculation for equal distribution
        
        Returns:
            Dictionary mapping expert_id to weight
            Auto-calculates equal weights if all are NULL
        """
        experts = self.get_experts(project_id)
        if not experts:
            return {}
        
        weights = {}
        null_count = 0
        total_weight = 0.0
        
        # First pass: collect weights and count NULLs
        for expert in experts:
            w = expert.get('weight')
            if w is None:
                null_count += 1
            else:
                weights[expert['id']] = w
                total_weight += w
        
        # If all NULL, equal distribution
        if null_count == len(experts):
            equal_weight = 1.0 / len(experts)
            return {expert['id']: equal_weight for expert in experts}
        
        # If some NULL, distribute remaining
        if null_count > 0:
            remaining = max(0.0, 1.0 - total_weight)
            auto_weight = remaining / null_count if null_count > 0 else 0.0
            for expert in experts:
                if expert.get('weight') is None:
                    weights[expert['id']] = auto_weight
        
        return weights
    
    def delete_expert(self, expert_id: int) -> None:
        """Delete an expert"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM experts WHERE id = ?", (expert_id,))
        self.conn.commit()
    
    # ==================== AHP Comparison Operations ====================
    
    def add_ahp_comparison(self, project_id: int, expert_id: int, criterion1_id: int,
                          criterion2_id: int, fuzzy_l: float, fuzzy_m: float, 
                          fuzzy_u: float, scenario_id: int = 1) -> None:
        """
        Add or update an AHP pairwise comparison
        
        Args:
            scenario_id: Scenario ID (default=1 for Base Scenario)
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO ahp_comparisons 
            (project_id, scenario_id, expert_id, criterion1_id, criterion2_id, fuzzy_l, fuzzy_m, fuzzy_u)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (project_id, scenario_id, expert_id, criterion1_id, criterion2_id, fuzzy_l, fuzzy_m, fuzzy_u))
        self.conn.commit()
    
    
    def get_ahp_comparisons(self, project_id: int, expert_id: Optional[int] = None,
                           scenario_id: int = 1) -> List[Dict[str, Any]]:
        """
        Get AHP comparisons for a project (optionally filtered by expert)
        
        Args:
            scenario_id: Scenario ID to filter by (default=1 for Base Scenario)
        """
        cursor = self.conn.cursor()
        if expert_id:
            cursor.execute(
                """SELECT * FROM ahp_comparisons 
                   WHERE project_id = ? AND expert_id = ? AND scenario_id = ?""",
                (project_id, expert_id, scenario_id)
            )
        else:
            cursor.execute(
                """SELECT * FROM ahp_comparisons 
                   WHERE project_id = ? AND scenario_id = ?""",
                (project_id, scenario_id)
            )
        return [dict(row) for row in cursor.fetchall()]
    
    def delete_ahp_comparisons_by_expert(self, expert_id: int) -> None:
        """Delete all comparisons for an expert"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM ahp_comparisons WHERE expert_id = ?", (expert_id,))
        self.conn.commit()
    
    # ==================== TOPSIS Rating Operations ====================
    
    def add_topsis_rating(self, project_id: int, alternative_id: int, criterion_id: int,
                         rating_lower: float, rating_upper: float, expert_id: Optional[int] = None,
                         scenario_id: int = 1) -> None:
        """
        Add or update a TOPSIS rating
        
        Args:
            scenario_id: Scenario ID (default=1 for Base Scenario)
        """
        cursor = self.conn.cursor()
        
        if expert_id is None:
            # Legacy or global rating (expert_id IS NULL)
            # Check if exists
            cursor.execute("""
                SELECT id FROM topsis_ratings 
                WHERE project_id=? AND alternative_id=? AND criterion_id=? 
                  AND expert_id IS NULL AND scenario_id=?
            """, (project_id, alternative_id, criterion_id, scenario_id))
            row = cursor.fetchone()
            
            if row:
                cursor.execute("""
                    UPDATE topsis_ratings 
                    SET rating_lower=?, rating_upper=?
                    WHERE id=?
                """, (rating_lower, rating_upper, row[0]))
            else:
                cursor.execute("""
                    INSERT INTO topsis_ratings 
                    (project_id, scenario_id, alternative_id, criterion_id, rating_lower, rating_upper, expert_id)
                    VALUES (?, ?, ?, ?, ?, ?, NULL)
                """, (project_id, scenario_id, alternative_id, criterion_id, rating_lower, rating_upper))
        else:
            # Expert specific rating
            # Check if exists
            cursor.execute("""
                SELECT id FROM topsis_ratings 
                WHERE project_id=? AND alternative_id=? AND criterion_id=? 
                  AND expert_id=? AND scenario_id=?
            """, (project_id, alternative_id, criterion_id, expert_id, scenario_id))
            row = cursor.fetchone()
            
            if row:
                cursor.execute("""
                    UPDATE topsis_ratings 
                    SET rating_lower=?, rating_upper=?
                    WHERE id=?
                """, (rating_lower, rating_upper, row[0]))
            else:
                cursor.execute("""
                    INSERT INTO topsis_ratings 
                    (project_id, scenario_id, alternative_id, criterion_id, rating_lower, rating_upper, expert_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (project_id, scenario_id, alternative_id, criterion_id, rating_lower, rating_upper, expert_id))
                
        self.conn.commit()
    
    
    def get_topsis_ratings(self, project_id: int, expert_id: Optional[int] = None,
                          scenario_id: int = 1) -> List[Dict[str, Any]]:
        """
        Get TOPSIS ratings for a project, optionally filtered by expert
        
        Args:
            scenario_id: Scenario ID to filter by (default=1 for Base Scenario)
        """
        cursor = self.conn.cursor()
        if expert_id is None:
            # Get all ratings for this scenario (including those with expert_id=NULL and specific experts)
            cursor.execute(
                "SELECT * FROM topsis_ratings WHERE project_id = ? AND scenario_id = ?",
                (project_id, scenario_id)
            )
        else:
            # Get ratings for specific expert in this scenario
            cursor.execute(
                "SELECT * FROM topsis_ratings WHERE project_id = ? AND expert_id = ? AND scenario_id = ?",
                (project_id, expert_id, scenario_id)
            )
            
        return [dict(row) for row in cursor.fetchall()]
    
    
    def get_topsis_rating(self, project_id: int, alternative_id: int, 
                         criterion_id: int, expert_id: Optional[int] = None,
                         scenario_id: int = 1) -> Optional[Tuple[float, float]]:
        """
        Get a specific TOPSIS rating
        
        Args:
            scenario_id: Scenario ID to filter by (default=1 for Base Scenario)
        """
        cursor = self.conn.cursor()
        if expert_id is None:
            query = """SELECT rating_lower, rating_upper FROM topsis_ratings 
                       WHERE project_id = ? AND alternative_id = ? AND criterion_id = ? 
                         AND expert_id IS NULL AND scenario_id = ?"""
            params = (project_id, alternative_id, criterion_id, scenario_id)
        else:
            query = """SELECT rating_lower, rating_upper FROM topsis_ratings 
                       WHERE project_id = ? AND alternative_id = ? AND criterion_id = ? 
                         AND expert_id = ? AND scenario_id = ?"""
            params = (project_id, alternative_id, criterion_id, expert_id, scenario_id)
            
        cursor.execute(query, params)
        row = cursor.fetchone()
        return (row[0], row[1]) if row else None
