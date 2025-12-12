"""
Direct Database Inspector
Check the ACTUAL schema of the newest .mcdm file
"""

import sqlite3
import os
from datetime import datetime

# Find newest .mcdm file
import glob
downloads = r"C:\Users\minh\Downloads"
mcdm_files = glob.glob(os.path.join(downloads, "*.mcdm"))

if not mcdm_files:
    print("No .mcdm files found in Downloads!")
    exit(1)

# Sort by modification time, newest first
mcdm_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
newest_file = mcdm_files[0]

print("="*70)
print(f"INSPECTING: {os.path.basename(newest_file)}")
print(f"Modified: {datetime.fromtimestamp(os.path.getmtime(newest_file))}")
print("="*70)

conn = sqlite3.connect(newest_file)
cursor = conn.cursor()

# Check all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [row[0] for row in cursor.fetchall()]

print("\n📋 TABLES FOUND:")
for table in tables:
    print(f"  - {table}")

# Check if scenarios table exists
if 'scenarios' in tables:
    print("\n✅ scenarios table EXISTS")
    cursor.execute("SELECT COUNT(*) FROM scenarios")
    count = cursor.fetchone()[0]
    print(f"   Scenarios count: {count}")
else:
    print("\n❌ scenarios table MISSING!")

# Check ahp_comparisons schema
print("\n📊 ahp_comparisons schema:")
cursor.execute("PRAGMA table_info(ahp_comparisons)")
ahp_columns = [(row[1], row[2]) for row in cursor.fetchall()]
for col_name, col_type in ahp_columns:
    marker = "✓" if col_name == "scenario_id" else " "
    print(f"  {marker} {col_name}: {col_type}")

if not any(col[0] == 'scenario_id' for col in ahp_columns):
    print("  ❌ scenario_id MISSING in ahp_comparisons!")

# Check topsis_ratings schema
print("\n📊 topsis_ratings schema:")
cursor.execute("PRAGMA table_info(topsis_ratings)")
topsis_columns = [(row[1], row[2]) for row in cursor.fetchall()]
for col_name, col_type in topsis_columns:
    marker = "✓" if col_name == "scenario_id" else " "
    print(f"  {marker} {col_name}: {col_type}")

if not any(col[0] == 'scenario_id' for col in topsis_columns):
    print("  ❌ scenario_id MISSING in topsis_ratings!")

conn.close()

print("\n" + "="*70)
print("CONCLUSION:")
if 'scenarios' not in tables:
    print("❌ OLD SCHEMA - scenarios table missing!")
    print("   → schema.py NOT being used!")
elif not any(col[0] == 'scenario_id' for col in topsis_columns):
    print("❌ OLD SCHEMA - scenario_id missing!")
    print("   → schema.py NOT being used!")
else:
    print("✅ NEW SCHEMA - All correct!")
    print("   → But you're still getting errors???")
    print("   → Maybe opening WRONG file?")
print("="*70)
