"""
Migrate All Projects Script
Quick utility to migrate all .mcdm files to support scenarios
Run this once to batch migrate all projects
"""

import os
from database.database_migration import migrate_to_scenarios

def migrate_all_projects(directory='.'):
    """Migrate all .mcdm files in directory"""
    migrated = []
    failed = []
    
    print(f"Scanning {directory} for .mcdm files...")
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.mcdm'):
                filepath = os.path.join(root, file)
                print(f"\n{'='*60}")
                print(f"Migrating: {filepath}")
                print('='*60)
                
                try:
                    migrate_to_scenarios(filepath)
                    migrated.append(filepath)
                    print(f"✓ SUCCESS: {file}")
                except Exception as e:
                    failed.append((filepath, str(e)))
                    print(f"✗ FAILED: {file}")
                    print(f"  Error: {e}")
    
    # Summary
    print(f"\n{'='*60}")
    print("MIGRATION SUMMARY")
    print('='*60)
    print(f"✓ Successfully migrated: {len(migrated)}")
    print(f"✗ Failed: {len(failed)}")
    
    if migrated:
        print("\nMigrated files:")
        for f in migrated:
            print(f"  - {f}")
    
    if failed:
        print("\nFailed files:")
        for f, err in failed:
            print(f"  - {f}")
            print(f"    Error: {err}")
    
    return len(failed) == 0

if __name__ == "__main__":
    # Run from supplier_selection_app directory
    success = migrate_all_projects('.')
    
    if success:
        print("\n✓ All projects migrated successfully!")
    else:
        print("\n⚠ Some migrations failed - see errors above")
        exit(1)
