from abc import ABC, abstractmethod
from typing import List, Optional, Callable

class Command(ABC):
    """Base class for all undoable commands"""
    
    @abstractmethod
    def execute(self) -> bool:
        """Execute the command. Returns True if successful."""
        pass
    
    @abstractmethod
    def undo(self) -> bool:
        """Undo the command. Returns True if successful."""
        pass
    
    @abstractmethod
    def description(self) -> str:
        """Description of the command for UI"""
        pass

class UndoManager:
    """Manages undo/redo stacks"""
    
    def __init__(self, max_history: int = 50):
        self.undo_stack: List[Command] = []
        self.redo_stack: List[Command] = []
        self.max_history = max_history
        self.on_stack_change: Optional[Callable] = None
        
    def execute(self, command: Command) -> bool:
        """Execute a new command and add to undo stack"""
        if command.execute():
            self.undo_stack.append(command)
            self.redo_stack.clear() # Clear redo stack on new action
            
            # Limit history
            if len(self.undo_stack) > self.max_history:
                self.undo_stack.pop(0)
                
            self._notify_change()
            return True
        return False
    
    def undo(self) -> bool:
        """Undo the last command"""
        if not self.undo_stack:
            return False
            
        command = self.undo_stack.pop()
        if command.undo():
            self.redo_stack.append(command)
            self._notify_change()
            return True
        else:
            # If undo fails, put it back? Or discard? 
            # Usually if undo fails, state is inconsistent.
            # For now, let's assume it might be recoverable or just log error
            self.undo_stack.append(command)
            return False
            
    def redo(self) -> bool:
        """Redo the last undone command"""
        if not self.redo_stack:
            return False
            
        command = self.redo_stack.pop()
        if command.execute():
            self.undo_stack.append(command)
            self._notify_change()
            return True
        else:
            self.redo_stack.append(command)
            return False
            
    def can_undo(self) -> bool:
        return len(self.undo_stack) > 0
        
    def can_redo(self) -> bool:
        return len(self.redo_stack) > 0
        
    def undo_description(self) -> str:
        if self.undo_stack:
            return f"Undo {self.undo_stack[-1].description()}"
        return "Undo"
        
    def redo_description(self) -> str:
        if self.redo_stack:
            return f"Redo {self.redo_stack[-1].description()}"
        return "Redo"
        
    def clear(self):
        """Clear history (e.g. on file load)"""
        self.undo_stack.clear()
        self.redo_stack.clear()
        self._notify_change()
        
    def _notify_change(self):
        if self.on_stack_change:
            self.on_stack_change()
