"""
Database Schema Module
Defines SQLite database schema for the Supplier Selection Application
"""

import sqlite3
from typing import Optional


class DatabaseSchema:
    """Manages database schema creation and initialization"""
    
    @staticmethod
    def create_schema(db_path: str) -> None:
        """
        Create all necessary tables for the application
        
        Args:
            db_path: Path to the SQLite database file
        """
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Projects table - stores project metadata
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Criteria table - stores evaluation criteria with hierarchy support
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS criteria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                parent_id INTEGER,
                weight REAL DEFAULT 0.0,
                is_benefit BOOLEAN DEFAULT 1,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (parent_id) REFERENCES criteria(id) ON DELETE CASCADE,
                UNIQUE(project_id, name)
            )
        """)
        
        # Alternatives table - stores suppliers/alternatives
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alternatives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                UNIQUE(project_id, name)
            )
        """)
        
        # Experts table - stores expert profiles
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS experts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                expertise_level TEXT,
                weight REAL DEFAULT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                UNIQUE(project_id, name)
            )
        """)
        
        # AHP Comparisons table - stores pairwise comparison judgments
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ahp_comparisons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                expert_id INTEGER NOT NULL,
                criterion1_id INTEGER NOT NULL,
                criterion2_id INTEGER NOT NULL,
                fuzzy_l REAL NOT NULL,
                fuzzy_m REAL NOT NULL,
                fuzzy_u REAL NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (expert_id) REFERENCES experts(id) ON DELETE CASCADE,
                FOREIGN KEY (criterion1_id) REFERENCES criteria(id) ON DELETE CASCADE,
                FOREIGN KEY (criterion2_id) REFERENCES criteria(id) ON DELETE CASCADE,
                UNIQUE(project_id, expert_id, criterion1_id, criterion2_id)
            )
        """)
        
        # TOPSIS Ratings table - stores performance ratings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS topsis_ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                expert_id INTEGER,
                alternative_id INTEGER NOT NULL,
                criterion_id INTEGER NOT NULL,
                rating_lower REAL NOT NULL,
                rating_upper REAL NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (expert_id) REFERENCES experts(id) ON DELETE CASCADE,
                FOREIGN KEY (alternative_id) REFERENCES alternatives(id) ON DELETE CASCADE,
                FOREIGN KEY (criterion_id) REFERENCES criteria(id) ON DELETE CASCADE
            )
        """)
        
        # Create indexes for better query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_criteria_project ON criteria(project_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_alternatives_project ON alternatives(project_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_experts_project ON experts(project_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ahp_project ON ahp_comparisons(project_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_topsis_project ON topsis_ratings(project_id)")
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def initialize_project(db_path: str, project_name: str, description: str = "") -> int:
        """
        Initialize a new project in the database
        
        Args:
            db_path: Path to the SQLite database file
            project_name: Name of the project
            description: Project description
            
        Returns:
            Project ID
        """
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO projects (name, description) VALUES (?, ?)",
            (project_name, description)
        )
        project_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return project_id
