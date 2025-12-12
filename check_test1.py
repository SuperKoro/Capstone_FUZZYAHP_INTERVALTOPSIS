import sqlite3

conn = sqlite3.connect(r"C:\Users\minh\Downloads\test1.mcdm")
cursor = conn.cursor()

print("="*60)
print("CHECKING: test1.mcdm")
print("="*60)

# Get tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cursor.fetchall()]
print("\nTables:", tables)

# Check scenarios
if 'scenarios' in tables:
    print("\n✅ scenarios table EXISTS")
else:
    print("\n❌ scenarios table MISSING")

# Check topsis_ratings columns
cursor.execute("PRAGMA table_info(topsis_ratings)")
cols = [r[1] for r in cursor.fetchall()]
print("\ntopsis_ratings columns:", cols)

if 'scenario_id' in cols:
    print("✅ scenario_id EXISTS")
else:
    print("❌ scenario_id MISSING")

conn.close()
