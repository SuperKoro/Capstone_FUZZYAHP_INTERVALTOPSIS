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
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        self.conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        
        # Auto-migrate if needed
        self._check_and_migrate()
    
    def _check_and_migrate(self):
        """Check and auto-migrate database schema if needed"""
        cursor = self.conn.cursor()
        
        try:
            # Check if expert_id column exists in topsis_ratings
            cursor.execute("PRAGMA table_info(topsis_ratings)")
            columns = [info[1] for info in cursor.fetchall()]
            
            if 'expert_id' not in columns:
                print(f"Auto-migrating database: {self.db_path}")
                print("  Adding expert_id column to topsis_ratings...")
                cursor.execute("ALTER TABLE topsis_ratings ADD COLUMN expert_id INTEGER")
                self.conn.commit()
                print("  Migration complete!")
            
            # Check if weight column exists in experts
            cursor.execute("PRAGMA table_info(experts)")
            expert_columns = [info[1] for info in cursor.fetchall()]
            
            if 'weight' not in expert_columns:
                print(f"Auto-migrating database: {self.db_path}")
                print("  Adding weight column to experts...")
                cursor.execute("ALTER TABLE experts ADD COLUMN weight REAL DEFAULT NULL")
                self.conn.commit()
                print("  Experts migration complete!")
            
            # Check if UNIQUE constraint needs fixing
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='topsis_ratings'")
            result = cursor.fetchone()
            
            # If constraint doesn't include expert_id, we need to recreate the table
            if result and "UNIQUE(project_id, alternative_id, criterion_id, expert_id)" not in result[0]:
                print("  Fixing UNIQUE constraint...")
                
                cursor.execute("BEGIN TRANSACTION")
                
                # Rename old table
                cursor.execute("ALTER TABLE topsis_ratings RENAME TO topsis_ratings_old")
                
                # Create new table
                cursor.execute("""
                    CREATE TABLE topsis_ratings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        project_id INTEGER NOT NULL,
                        expert_id INTEGER,
                        alternative_id INTEGER NOT NULL,
                        criterion_id INTEGER NOT NULL,
                        rating_lower REAL NOT NULL,
                        rating_upper REAL NOT NULL,
                        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                        FOREIGN KEY (expert_id) REFERENCES experts(id) ON DELETE CASCADE,
                        FOREIGN KEY (alternative_id) REFERENCES alternatives(id) ON DELETE CASCADE,
                        FOREIGN KEY (criterion_id) REFERENCES criteria(id) ON DELETE CASCADE,
                        UNIQUE(project_id, alternative_id, criterion_id, expert_id)
                    )
                """)
                
                # Copy data
                cursor.execute("PRAGMA table_info(topsis_ratings_old)")
                old_cols = [info[1] for info in cursor.fetchall()]
                
                if 'expert_id' in old_cols:
                    cursor.execute("""
                        INSERT INTO topsis_ratings 
                        (id, project_id, expert_id, alternative_id, criterion_id, rating_lower, rating_upper)
                        SELECT id, project_id, expert_id, alternative_id, criterion_id, rating_lower, rating_upper
                        FROM topsis_ratings_old
                    """)
                else:
                    cursor.execute("""
                        INSERT INTO topsis_ratings 
                        (id, project_id, alternative_id, criterion_id, rating_lower, rating_upper)
                        SELECT id, project_id, alternative_id, criterion_id, rating_lower, rating_upper
                        FROM topsis_ratings_old
                    """)
                
                cursor.execute("DROP TABLE topsis_ratings_old")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_topsis_project ON topsis_ratings(project_id)")
                
                self.conn.commit()
                print("  UNIQUE constraint fixed!")
                
        except Exception as e:
            print(f"Migration error (non-fatal): {e}")
            self.conn.rollback()
    
    def disconnect(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
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
                          fuzzy_u: float) -> None:
        """Add or update an AHP pairwise comparison"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO ahp_comparisons 
            (project_id, expert_id, criterion1_id, criterion2_id, fuzzy_l, fuzzy_m, fuzzy_u)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (project_id, expert_id, criterion1_id, criterion2_id, fuzzy_l, fuzzy_m, fuzzy_u))
        self.conn.commit()
    
    def get_ahp_comparisons(self, project_id: int, expert_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get AHP comparisons for a project (optionally filtered by expert)"""
        cursor = self.conn.cursor()
        if expert_id:
            cursor.execute(
                "SELECT * FROM ahp_comparisons WHERE project_id = ? AND expert_id = ?",
                (project_id, expert_id)
            )
        else:
            cursor.execute("SELECT * FROM ahp_comparisons WHERE project_id = ?", (project_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def delete_ahp_comparisons_by_expert(self, expert_id: int) -> None:
        """Delete all comparisons for an expert"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM ahp_comparisons WHERE expert_id = ?", (expert_id,))
        self.conn.commit()
    
    # ==================== TOPSIS Rating Operations ====================
    
    def add_topsis_rating(self, project_id: int, alternative_id: int, criterion_id: int,
                         rating_lower: float, rating_upper: float, expert_id: Optional[int] = None) -> None:
        """Add or update a TOPSIS rating"""
        cursor = self.conn.cursor()
        
        # Check if expert_id column exists (for backward compatibility if migration failed)
        # But we assume migration ran.
        
        if expert_id is None:
            # Legacy or global rating (expert_id IS NULL)
            cursor.execute("""
                INSERT OR REPLACE INTO topsis_ratings 
                (project_id, alternative_id, criterion_id, rating_lower, rating_upper, expert_id)
                VALUES (?, ?, ?, ?, ?, NULL)
            """, (project_id, alternative_id, criterion_id, rating_lower, rating_upper))
        else:
            # Expert specific rating
            # Note: We need a unique constraint on (project_id, alternative_id, criterion_id, expert_id)
            # The original schema had UNIQUE(project_id, alternative_id, criterion_id) which might conflict
            # if we try to insert multiple experts.
            # However, SQLite handles NULL in UNIQUE constraints as distinct values usually, 
            # BUT we might need to drop the old unique index and create a new one.
            # For now, let's try to insert. If it fails, we might need to handle it.
            # Actually, the migration script didn't update the UNIQUE constraint.
            # This is a potential issue. 
            # Let's use a WHERE clause to update if exists, or insert.
            
            # Check if exists
            cursor.execute("""
                SELECT id FROM topsis_ratings 
                WHERE project_id=? AND alternative_id=? AND criterion_id=? AND expert_id=?
            """, (project_id, alternative_id, criterion_id, expert_id))
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
                    (project_id, alternative_id, criterion_id, rating_lower, rating_upper, expert_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (project_id, alternative_id, criterion_id, rating_lower, rating_upper, expert_id))
                
        self.conn.commit()
    
    def get_topsis_ratings(self, project_id: int, expert_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get TOPSIS ratings for a project, optionally filtered by expert"""
        cursor = self.conn.cursor()
        if expert_id is None:
            # Get all ratings (including those with expert_id=NULL and specific experts)
            cursor.execute("SELECT * FROM topsis_ratings WHERE project_id = ?", (project_id,))
        else:
            # Get ratings for specific expert
            cursor.execute("SELECT * FROM topsis_ratings WHERE project_id = ? AND expert_id = ?", (project_id, expert_id))
            
        return [dict(row) for row in cursor.fetchall()]
    
    def get_topsis_rating(self, project_id: int, alternative_id: int, 
                         criterion_id: int, expert_id: Optional[int] = None) -> Optional[Tuple[float, float]]:
        """Get a specific TOPSIS rating"""
        cursor = self.conn.cursor()
        if expert_id is None:
            query = "SELECT rating_lower, rating_upper FROM topsis_ratings WHERE project_id = ? AND alternative_id = ? AND criterion_id = ? AND expert_id IS NULL"
            params = (project_id, alternative_id, criterion_id)
        else:
            query = "SELECT rating_lower, rating_upper FROM topsis_ratings WHERE project_id = ? AND alternative_id = ? AND criterion_id = ? AND expert_id = ?"
            params = (project_id, alternative_id, criterion_id, expert_id)
            
        cursor.execute(query, params)
        row = cursor.fetchone()
        return (row[0], row[1]) if row else None
