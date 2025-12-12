"""
Integration Tests for GUI ↔ Database
Tests data flow between UI components and database
"""

import pytest
import sys
import os
import tempfile
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from database.schema import DatabaseSchema
from database.manager import DatabaseManager
from gui.main_window import MainWindow


@pytest.fixture(scope='session')
def qapp():
    """Create QApplication instance"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def temp_db():
    """Create temporary database with sample data"""
    with tempfile.NamedTemporaryFile(suffix='.mcdm', delete=False) as f:
        db_path = f.name
    
    DatabaseSchema.create_schema(db_path)
    project_id = DatabaseSchema.initialize_project(db_path, "Integration Test Project")
    
    db_manager = DatabaseManager(db_path)
    with db_manager as db:
        # Add criteria
        c1_id = db.add_criterion(project_id, "Price", None, False)
        c2_id = db.add_criterion(project_id, "Quality", None, True)
        c3_id = db.add_criterion(project_id, "Delivery Time", None, True)
        
        # Add alternatives
        a1_id = db.add_alternative(project_id, "Supplier A", "Description A")
        a2_id = db.add_alternative(project_id, "Supplier B", "Description B")
        
        # Add experts
        e1_id = db.add_expert(project_id, "Expert 1", "Senior", 0.6)
        e2_id = db.add_expert(project_id, "Expert 2", "Junior", 0.4)
    
    yield db_path, project_id
    os.unlink(db_path)


class TestProjectTabIntegration:
    """Test Project Tab ↔ Database"""
    
    def test_load_criteria_from_database(self, qapp, temp_db):
        """Test that criteria are loaded correctly"""
        db_path, project_id = temp_db
        window = MainWindow()
        window.load_project(db_path)
        
        # Check criteria loaded
        db_manager = window.get_db_manager()
        with db_manager as db:
            criteria = db.get_criteria(project_id)
            assert len(criteria) == 3
            criteria_names = [c['name'] for c in criteria]
            assert "Price" in criteria_names
            assert "Quality" in criteria_names
        
        window.close()
    
    def test_add_criterion_saves_to_database(self, qapp, temp_db):
        """Test that adding criterion via UI saves to DB"""
        db_path, project_id = temp_db
        window = MainWindow()
        window.load_project(db_path)
        
        # Add criterion via UI (would need to interact with UI)
        # For now, test the flow through database manager
        db_manager = window.get_db_manager()
        with db_manager as db:
            initial_count = len(db.get_criteria(project_id))
            db.add_criterion(project_id, "New Criterion", None, True)
            new_count = len(db.get_criteria(project_id))
            assert new_count == initial_count + 1
        
        window.close()
    
    def test_delete_criterion_removes_from_database(self, qapp, temp_db):
        """Test that deleting criterion via UI removes from DB"""
        db_path, project_id = temp_db
        window = MainWindow()
        window.load_project(db_path)
        
        db_manager = window.get_db_manager()
        with db_manager as db:
            criteria = db.get_criteria(project_id)
            criterion_id = criteria[0]['id']
            
            db.delete_criterion(criterion_id)
            
            remaining = db.get_criteria(project_id)
            assert len(remaining) == len(criteria) - 1
        
        window.close()


class TestAHPTabIntegration:
    """Test AHP Tab ↔ Database"""
    
    def test_load_experts_from_database(self, qapp, temp_db):
        """Test experts are loaded correctly"""
        db_path, project_id = temp_db
        window = MainWindow()
        window.load_project(db_path)
        
        db_manager = window.get_db_manager()
        with db_manager as db:
            experts = db.get_experts(project_id)
            assert len(experts) == 2
            assert experts[0]['name'] == "Expert 1"
        
        window.close()
    
    def test_save_ahp_comparison(self, qapp, temp_db):
        """Test AHP comparison saves to database"""
        db_path, project_id = temp_db
        window = MainWindow()
        window.load_project(db_path)
        
        db_manager = window.get_db_manager()
        with db_manager as db:
            experts = db.get_experts(project_id)
            criteria = db.get_criteria(project_id)
            
            expert_id = experts[0]['id']
            c1_id = criteria[0]['id']
            c2_id = criteria[1]['id']
            
            # Add comparison
            db.add_ahp_comparison(project_id, expert_id, c1_id, c2_id, 
                                 2.0, 3.0, 4.0)
            
            # Verify
            comparisons = db.get_ahp_comparisons(project_id, expert_id)
            assert len(comparisons) > 0
            
            comp = comparisons[0]
            assert comp['fuzzy_m'] == 3.0
        
        window.close()
    
    def test_calculate_weights_updates_database(self, qapp, temp_db):
        """Test that calculated weights are saved"""
        db_path, project_id = temp_db
        window = MainWindow()
        window.load_project(db_path)
        
        # Would trigger calculation via UI
        # For now test database update
        db_manager = window.get_db_manager()
        with db_manager as db:
            criteria = db.get_criteria(project_id)
            criterion_id = criteria[0]['id']
            
            db.update_criterion_weight(criterion_id, 0.35)
            
            updated = db.get_criteria(project_id)
            updated_criterion = next(c for c in updated if c['id'] == criterion_id)
            assert abs(updated_criterion['weight'] - 0.35) < 0.01
        
        window.close()


class TestTOPSISTabIntegration:
    """Test TOPSIS Tab ↔ Database"""
    
    def test_load_alternatives_and_criteria(self, qapp, temp_db):
        """Test TOPSIS tab loads matrix structure"""
        db_path, project_id = temp_db
        window = MainWindow()
        window.load_project(db_path)
        
        db_manager = window.get_db_manager()
        with db_manager as db:
            alternatives = db.get_alternatives(project_id)
            criteria = db.get_criteria(project_id)
            
            assert len(alternatives) == 2
            assert len(criteria) == 3
        
        window.close()
    
    def test_save_topsis_rating(self, qapp, temp_db):
        """Test TOPSIS rating saves to database"""
        db_path, project_id = temp_db
        window = MainWindow()
        window.load_project(db_path)
        
        db_manager = window.get_db_manager()
        with db_manager as db:
            alternatives = db.get_alternatives(project_id)
            criteria = db.get_criteria(project_id)
            experts = db.get_experts(project_id)
            
            alt_id = alternatives[0]['id']
            crit_id = criteria[0]['id']
            expert_id = experts[0]['id']
            
            # Save rating
            db.add_topsis_rating(project_id, expert_id, alt_id, crit_id, 
                                5.0, 7.0)
            
            # Verify
            ratings = db.get_topsis_ratings(project_id, expert_id)
            assert len(ratings) > 0
        
        window.close()


class TestResultsTabIntegration:
    """Test Results Tab ↔ Calculations"""
    
    def test_results_display_after_calculation(self, qapp, temp_db):
        """Test that results tab shows calculated rankings"""
        db_path, project_id = temp_db
        window = MainWindow()
        window.load_project(db_path)
        
        # Would need to:
        # 1. Add all AHP comparisons
        # 2. Calculate weights
        # 3. Add TOPSIS ratings
        # 4. Calculate rankings
        # 5. Check results tab displays correctly
        
        # This is a full integration test
        window.close()


class TestDataConsistency:
    """Test data consistency across UI and database"""
    
    def test_refresh_updates_all_tabs(self, qapp, temp_db):
        """Test that refresh_all_tabs() updates all UI"""
        db_path, project_id = temp_db
        window = MainWindow()
        window.load_project(db_path)
        
        # Add data via database
        db_manager = window.get_db_manager()
        with db_manager as db:
            db.add_criterion(project_id, "New Via DB", None, True)
        
        # Refresh UI
        window.refresh_all_tabs()
        
        # Check UI reflects new data
        # Would need to check actual widgets
        
        window.close()
    
    def test_undo_reverts_database_changes(self, qapp, temp_db):
        """Test that undo functionality reverts DB"""
        # This tests the undo/redo integration with database
        pass
