"""
Database Migration Script
Adds weight column to experts table in existing databases
"""

import sqlite3
import sys

def migrate_database(db_path):
    """Add weight column to experts table if it doesn't exist"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if weight column exists
        cursor.execute("PRAGMA table_info(experts)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'weight' not in columns:
            print(f"Adding weight column to experts table in {db_path}...")
            cursor.execute("ALTER TABLE experts ADD COLUMN weight REAL DEFAULT NULL")
            conn.commit()
            print("Migration completed successfully!")
        else:
            print("Weight column already exists. No migration needed.")
            
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
    
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        # Default to demo files
        import glob
        db_files = glob.glob("*.mcdm")
        if db_files:
            print(f"Found {len(db_files)} .mcdm files:")
            for db_file in db_files:
                print(f"  - {db_file}")
                migrate_database(db_file)
        else:
            print("No .mcdm files found. Please specify database path.")
