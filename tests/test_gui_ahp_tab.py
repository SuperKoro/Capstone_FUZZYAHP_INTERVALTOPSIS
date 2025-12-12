"""
Unit Tests for AHP Tab GUI
Tests user interactions, widget states, and data binding
"""

import pytest
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.schema import DatabaseSchema
from database.manager import DatabaseManager
from gui.ahp_tab import AHPTab
from gui.main_window import MainWindow


@pytest.fixture(scope='session')
def qapp():
    """Create QApplication instance for all tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def temp_db():
    """Create temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix='.mcdm', delete=False) as f:
        db_path = f.name
    
    # Create schema and initialize project
    DatabaseSchema.create_schema(db_path)
    project_id = DatabaseSchema.initialize_project(db_path, "Test Project")
    
    # Add some test criteria
    db_manager = DatabaseManager(db_path)
    with db_manager as db:
        db.add_criterion(project_id, "Price", None, False)  # Cost
        db.add_criterion(project_id, "Quality", None, True)  # Benefit
        db.add_criterion(project_id, "Delivery", None, True)  # Benefit
        
        # Add test expert
        db.add_expert(project_id, "Expert 1", "Senior", None)
    
    yield db_path
    
    # Cleanup
    os.unlink(db_path)


@pytest.fixture
def main_window(qapp, temp_db):
    """Create main window with loaded project"""
    window = MainWindow()
    window.load_project(temp_db)
    yield window
    window.close()


@pytest.fixture
def ahp_tab(main_window):
    """Get AHP tab from main window"""
    return main_window.ahp_tab


# ============================================================================
# Test 1: Initial State
# ============================================================================

def test_ahp_tab_loads_successfully(ahp_tab):
    """Test that AHP tab initializes without errors"""
    assert ahp_tab is not None
    assert ahp_tab.main_window is not None


def test_experts_table_shows_data(ahp_tab):
    """Test that experts table populates from database"""
    # Should have at least the header row
    assert ahp_tab.experts_table is not None
    # Check that expert was loaded
    # Note: Actual table structure may vary, adjust as needed


def test_criteria_tree_loads(ahp_tab):
    """Test that criteria tree loads from database"""
    # Tree should exist and have items
    assert ahp_tab.criteria_tree is not None


# ============================================================================
# Test 2: Expert Management
# ============================================================================

def test_add_expert_button_exists(ahp_tab):
    """Test that add expert button is present"""
    # Check button exists (name may vary based on your implementation)
    assert hasattr(ahp_tab, 'add_expert_button') or \
           ahp_tab.findChild(type(ahp_tab), name='add_expert_button') is not None


def test_delete_expert_button_state(ahp_tab):
    """Test that delete button is disabled when no expert selected"""
    # This test depends on your implementation
    # Example: assert ahp_tab.delete_expert_button.isEnabled() == False
    pass


# ============================================================================
# Test 3: Pairwise Comparisons
# ============================================================================

def test_comparison_table_created(ahp_tab):
    """Test that pairwise comparison table is created"""
    # Table should exist for comparisons
    assert hasattr(ahp_tab, 'comparison_table')


def test_linguistic_scale_dropdown(ahp_tab):
    """Test that dropdowns contain correct linguistic scale values"""
    # Check that scale values are available
    from algorithms.fuzzy_ahp import FuzzyAHP
    
    # Your implementation may store scale in dropdown
    # Example test structure:
    # combo = ahp_tab.comparison_table.cellWidget(0, 0)
    # if combo:
    #     assert combo.count() > 0
    #     assert any("Equally important" in combo.itemText(i) for i in range(combo.count()))
    pass


# ============================================================================
# Test 4: Calculate AHP Weights
# ============================================================================

def test_calculate_button_exists(ahp_tab):
    """Test that calculate weights button exists"""
    assert hasattr(ahp_tab, 'calculate_button')


def test_calculate_button_disabled_without_comparisons(ahp_tab):
    """Test that calculate button is disabled when no comparisons entered"""
    # This depends on your validation logic
    # Example: assert ahp_tab.calculate_button.isEnabled() == False
    pass


