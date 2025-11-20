import sqlite3
import pandas as pd
import numpy as np
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from database.manager import DatabaseManager

def inspect_data():
    db_path = "supplier_selection.db" # Default name, might need to check main.py or ask user
    # But DatabaseManager uses a specific path. Let's use DatabaseManager directly if possible or find the file.
    
    # Try to find the latest .mcdm file or just use the one the app uses.
    # The app uses QFileDialog to open/save. 
    # Let's look for .mcdm files in the current directory.
    
    files = [f for f in os.listdir('.') if f.endswith('.mcdm')]
    if not files:
        print("No .mcdm files found in current directory.")
        return

    print(f"Found files: {files}")
    # Use the most recent one
    latest_file = max(files, key=os.path.getmtime)
    print(f"Inspecting latest file: {latest_file}")
    
    conn = sqlite3.connect(latest_file)
    cursor = conn.cursor()
    
    print("\n1. CRITERIA & WEIGHTS")
    print("-" * 50)
    try:
        criteria = pd.read_sql_query("SELECT * FROM criteria", conn)
        print(criteria[['id', 'name', 'weight', 'is_benefit']])
    except Exception as e:
        print(f"Error reading criteria: {e}")

    print("\n2. ALTERNATIVES")
    print("-" * 50)
    try:
        alts = pd.read_sql_query("SELECT * FROM alternatives", conn)
        print(alts)
    except Exception as e:
        print(f"Error reading alternatives: {e}")

    print("\n3. TOPSIS RATINGS")
    print("-" * 50)
    try:
        ratings = pd.read_sql_query("""
            SELECT r.alternative_id, a.name as alt_name, 
                   r.criterion_id, c.name as crit_name,
                   r.rating_lower, r.rating_upper
            FROM topsis_ratings r
            JOIN alternatives a ON r.alternative_id = a.id
            JOIN criteria c ON r.criterion_id = c.id
        """, conn)
        print(ratings)
    except Exception as e:
        print(f"Error reading ratings: {e}")
        
    conn.close()

if __name__ == "__main__":
    inspect_data()
