"""
Manual Migration Runner
Run this script to migrate your .mcdm database file to support Scenarios feature
"""
import sys
import os
from database.database_migration import migrate_to_scenarios, check_migration_needed


def main():
    print("\n" + "="*60)
    print("DATABASE MIGRATION TOOL - Scenarios Feature")
    print("="*60 + "\n")
    
    # Find all .mcdm files in current directory
    mcdm_files = [f for f in os.listdir('.') if f.endswith('.mcdm')]
    
    if not mcdm_files:
        print("❌ No .mcdm files found in current directory")
        print("Please run this script from the project directory containing your .mcdm file")
        return
    
    print(f"Found {len(mcdm_files)} .mcdm file(s):")
    for i, f in enumerate(mcdm_files, 1):
        print(f"  {i}. {f}")
    
    print()
    
    # Migrate all files
    success_count = 0
    already_migrated_count = 0
    failed_count = 0
    
    for mcdm_file in mcdm_files:
        print(f"\n{'='*60}")
        print(f"Processing: {mcdm_file}")
        print('='*60)
        
        try:
            if check_migration_needed(mcdm_file):
                print(f"✓ Migration needed for {mcdm_file}")
                print(f"  Starting migration...")
                migrate_to_scenarios(mcdm_file)
                print(f"✓ Successfully migrated {mcdm_file}")
                success_count += 1
            else:
                print(f"✓ {mcdm_file} already migrated - no action needed")
                already_migrated_count += 1
        except Exception as e:
            print(f"❌ Failed to migrate {mcdm_file}: {e}")
            failed_count += 1
    
    # Summary
    print(f"\n{'='*60}")
    print("MIGRATION SUMMARY")
    print('='*60)
    print(f"✓ Successfully migrated: {success_count}")
    print(f"✓ Already migrated: {already_migrated_count}")
    if failed_count > 0:
        print(f"❌ Failed: {failed_count}")
    print('='*60)
    
    if failed_count > 0:
        print("\n⚠️  Some migrations failed. Please check the error messages above.")
        print("You may need to backup and restore your database manually.")
    elif success_count > 0:
        print("\n✓ Migration complete! Your database(s) now support Scenarios feature.")
        print("You can now start the application: python main.py")
    else:
        print("\n✓ All databases are already up to date.")


if __name__ == "__main__":
    main()