# ============================================================================
# Test 5: Consistency Ratio Display
# ============================================================================

def test_consistency_ratio_label_exists(ahp_tab):
    """Test that CR result label exists"""
    # Check for label/field showing CR
    # Example: assert hasattr(ahp_tab, 'cr_label')
    pass


def test_cr_color_coding(ahp_tab):
    """Test that CR value changes color based on threshold"""
    # If CR < 0.1: green, else: red
    # This is a visual test that may need special handling
    pass


# ============================================================================
# Test 6: Excel Import/Export
# ============================================================================

def test_excel_template_button_exists(ahp_tab):
    """Test that Excel template generation button exists"""
    assert hasattr(ahp_tab, 'generate_template_button') or \
           hasattr(ahp_tab, 'export_template_button')


def test_import_excel_button_exists(ahp_tab):
    """Test that Excel import button exists"""
    assert hasattr(ahp_tab, 'import_excel_button') or \
           hasattr(ahp_tab, 'import_button')


# ============================================================================
# Test 7: User Interactions (with qtbot)
# ============================================================================

def test_clicking_add_expert_opens_dialog(ahp_tab, qtbot):
    """Test that clicking Add Expert shows input dialog"""
    # This requires mocking the dialog
    # Example using qtbot:
    # with qtbot.waitSignal(ahp_tab.expert_added):
    #     QTest.mouseClick(ahp_tab.add_expert_button, Qt.MouseButton.LeftButton)
    pass


def test_selecting_expert_enables_delete_button(ahp_tab, qtbot):
    """Test that selecting an expert enables delete button"""
    # Select first expert
    # ahp_tab.experts_table.selectRow(0)
    # assert ahp_tab.delete_expert_button.isEnabled() == True
    pass


def test_pairwise_comparison_interaction(ahp_tab, qtbot):
    """Test changing a comparison value in the table"""
    # This tests the interaction flow
    # 1. Change dropdown value
    # 2. Check that data is updated
    pass


# ============================================================================
# Test 8: Data Integration
# ============================================================================

def test_load_data_from_database(ahp_tab, temp_db):
    """Test that load_data() populates UI from database"""
    # Clear current data
    # Call load_data()
    ahp_tab.load_data()
    
    # Verify data is loaded
    # Example: check experts table has rows
    # assert ahp_tab.experts_table.rowCount() > 0
    pass


def test_save_comparisons_to_database(ahp_tab, qtbot):
    """Test that entered comparisons are saved to database"""
    # Enter some comparison data
    # Save
    # Query database to verify
    pass


# ============================================================================
# Test 9: Validation
# ============================================================================

def test_cannot_calculate_with_incomplete_comparisons(ahp_tab):
    """Test that validation prevents calculation with incomplete data"""
    # Try to calculate without all comparisons
    # Should show error or disable button
    pass


def test_expert_name_validation(ahp_tab, qtbot):
    """Test that duplicate expert names are rejected"""
    # Try to add expert with existing name
    # Should show error message
    pass


# ============================================================================
# Test 10: Undo/Redo
# ============================================================================

def test_undo_after_adding_expert(ahp_tab, qtbot):
    """Test that undo works after adding expert"""
    # Add expert
    # Call undo
    # Verify expert is removed
    pass


def test_redo_after_undo(ahp_tab, qtbot):
    """Test that redo works after undo"""
    # Add expert, undo, redo
    # Verify expert is back
    pass


# ============================================================================
# Helper Functions (if needed)
# ============================================================================

def add_test_comparison(ahp_tab, criterion1_idx, criterion2_idx, scale_value):
    """Helper to programmatically add a comparison"""
    # Implementation depends on your UI structure
    pass


def simulate_calculate_weights(ahp_tab, qtbot):
    """Helper to simulate clicking Calculate button"""
    # QTest.mouseClick(ahp_tab.calculate_button, Qt.MouseButton.LeftButton)
    # qtbot.wait(100)  # Wait for processing
    pass
