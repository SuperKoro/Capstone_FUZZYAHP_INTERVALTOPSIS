"""
Fix Recent Projects - Add current .mcdm files to recent projects list
"""

import os
import json
from datetime import datetime
import sqlite3

# Configuration
config_dir = os.path.join(os.path.expanduser("~"), ".gemini", "supplier_selection_app")
config_file = os.path.join(config_dir, "projects.json")

# Ensure config directory exists
if not os.path.exists(config_dir):
    os.makedirs(config_dir)
    print(f"Created config directory: {config_dir}")

# Find all .mcdm files in current directory
mcdm_files = []
for file in os.listdir('.'):
    if file.endswith('.mcdm'):
        full_path = os.path.abspath(file)
        
        # Try to get project name from database
        try:
            conn = sqlite3.connect(full_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM projects WHERE id = 1")
            result = cursor.fetchone()
            project_name = result[0] if result else os.path.splitext(file)[0]
            conn.close()
        except Exception as e:
            print(f"Could not read project name from {file}: {e}")
            project_name = os.path.splitext(file)[0]
        
        # Get last modified time
        mtime = os.path.getmtime(full_path)
        last_modified = datetime.fromtimestamp(mtime).isoformat()
        
        mcdm_files.append({
            'name': project_name,
            'path': full_path,
            'last_opened': last_modified,
            'last_modified': last_modified
        })
        
        print(f"Found: {project_name} ({file})")

if mcdm_files:
    # Sort by last modified (newest first)
    mcdm_files.sort(key=lambda x: x['last_modified'], reverse=True)
    
    # Save to projects.json
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(mcdm_files, f, indent=4, ensure_ascii=False)
    
    print(f"\n✓ Successfully added {len(mcdm_files)} project(s) to recent list")
    print(f"✓ Config file: {config_file}")
    
    # Show content
    print("\nRecent projects:")
    for i, p in enumerate(mcdm_files, 1):
        print(f"{i}. {p['name']}")
        print(f"   Path: {p['path']}")
        print(f"   Modified: {p['last_modified']}")
else:
    print("No .mcdm files found in current directory")
