import sqlite3
import os

DB_FILES = ["Demo_Master.mcdm", "Demo_Expert.mcdm"]

def fix_database(db_file):
    if not os.path.exists(db_file):
        print(f"Skipping {db_file} (not found)")
        return

    print(f"Fixing schema for {db_file}...")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    try:
        # Start transaction
        cursor.execute("BEGIN TRANSACTION")

        # 1. Rename old table
        print("  Renaming old table...")
        cursor.execute("ALTER TABLE topsis_ratings RENAME TO topsis_ratings_old")

        # 2. Create new table with updated UNIQUE constraint
        print("  Creating new table...")
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

        # 3. Copy data from old table
        print("  Copying data...")
        # Check columns in old table to be safe
        cursor.execute("PRAGMA table_info(topsis_ratings_old)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'expert_id' in columns:
            cursor.execute("""
                INSERT INTO topsis_ratings (id, project_id, expert_id, alternative_id, criterion_id, rating_lower, rating_upper)
                SELECT id, project_id, expert_id, alternative_id, criterion_id, rating_lower, rating_upper
                FROM topsis_ratings_old
            """)
        else:
            # If expert_id was missing (shouldn't happen if migration ran, but just in case)
            print("  Warning: expert_id column missing in old table, defaulting to NULL")
            cursor.execute("""
                INSERT INTO topsis_ratings (id, project_id, alternative_id, criterion_id, rating_lower, rating_upper)
                SELECT id, project_id, alternative_id, criterion_id, rating_lower, rating_upper
                FROM topsis_ratings_old
            """)

        # 4. Drop old table
        print("  Dropping old table...")
        cursor.execute("DROP TABLE topsis_ratings_old")
        
        # 5. Recreate Index
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_topsis_project ON topsis_ratings(project_id)")

        conn.commit()
        print("  Success!")

    except Exception as e:
        conn.rollback()
        print(f"  Failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    for db in DB_FILES:
        fix_database(db)
