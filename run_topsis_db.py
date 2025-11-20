import sqlite3
import numpy as np
import sys
import os

sys.path.append(os.getcwd())
from algorithms.interval_topsis import IntervalTOPSIS

def run_topsis_on_db():
    # Find latest .mcdm file
    files = [f for f in os.listdir('.') if f.endswith('.mcdm')]
    if not files:
        print("No .mcdm files found.")
        return
    
    latest_file = max(files, key=os.path.getmtime)
    print(f"Processing file: {latest_file}")
    
    conn = sqlite3.connect(latest_file)
    cursor = conn.cursor()
    
    # 1. Get Criteria & Weights
    cursor.execute("SELECT id, name, weight, is_benefit FROM criteria ORDER BY id")
    criteria_rows = cursor.fetchall()
    
    if not criteria_rows:
        print("No criteria found.")
        return
        
    criteria_map = {row[0]: i for i, row in enumerate(criteria_rows)}
    weights = np.array([row[2] for row in criteria_rows])
    is_benefit = np.array([bool(row[3]) for row in criteria_rows])
    crit_names = [row[1] for row in criteria_rows]
    
    print("\nCRITERIA:")
    for i, name in enumerate(crit_names):
        print(f"  {name}: Weight={weights[i]:.4f}, Benefit={is_benefit[i]}")
    
    # 2. Get Alternatives
    cursor.execute("SELECT id, name FROM alternatives ORDER BY id")
    alt_rows = cursor.fetchall()
    
    if not alt_rows:
        print("No alternatives found.")
        return
        
    alt_map = {row[0]: i for i, row in enumerate(alt_rows)}
    alt_names = [row[1] for row in alt_rows]
    
    print("\nALTERNATIVES:")
    for name in alt_names:
        print(f"  {name}")
        
    # 3. Get Ratings
    n_alts = len(alt_rows)
    n_crits = len(criteria_rows)
    decision_matrix = np.zeros((n_alts, n_crits, 2))
    
    cursor.execute("SELECT alternative_id, criterion_id, rating_lower, rating_upper FROM topsis_ratings")
    rating_rows = cursor.fetchall()
    
    for r in rating_rows:
        alt_idx = alt_map.get(r[0])
        crit_idx = criteria_map.get(r[1])
        if alt_idx is not None and crit_idx is not None:
            decision_matrix[alt_idx, crit_idx] = [r[2], r[3]]
            
    conn.close()
    
    print("\nDECISION MATRIX:")
    print(decision_matrix)
    
    # 4. Run TOPSIS
    print("\nRUNNING TOPSIS CALCULATION...")
    try:
        CC, results = IntervalTOPSIS.rank_alternatives(decision_matrix, weights, is_benefit)
        
        print("\nRESULTS:")
        print("-" * 40)
        sorted_indices = results['ranking']
        
        for rank, idx in enumerate(sorted_indices):
            print(f"Rank {rank+1}: {alt_names[idx]} (CC = {CC[idx]:.4f})")
            
        print("-" * 40)
        
        # Detailed debug
        print("\nDEBUG DETAILS:")
        print(f"PIS: {results['PIS']}")
        print(f"NIS: {results['NIS']}")
        print(f"Dist to PIS: {results['distances_to_PIS']}")
        print(f"Dist to NIS: {results['distances_to_NIS']}")
        
    except Exception as e:
        print(f"Error running TOPSIS: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_topsis_on_db()
