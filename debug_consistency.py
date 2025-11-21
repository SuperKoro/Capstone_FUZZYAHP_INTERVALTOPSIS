"""
Debug script to check why consistency metrics are not displayed
"""

import sqlite3
import numpy as np
from algorithms.fuzzy_ahp import FuzzyAHP
from algorithms.hierarchical_ahp import HierarchicalFuzzyAHP

# Connect to your demo database
conn = sqlite3.connect('Demo_Master.mcdm')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get project info
cursor.execute("SELECT * FROM projects LIMIT 1")
project = dict(cursor.fetchone())
project_id = project['id']
print(f"Project: {project['name']} (ID: {project_id})")
print("=" * 60)

# Get criteria
cursor.execute("SELECT * FROM criteria WHERE project_id = ?", (project_id,))
criteria = [dict(row) for row in cursor.fetchall()]
print(f"\nTotal Criteria: {len(criteria)}")
for c in criteria:
    print(f"  - {c['name']} (ID: {c['id']}, Parent: {c.get('parent_id')})")

# Get experts
cursor.execute("SELECT * FROM experts WHERE project_id = ?", (project_id,))
experts = [dict(row) for row in cursor.fetchall()]
print(f"\nTotal Experts: {len(experts)}")
for e in experts:
    print(f"  - {e['name']} (Weight: {e.get('weight')})")

# Get comparisons
cursor.execute("SELECT * FROM ahp_comparisons WHERE project_id = ?", (project_id,))
comparisons = [dict(row) for row in cursor.fetchall()]
print(f"\nTotal Comparisons: {len(comparisons)}")

# Organize comparisons by group
comparisons_by_group = HierarchicalFuzzyAHP.organize_comparisons_by_group(comparisons, criteria)
print(f"\nComparisons organized into {len(comparisons_by_group)} groups:")
for group_key, matrices in comparisons_by_group.items():
    print(f"  - {group_key}: {len(matrices)} expert matrices")

# Calculate hierarchical weights
print("\n" + "=" * 60)
print("CALCULATING HIERARCHICAL WEIGHTS...")
print("=" * 60)

try:
    global_weights, consistency_info = HierarchicalFuzzyAHP.calculate_hierarchical_weights(
        criteria, comparisons_by_group
    )
    
    print("\nGlobal Weights:")
    for crit_id, weight in global_weights.items():
        crit_name = next(c['name'] for c in criteria if c['id'] == crit_id)
        print(f"  - {crit_name}: {weight:.4f}")
    
    print("\nConsistency Info:")
    print(f"Keys in consistency_info: {list(consistency_info.keys())}")
    for group_key, metrics in consistency_info.items():
        print(f"\n  Group: {group_key}")
        print(f"    CR: {metrics.get('cr', 'N/A'):.4f}")
        print(f"    CI: {metrics.get('ci', 'N/A'):.4f}")
        print(f"    λmax: {metrics.get('lambda_max', 'N/A'):.4f}")
        matrix = metrics.get('matrix')
        if matrix is not None:
            print(f"    Matrix shape: {matrix.shape if isinstance(matrix, np.ndarray) else 'Not ndarray'}")
    
    # Check if 'main' group has data
    if 'main' in consistency_info:
        print("\n✓ 'main' group HAS consistency data")
    else:
        print("\n✗ 'main' group DOES NOT have consistency data")
        print(f"   Available groups: {list(consistency_info.keys())}")
    
except Exception as e:
    import traceback
    print(f"\n✗ ERROR: {str(e)}")
    traceback.print_exc()

conn.close()
