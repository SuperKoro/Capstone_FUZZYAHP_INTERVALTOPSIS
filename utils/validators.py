"""
Input Validators Module
Provides validation functions for user inputs
"""

import re
from typing import Optional


class Validators:
    """Input validation utilities"""
    
    @staticmethod
    def validate_project_name(name: str) -> tuple[bool, Optional[str]]:
        """
        Validate project name
        
        Args:
            name: Project name to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not name or not name.strip():
            return False, "Project name cannot be empty"
        
        if len(name) > 100:
            return False, "Project name must be less than 100 characters"
        
        # Check for invalid characters
        if re.search(r'[<>:"/\\|?*]', name):
            return False, "Project name contains invalid characters"
        
        return True, None
    
    @staticmethod
    def validate_criterion_name(name: str) -> tuple[bool, Optional[str]]:
        """Validate criterion name"""
        if not name or not name.strip():
            return False, "Criterion name cannot be empty"
        
        if len(name) > 100:
            return False, "Criterion name must be less than 100 characters"
        
        return True, None
    
    @staticmethod
    def validate_alternative_name(name: str) -> tuple[bool, Optional[str]]:
        """Validate alternative name"""
        if not name or not name.strip():
            return False, "Alternative name cannot be empty"
        
        if len(name) > 100:
            return False, "Alternative name must be less than 100 characters"
        
        return True, None
    
    @staticmethod
    def validate_expert_name(name: str) -> tuple[bool, Optional[str]]:
        """Validate expert name"""
        if not name or not name.strip():
            return False, "Expert name cannot be empty"
        
        if len(name) > 100:
            return False, "Expert name must be less than 100 characters"
        
        return True, None
    
    @staticmethod
    def validate_scale_value(value: int) -> tuple[bool, Optional[str]]:
        """Validate AHP scale value"""
        if value == 0:
            return False, "Scale value cannot be 0"
        
        if value < -9 or value > 9:
            return False, "Scale value must be between -9 and 9"
        
        return True, None
    
    @staticmethod
    def validate_minimum_criteria(count: int) -> tuple[bool, Optional[str]]:
        """Validate minimum number of criteria"""
        if count < 2:
            return False, "At least 2 criteria are required"
        
        return True, None
    
    @staticmethod
    def validate_minimum_alternatives(count: int) -> tuple[bool, Optional[str]]:
        """Validate minimum number of alternatives"""
        if count < 2:
            return False, "At least 2 alternatives are required"
        
        return True, None
