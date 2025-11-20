import sqlite3
import os
import glob

def check_expert_id_exists(db_file):
    """Check if expert_id column exists in topsis_ratings table"""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA table_info(topsis_ratings)")
        columns = [info[1] for info in cursor.fetchall()]
        return 'expert_id' in columns
    finally:
        conn.close()

def add_expert_id_column(db_file):
    """Add expert_id column if it doesn't exist"""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    try:
        print(f"  Adding expert_id column...")
        cursor.execute("ALTER TABLE topsis_ratings ADD COLUMN expert_id INTEGER")
        cursor.execute("UPDATE topsis_ratings SET expert_id = NULL WHERE expert_id IS NULL")
        conn.commit()
        print(f"  Column added successfully")
        return True
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print(f"  Column already exists, skipping...")
            return True
        else:
            print(f"  Error: {e}")
            return False
    finally:
        conn.close()

def fix_unique_constraint(db_file):
    """Fix UNIQUE constraint to include expert_id"""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    try:
        cursor.execute("BEGIN TRANSACTION")
        
        # Check if we need to fix the constraint
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='topsis_ratings'")
        result = cursor.fetchone()
        if result and "UNIQUE(project_id, alternative_id, criterion_id, expert_id)" in result[0]:
            print("  UNIQUE constraint already correct, skipping...")
            conn.rollback()
            return True
        
        print("  Fixing UNIQUE constraint...")
        
        # Rename old table
        cursor.execute("ALTER TABLE topsis_ratings RENAME TO topsis_ratings_old")
        
        # Create new table with corrected constraint
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
        old_columns = [info[1] for info in cursor.fetchall()]
        
        if 'expert_id' in old_columns:
            cursor.execute("""
                INSERT INTO topsis_ratings (id, project_id, expert_id, alternative_id, criterion_id, rating_lower, rating_upper)
                SELECT id, project_id, expert_id, alternative_id, criterion_id, rating_lower, rating_upper
                FROM topsis_ratings_old
            """)
        else:
            cursor.execute("""
                INSERT INTO topsis_ratings (id, project_id, alternative_id, criterion_id, rating_lower, rating_upper)
                SELECT id, project_id, alternative_id, criterion_id, rating_lower, rating_upper
                FROM topsis_ratings_old
            """)
        
        # Drop old table
        cursor.execute("DROP TABLE topsis_ratings_old")
        
        # Recreate index
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_topsis_project ON topsis_ratings(project_id)")
        
        conn.commit()
        print("  UNIQUE constraint fixed successfully")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"  Error fixing constraint: {e}")
        return False
    finally:
        conn.close()

def migrate_database(db_file):
    """Migrate a single database file"""
    print(f"\nMigrating {db_file}...")
    
    # Step 1: Add expert_id column if missing
    if not check_expert_id_exists(db_file):
        if not add_expert_id_column(db_file):
            return False
    else:
        print("  expert_id column already exists")
    
    # Step 2: Fix UNIQUE constraint
    if not fix_unique_constraint(db_file):
        return False
    
    print(f"  ✓ {db_file} migration complete")
    return True

if __name__ == "__main__":
    # Find all .mcdm files in current directory
    mcdm_files = glob.glob("*.mcdm")
    
    if not mcdm_files:
        print("No .mcdm files found in current directory")
    else:
        print(f"Found {len(mcdm_files)} .mcdm file(s):")
        for f in mcdm_files:
            print(f"  - {f}")
        
        print("\nStarting migration...")
        success_count = 0
        
        for db_file in mcdm_files:
            if migrate_database(db_file):
                success_count += 1
        
        print(f"\n{'='*50}")
        print(f"Migration complete: {success_count}/{len(mcdm_files)} files migrated successfully")
