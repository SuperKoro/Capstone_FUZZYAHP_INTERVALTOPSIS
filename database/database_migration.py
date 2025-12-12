"""
Database Migration Script
Handles schema evolution for Scenarios feature
"""

import sqlite3
from sqlite3 import OperationalError
from typing import Optional


def migrate_to_scenarios(db_path: str) -> None:
    """
    Migrate database to support Scenarios feature
    
    Changes:
    1. Create `scenarios` table
    2. Add `scenario_id` column to `ahp_comparisons` and `topsis_ratings`
    3. Create base scenario and assign all existing data to it
    
    Args:
        db_path: Path to .mcdm database file
        
    This function is idempotent - safe to run multiple times
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print(f"[Migration] Starting migration for: {db_path}")
        
        # ================================================================
        # Step 1: Create scenarios table
        # ================================================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scenarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_base BOOLEAN DEFAULT 0,
                parent_id INTEGER NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (parent_id) REFERENCES scenarios(id) ON DELETE SET NULL,
                UNIQUE(project_id, name)
            )
        """)
        print("[Migration] ✓ Scenarios table created/verified")
        
        # ================================================================
        # Step 2: Ensure Base Scenario exists
        # ================================================================
        # Get project_id (assume single project per file)
        cursor.execute("SELECT id FROM projects LIMIT 1")
        project_row = cursor.fetchone()
        
        if project_row is None:
            print("[Migration] ⚠ No project found in database - skipping scenario creation")
            conn.close()
            return
        
        project_id = project_row[0]
        
        # Check if base scenario exists for this project
        cursor.execute("""
            SELECT id FROM scenarios 
            WHERE project_id = ? AND is_base = 1
        """, (project_id,))
        
        base_scenario_row = cursor.fetchone()
        
        if base_scenario_row is None:
            # Create base scenario
            cursor.execute("""
                INSERT INTO scenarios (project_id, name, description, is_base)
                VALUES (?, 'Base Scenario', 'Original project data', 1)
            """, (project_id,))
            base_scenario_id = cursor.lastrowid
            print(f"[Migration] ✓ Base scenario created with ID: {base_scenario_id}")
        else:
            base_scenario_id = base_scenario_row[0]
            print(f"[Migration] ✓ Base scenario exists with ID: {base_scenario_id}")
        
        # ================================================================
        # Step 3: Add scenario_id column to ahp_comparisons
        # ================================================================
        try:
            # Check if column exists
            cursor.execute("PRAGMA table_info(ahp_comparisons)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'scenario_id' not in columns:
                # Add column - SQLite requires recreating table for proper constraints
                print("[Migration] Adding scenario_id to ahp_comparisons...")
                
                # Backup existing data
                cursor.execute("""
                    CREATE TABLE ahp_comparisons_backup AS 
                    SELECT * FROM ahp_comparisons
                """)
                
                # Drop old table
                cursor.execute("DROP TABLE ahp_comparisons")
                
                # Create new table with scenario_id
                cursor.execute("""
                    CREATE TABLE ahp_comparisons (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        project_id INTEGER NOT NULL,
                        scenario_id INTEGER NOT NULL DEFAULT 1,
                        expert_id INTEGER NOT NULL,
                        criterion1_id INTEGER NOT NULL,
                        criterion2_id INTEGER NOT NULL,
                        fuzzy_l REAL NOT NULL,
                        fuzzy_m REAL NOT NULL,
                        fuzzy_u REAL NOT NULL,
                        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                        FOREIGN KEY (scenario_id) REFERENCES scenarios(id) ON DELETE CASCADE,
                        FOREIGN KEY (expert_id) REFERENCES experts(id) ON DELETE CASCADE,
                        FOREIGN KEY (criterion1_id) REFERENCES criteria(id) ON DELETE CASCADE,
                        FOREIGN KEY (criterion2_id) REFERENCES criteria(id) ON DELETE CASCADE,
                        UNIQUE(project_id, scenario_id, expert_id, criterion1_id, criterion2_id)
                    )
                """)
                
                # Restore data with scenario_id = base_scenario_id
                cursor.execute(f"""
                    INSERT INTO ahp_comparisons 
                        (id, project_id, scenario_id, expert_id, criterion1_id, 
                         criterion2_id, fuzzy_l, fuzzy_m, fuzzy_u)
                    SELECT 
                        id, project_id, {base_scenario_id}, expert_id, criterion1_id,
                        criterion2_id, fuzzy_l, fuzzy_m, fuzzy_u
                    FROM ahp_comparisons_backup
                """)
                
                # Drop backup
                cursor.execute("DROP TABLE ahp_comparisons_backup")
                
                # Recreate index
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_ahp_project 
                    ON ahp_comparisons(project_id)
                """)
                
                print("[Migration] ✓ ahp_comparisons migrated successfully")
            else:
                print("[Migration] ✓ ahp_comparisons already has scenario_id")
                
        except Exception as e:
            print(f"[Migration] ✗ Error migrating ahp_comparisons: {e}")
            raise
        
        # ================================================================
        # Step 4: Add scenario_id column to topsis_ratings
        # ================================================================
        try:
            # Check if column exists
            cursor.execute("PRAGMA table_info(topsis_ratings)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'scenario_id' not in columns:
                print("[Migration] Adding scenario_id to topsis_ratings...")
                
                # Backup existing data
                cursor.execute("""
                    CREATE TABLE topsis_ratings_backup AS 
                    SELECT * FROM topsis_ratings
                """)
                
                # Drop old table
                cursor.execute("DROP TABLE topsis_ratings")
                
                # Create new table with scenario_id
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
                        FOREIGN KEY (criterion_id) REFERENCES criteria(id) ON DELETE CASCADE
                    )
                """)
                
                # Restore data with scenario_id = base_scenario_id
                cursor.execute(f"""
                    INSERT INTO topsis_ratings
                        (id, project_id, scenario_id, expert_id, alternative_id,
                         criterion_id, rating_lower, rating_upper)
                    SELECT 
                        id, project_id, {base_scenario_id}, expert_id, alternative_id,
                        criterion_id, rating_lower, rating_upper
                    FROM topsis_ratings_backup
                """)
                
                # Drop backup
                cursor.execute("DROP TABLE topsis_ratings_backup")
                
                # Recreate index
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_topsis_project 
                    ON topsis_ratings(project_id)
                """)
                
                print("[Migration] ✓ topsis_ratings migrated successfully")
            else:
                print("[Migration] ✓ topsis_ratings already has scenario_id")
                
        except Exception as e:
            print(f"[Migration] ✗ Error migrating topsis_ratings: {e}")
            raise
        
        # ================================================================
        # Commit all changes
        # ================================================================
        conn.commit()
        print("[Migration] ✓ Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"[Migration] ✗ Migration failed: {e}")
        print("[Migration] ✗ Rolling back changes...")
        raise e
        
    finally:
        conn.close()


def check_migration_needed(db_path: str) -> bool:
    """
    Check if database needs migration to scenarios
    
    Args:
        db_path: Path to .mcdm database file
        
    Returns:
        True if migration is needed
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if scenarios table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='scenarios'
        """)
        
        if cursor.fetchone() is None:
            return True  # Need migration
        
        # Check if ahp_comparisons has scenario_id
        cursor.execute("PRAGMA table_info(ahp_comparisons)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'scenario_id' not in columns:
            return True  # Need migration
        
        return False  # Already migrated
        
    finally:
        conn.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python database_migration.py <path_to_mcdm_file>")
        print("\nExample:")
        print("  python database_migration.py Demo_Master.mcdm")
        sys.exit(1)
    
    db_path = sys.argv[1]
    
    print("=" * 60)
    print("Database Migration Tool - Scenarios Feature")
    print("=" * 60)
    
    # Check if migration needed
    if check_migration_needed(db_path):
        print(f"\n📋 Migration required for: {db_path}")
        print("\nThis will:")
        print("  1. Create 'scenarios' table")
        print("  2. Add 'scenario_id' to ahp_comparisons")
        print("  3. Add 'scenario_id' to topsis_ratings")
        print("  4. Assign existing data to 'Base Scenario'")
        
        response = input("\nProceed with migration? (yes/no): ")
        if response.lower() in ['yes', 'y']:
            migrate_to_scenarios(db_path)
            print("\n✓ Migration successful! Your project is now ready for Scenarios.")
        else:
            print("\n✗ Migration cancelled.")
    else:
        print(f"\n✓ Database already migrated: {db_path}")
        print("  No action needed.")
