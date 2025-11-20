import sqlite3
import os

def migrate_db():
    # Find all .mcdm files
    files = [f for f in os.listdir('.') if f.endswith('.mcdm')]
    
    if not files:
        print("No .mcdm files found to migrate.")
        return

    for file in files:
        print(f"Migrating {file}...")
        try:
            conn = sqlite3.connect(file)
            cursor = conn.cursor()
            
            # Check if column exists
            cursor.execute("PRAGMA table_info(topsis_ratings)")
            columns = [info[1] for info in cursor.fetchall()]
            
            if 'expert_id' not in columns:
                print(f"  Adding expert_id column to {file}...")
                # Add column
                cursor.execute("ALTER TABLE topsis_ratings ADD COLUMN expert_id INTEGER REFERENCES experts(id)")
                
                # If there are existing ratings, we might want to assign them to a default expert 
                # or leave them NULL (global). For now, leaving NULL is safer.
                
                conn.commit()
                print("  Success!")
            else:
                print("  Column expert_id already exists.")
                
            conn.close()
            
        except Exception as e:
            print(f"  Error migrating {file}: {e}")

if __name__ == "__main__":
    migrate_db()
