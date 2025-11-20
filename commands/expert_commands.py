from utils.undo_manager import Command
from typing import Optional

class AddExpertCommand(Command):
    def __init__(self, db_manager, project_id: int, name: str, weight: Optional[float] = None):
        self.db = db_manager
        self.project_id = project_id
        self.name = name
        self.weight = weight
        self.expert_id = None
        
    def execute(self) -> bool:
        with self.db as database:
            self.expert_id = database.add_expert(
                self.project_id, self.name, weight=self.weight
            )
        return True
    
    def undo(self) -> bool:
        if self.expert_id is None:
            return False
        with self.db as database:
            database.delete_expert(self.expert_id)
        return True
    
    def description(self) -> str:
        return f"Add Expert '{self.name}'"

class DeleteExpertCommand(Command):
    def __init__(self, db_manager, expert_id: int):
        self.db = db_manager
        self.expert_id = expert_id
        self.expert_data = None
        self.comparisons = None
        
    def execute(self) -> bool:
        # Save state before deletion
        with self.db as database:
            # Get expert details
            cursor = database.conn.cursor()
            cursor.execute("SELECT * FROM experts WHERE id = ?", (self.expert_id,))
            row = cursor.fetchone()
            if row:
                self.expert_data = dict(row)
            
            # Get comparisons
            self.comparisons = database.get_ahp_comparisons(
                self.expert_data['project_id'], expert_id=self.expert_id
            )
            
            # Delete
            database.delete_ahp_comparisons_by_expert(self.expert_id)
            database.delete_expert(self.expert_id)
        return True
    
    def undo(self) -> bool:
        if not self.expert_data:
            return False
            
        with self.db as database:
            # Restore expert (we need to force the ID to be the same)
            # Standard add_expert doesn't allow setting ID, so we might need raw SQL
            # or update add_expert. Let's use raw SQL for restoration to keep ID
            cursor = database.conn.cursor()
            cursor.execute(
                "INSERT INTO experts (id, project_id, name, expertise_level, weight) VALUES (?, ?, ?, ?, ?)",
                (self.expert_id, self.expert_data['project_id'], self.expert_data['name'], 
                 self.expert_data['expertise_level'], self.expert_data['weight'])
            )
            
            # Restore comparisons
            for comp in self.comparisons:
                database.add_ahp_comparison(
                    comp['project_id'], comp['expert_id'], 
                    comp['criterion1_id'], comp['criterion2_id'],
                    comp['fuzzy_l'], comp['fuzzy_m'], comp['fuzzy_u']
                )
            
            database.conn.commit()
        return True
    
    def description(self) -> str:
        name = self.expert_data['name'] if self.expert_data else "Expert"
        return f"Delete Expert '{name}'"

class SetExpertWeightCommand(Command):
    def __init__(self, db_manager, expert_id: int, new_weight: Optional[float]):
        self.db = db_manager
        self.expert_id = expert_id
        self.new_weight = new_weight
        self.old_weight = None
        self.expert_name = "Expert"
        
    def execute(self) -> bool:
        with self.db as database:
            # Get current weight first
            cursor = database.conn.cursor()
            cursor.execute("SELECT name, weight FROM experts WHERE id = ?", (self.expert_id,))
            row = cursor.fetchone()
            if row:
                self.expert_name = row['name']
                self.old_weight = row['weight']
            
            database.update_expert_weight(self.expert_id, self.new_weight)
        return True
    
    def undo(self) -> bool:
        with self.db as database:
            database.update_expert_weight(self.expert_id, self.old_weight)
        return True
    
    def description(self) -> str:
        return f"Change Weight for '{self.expert_name}'"

class RenameExpertCommand(Command):
    """Command to rename an expert"""
    def __init__(self, db_manager, expert_id: int, new_name: str):
        self.db = db_manager
        self.expert_id = expert_id
        self.new_name = new_name
        self.old_name = None
        
    def execute(self) -> bool:
        with self.db as database:
            # Get current name first
            cursor = database.conn.cursor()
            cursor.execute("SELECT name FROM experts WHERE id = ?", (self.expert_id,))
            row = cursor.fetchone()
            if row:
                self.old_name = row['name']
            
            # Update name
            cursor.execute(
                "UPDATE experts SET name = ? WHERE id = ?",
                (self.new_name, self.expert_id)
            )
            database.conn.commit()
        return True
    
    def undo(self) -> bool:
        if self.old_name is None:
            return False
            
        with self.db as database:
            cursor = database.conn.cursor()
            cursor.execute(
                "UPDATE experts SET name = ? WHERE id = ?",
                (self.old_name, self.expert_id)
            )
            database.conn.commit()
        return True
    
    def description(self) -> str:
        return f"Rename Expert '{self.old_name}' to '{self.new_name}'"
