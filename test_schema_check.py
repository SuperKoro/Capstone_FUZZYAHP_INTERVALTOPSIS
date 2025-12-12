"""
Force Reload Test Script
Test if schema.py is correctly imported with latest changes
"""

import sys
import importlib

# Remove cached modules
if 'database.schema' in sys.modules:
    del sys.modules['database.schema']

# Re-import fresh
from database.schema import DatabaseSchema
import inspect

# Check if scenarios table is in create_schema
source = inspect.getsource(DatabaseSchema.create_schema)

print("="*60)
print("SCHEMA SOURCE CODE CHECK")
print("="*60)

if "scenarios" in source:
    print("✓ scenarios table FOUND in schema")
else:
    print("✗ scenarios table NOT FOUND in schema")

if "scenario_id INTEGER NOT NULL DEFAULT 1" in source:
    print("✓ scenario_id column FOUND in ahp_comparisons")
else:
    print("✗ scenario_id column NOT FOUND in ahp_comparisons")

if "scenario_id INTEGER NOT NULL DEFAULT 1" in source:
    print("✓ scenario_id column FOUND in topsis_ratings")
else:
    print("✗ scenario_id column NOT FOUND in topsis_ratings")

print("\n" + "="*60)
print("TEST: Create a test database")
print("="*60)

import os
test_db = "test_schema_check.mcdm"

# Clean old test
if os.path.exists(test_db):
    os.remove(test_db)

# Create with schema
DatabaseSchema.create_schema(test_db)
project_id = DatabaseSchema.initialize_project(test_db, "Test Project")

# Check tables
import sqlite3
conn = sqlite3.connect(test_db)
cursor = conn.cursor()

# Check scenarios table
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scenarios'")
if cursor.fetchone():
    print("✓ scenarios table EXISTS")
else:
    print("✗ scenarios table MISSING")

# Check scenario_id in ahp_comparisons
cursor.execute("PRAGMA table_info(ahp_comparisons)")
columns =[(row[1]) for row in cursor.fetchall()]
if 'scenario_id' in columns:
    print("✓ scenario_id column EXISTS in ahp_comparisons")
else:
    print("✗ scenario_id column MISSING in ahp_comparisons")

# Check scenario_id in topsis_ratings
cursor.execute("PRAGMA table_info(topsis_ratings)")
columns = [row[1] for row in cursor.fetchall()]
if 'scenario_id' in columns:
    print("✓ scenario_id column EXISTS in topsis_ratings")
else:
    print("✗ scenario_id column MISSING in topsis_ratings")

# Check Base Scenario was created
cursor.execute("SELECT * FROM scenarios WHERE name='Base Scenario'")
if cursor.fetchone():
    print("✓ Base Scenario EXISTS")
else:
    print("✗ Base Scenario MISSING")

conn.close()

print("\n" + "="*60)
print("CONCLUSION")
print("="*60)
print("If all checks show ✓, schema is correct!")
print("If any show ✗, schema.py is not being used!")
print("="*60)

# Cleanup
if os.path.exists(test_db):
    os.remove(test_db)
    print("\n✓ Test database cleaned up")
