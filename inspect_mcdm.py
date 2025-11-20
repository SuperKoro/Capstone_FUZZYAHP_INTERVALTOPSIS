import sqlite3
import os

db_path = "Demo_Expert.mcdm"

if not os.path.exists(db_path):
    print(f"File not found: {db_path}")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables:", [t[0] for t in tables])
    
    # Check experts
    if ('experts',) in tables:
        print("\nExperts:")
        cursor.execute("SELECT * FROM experts")
        columns = [description[0] for description in cursor.description]
        print(columns)
        for row in cursor.fetchall():
            print(row)
            
    # Check comparisons
    if ('ahp_comparisons',) in tables:
        print("\nAHP Comparisons (first 5):")
        cursor.execute("SELECT * FROM ahp_comparisons LIMIT 5")
        columns = [description[0] for description in cursor.description]
        print(columns)
        for row in cursor.fetchall():
            print(row)

    conn.close()
except Exception as e:
    print(f"Error: {e}")
