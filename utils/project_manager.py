"""
Project Manager Module
Handles persistence of recent projects list
"""

import json
import os
from datetime import datetime

class ProjectManager:
    """Manages the list of recent projects"""
    
    def __init__(self):
        self.config_dir = os.path.join(os.path.expanduser("~"), ".gemini", "supplier_selection_app")
        self.config_file = os.path.join(self.config_dir, "projects.json")
        self.projects = []
        
        self._ensure_config_dir()
        self.load_projects()
    
    def _ensure_config_dir(self):
        """Ensure configuration directory exists"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
    
    def load_projects(self):
        """Load projects from config file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.projects = json.load(f)
            except Exception:
                self.projects = []
        else:
            self.projects = []
            
    def save_projects(self):
        """Save projects to config file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.projects, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving projects: {e}")
            
    def add_project(self, name, path):
        """Add or update a project in the list
        
        Args:
            name: Project name
            path: Absolute path to project file
        """
        # Remove if already exists (to update position/info)
        self.projects = [p for p in self.projects if p['path'] != path]
        
        # Add to top
        project_info = {
            'name': name,
            'path': path,
            'last_opened': datetime.now().isoformat()
        }
        self.projects.insert(0, project_info)
        
        # Keep only last 20 projects (increased for Excel view)
        if len(self.projects) > 20:
            self.projects = self.projects[:20]
            
        self.save_projects()
        
    def remove_project(self, path):
        """Remove a project from the list"""
        self.projects = [p for p in self.projects if p['path'] != path]
        self.save_projects()
        
    def get_recent_projects(self):
        """Get list of recent projects"""
        # Verify files still exist
        valid_projects = []
        changed = False
        
        for p in self.projects:
            if os.path.exists(p['path']):
                # Update last modified time from file system if possible, 
                # otherwise use last_opened
                try:
                    mtime = os.path.getmtime(p['path'])
                    p['last_modified'] = datetime.fromtimestamp(mtime).isoformat()
                except:
                    p['last_modified'] = p['last_opened']
                valid_projects.append(p)
            else:
                changed = True
        
        if changed:
            self.projects = valid_projects
            self.save_projects()
            
        return self.projects
