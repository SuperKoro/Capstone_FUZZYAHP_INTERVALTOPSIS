"""
Script to remove debug print statements from GUI files
"""
import re
import os

# Files to clean
files_to_clean = [
    'gui/topsis_tab.py',
    'gui/ahp_tab.py',
    'gui/main_window.py',
    'gui/sensitivity_tab.py'
]

def remove_print_statements(filepath):
    """Remove print() statements from a Python file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_lines = content.split('\n')
    cleaned_lines = []
    
    for line in original_lines:
        # Skip lines that are just print statements
        stripped = line.lstrip()
        if stripped.startswith('print(') or stripped.startswith('print '):
            # Check if it's a complete print statement on one line
            if stripped.count('(') == stripped.count(')'):
                # Skip this line (it's a debug print)
                continue
        
        cleaned_lines.append(line)
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(cleaned_lines))
    
    removed = len(original_lines) - len(cleaned_lines)
    return removed

if __name__ == '__main__':
    total_removed = 0
    for filepath in files_to_clean:
        if os.path.exists(filepath):
            removed = remove_print_statements(filepath)
            print(f"✓ {filepath}: Removed {removed} print statements")
            total_removed += removed
        else:
            print(f"✗ {filepath}: File not found")
    
    print(f"\n✅ Total: Removed {total_removed} debug print statements")
