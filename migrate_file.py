"""
Universal Migration Script
Migrate ANY .mcdm file from command line
"""

import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.database_migration import migrate_to_scenarios

def main():
    if len(sys.argv) < 2:
        print("Usage: python migrate_file.py <path_to_file.mcdm>")
        print("\nExample:")
        print('  python migrate_file.py "C:\\Users\\minh\\Downloads\\Test scena.mcdm"')
        print('  python migrate_file.py Demo_Master.mcdm')
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    if not os.path.exists(filepath):
        print(f"❌ Error: File not found: {filepath}")
        sys.exit(1)
    
    if not filepath.endswith('.mcdm'):
        print(f"❌ Error: File must have .mcdm extension: {filepath}")
        sys.exit(1)
    
    print(f"🔧 Migrating: {filepath}")
    print("="*60)
    
    try:
        migrate_to_scenarios(filepath)
        print("\n✅ Migration completed successfully!")
        print(f"📁 File: {filepath}")
        print("\nYou can now open this file in the application.")
    except Exception as e:
        print(f"\n❌ Migration failed!")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
