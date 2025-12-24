"""
Main Window Module
Creates the main application window with tabbed interface
"""

from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QMenuBar, QMenu, QFileDialog,
                             QMessageBox, QStatusBar, QToolBar, QWidget, QVBoxLayout, QApplication, QDialog)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt, QTimer
import os

from database.schema import DatabaseSchema
from database.manager import DatabaseManager
from gui.project_tab import ProjectTab
from gui.ahp_tab import AHPTab
from gui.topsis_tab import TOPSISTab
from gui.results_tab import ResultsTab
from gui.sensitivity_tab import SensitivityAnalysisTab
from gui.methodology_dialog import MethodologyDialog
from gui.user_guide_dialog import UserGuideDialog
from gui.welcome_dialog import WelcomeDialog
from utils.undo_manager import UndoManager
from utils.project_manager import ProjectManager


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        self.current_project_path = None
        self.db_manager = None
        self.project_id = None
        self.current_scenario_id = 1  # NEW: Default to Base Scenario
        self.undo_manager = UndoManager()
        self.undo_manager.on_stack_change = self.update_undo_redo_actions
        self.project_manager = ProjectManager()
        
        # Scenario UI components (initialized in create_toolbar)
        self.scenario_combo = None
        self.scenario_new_btn = None
        
        self.init_ui()
        
        # Show welcome dialog after window is shown
        QTimer.singleShot(100, self.show_welcome_dialog)
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Supplier Selection - Fuzzy AHP & Interval TOPSIS")
        self.setGeometry(100, 100, 1200, 800)
        
        # Set window icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "logo.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Create tabs
        self.project_tab = ProjectTab(self)
        self.ahp_tab = AHPTab(self)
        self.topsis_tab = TOPSISTab(self)
        self.results_tab = ResultsTab(self)
        self.sensitivity_tab = SensitivityAnalysisTab(self)
        
        self.tabs.addTab(self.project_tab, "Project Setup")
        self.tabs.addTab(self.ahp_tab, "Fuzzy AHP Evaluation")
        self.tabs.addTab(self.topsis_tab, "TOPSIS Rating")
        self.tabs.addTab(self.results_tab, "Results")
        self.tabs.addTab(self.sensitivity_tab, "Sensitivity Analysis")
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - No project loaded")
        
        # Disable tabs until project is loaded
        self.set_tabs_enabled(False)
    
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()
        
        # Home Action (Directly on Menu Bar)
        home_action = QAction("Home", self)
        home_action.setStatusTip("Go to Home Screen")
        home_action.triggered.connect(self.show_welcome_dialog)
        menubar.addAction(home_action)
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        save_action = QAction("Save Project", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save Project As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_project_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("Export Results to Excel", self)
        export_action.triggered.connect(self.export_results)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        self.undo_action = QAction("Undo", self)
        self.undo_action.setShortcut("Ctrl+Z")
        self.undo_action.triggered.connect(self.undo)
        self.undo_action.setEnabled(False)
        edit_menu.addAction(self.undo_action)
        
        self.redo_action = QAction("Redo", self)
        self.redo_action.setShortcuts(["Ctrl+Y", "Ctrl+Shift+Z"])
        self.redo_action.triggered.connect(self.redo)
        self.redo_action.setEnabled(False)
        edit_menu.addAction(self.redo_action)
        
        # Methodology menu
        methodology_menu = menubar.addMenu("Methodology")
        
        fuzzy_ahp_action = QAction("Fuzzy AHP", self)
        fuzzy_ahp_action.triggered.connect(lambda: self.show_methodology(0))
        methodology_menu.addAction(fuzzy_ahp_action)
        
        interval_topsis_action = QAction("Interval TOPSIS", self)
        interval_topsis_action.triggered.connect(lambda: self.show_methodology(1))
        methodology_menu.addAction(interval_topsis_action)
        
        methodology_menu.addSeparator()
        
        view_all_action = QAction("View All Methodologies", self)
        view_all_action.triggered.connect(lambda: self.show_methodology())
        methodology_menu.addAction(view_all_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        user_guide_action = QAction("User Guide", self)
        user_guide_action.setShortcut("F1")
        user_guide_action.triggered.connect(self.show_user_guide)
        help_menu.addAction(user_guide_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def update_recent_projects_menu(self):
        """Update the recent projects submenu (Not used in menu anymore, but kept for potential future use)"""
        pass

    def create_toolbar(self):
        """Create the toolbar"""
        from PyQt6.QtWidgets import QLabel, QComboBox, QPushButton
        
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        new_action = QAction("New", self)
        new_action.triggered.connect(self.new_project)
        toolbar.addAction(new_action)
        
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_project)
        toolbar.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_project)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        export_action = QAction("Export", self)
        export_action.triggered.connect(self.export_results)
        toolbar.addAction(export_action)
        
        toolbar.addSeparator()
        
        self.undo_tool_action = QAction("Undo", self)
        self.undo_tool_action.triggered.connect(self.undo)
        self.undo_tool_action.setEnabled(False)
        toolbar.addAction(self.undo_tool_action)
        
        self.redo_tool_action = QAction("Redo", self)
        self.redo_tool_action.triggered.connect(self.redo)
        self.redo_tool_action.setEnabled(False)
        toolbar.addAction(self.redo_tool_action)
        
        # ============================================================
        # NEW: Scenario Selector (Option B+ Implementation)
        # ============================================================
        toolbar.addSeparator()
        
        # Label
        scenario_label = QLabel(" Scenario: ")
        toolbar.addWidget(scenario_label)
        
        # ComboBox for scenario selection
        self.scenario_combo = QComboBox()
        self.scenario_combo.setMinimumWidth(200)
        self.scenario_combo.setToolTip("Select active scenario")
        self.scenario_combo.setStyleSheet("""
            QComboBox {
                color: #2c3e50;
                font-weight: bold;
                font-size: 11pt;
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QComboBox:hover {
                border: 1px solid #3498db;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                color: #2c3e50;
                background-color: white;
                selection-background-color: #3498db;
                selection-color: white;
            }
        """)
        self.scenario_combo.currentIndexChanged.connect(self.on_scenario_changed)
        toolbar.addWidget(self.scenario_combo)
        
        # New Scenario button
        self.scenario_new_btn = QPushButton("➕")
        self.scenario_new_btn.setToolTip("Create new scenario")
        self.scenario_new_btn.setFixedSize(30, 30)
        self.scenario_new_btn.clicked.connect(self.create_new_scenario)
        self.scenario_new_btn.setEnabled(False)  # Disabled until project loaded
        toolbar.addWidget(self.scenario_new_btn)
        
        # Delete Scenario button
        self.scenario_delete_btn = QPushButton("🗑️")
        self.scenario_delete_btn.setToolTip("Delete current scenario (Base scenario cannot be deleted)")
        self.scenario_delete_btn.setFixedSize(30, 30)
        self.scenario_delete_btn.clicked.connect(self.delete_current_scenario)
        self.scenario_delete_btn.setEnabled(False)  # Disabled until project loaded
        self.scenario_delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        toolbar.addWidget(self.scenario_delete_btn)
        
        # Initially populate with Base Scenario
        self.scenario_combo.addItem("Base Scenario", 1)  # (name, scenario_id)
        self.scenario_combo.setEnabled(False)  # Disabled until project loaded
    
    def show_welcome_dialog(self):
        """Show the welcome dialog"""
        # Always show dialog when requested
        dialog = WelcomeDialog(self.project_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if dialog.action == 'new':
                self.new_project()
            elif dialog.action == 'open':
                self.open_project()
            elif dialog.action == 'open_recent':
                self.load_project(dialog.selected_project_path)
        else:
            # If dialog rejected (Exit clicked)
            # If we don't have a project loaded, close app
            if not self.current_project_path:
                self.close()
            # If we DO have a project loaded, just return to it (dialog closes)

    def new_project(self):
        """Create a new project"""
        from PyQt6.QtWidgets import QInputDialog, QLineEdit
        
        # Ask for project name
        name, ok = QInputDialog.getText(self, "New Project", "Enter project name:")
        
        if ok and name:
            # Ask for save location
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save New Project", name + ".mcdm", "MCDM Project Files (*.mcdm)"
            )
            
            if file_path:
                # Create database
                DatabaseSchema.create_schema(file_path)
                self.project_id = DatabaseSchema.initialize_project(file_path, name)
                
                # Set current project
                self.current_project_path = file_path
                self.db_manager = DatabaseManager(file_path)
                self.undo_manager.clear()
                
                # Add to project manager
                self.project_manager.add_project(name, file_path)
                # self.update_recent_projects_menu() # Removed from menu
                
                # Clear previous results
                if hasattr(self, 'topsis_results'):
                    del self.topsis_results
                
                # Enable tabs and refresh
                self.set_tabs_enabled(True)
                self.refresh_all_tabs()
                
                self.status_bar.showMessage(f"Project: {name} - {file_path}")
                QMessageBox.information(self, "Success", f"Project '{name}' created successfully!")
    
    def open_project(self):
        """Open an existing project"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "", "MCDM Project Files (*.mcdm);;All Files (*)"
        )
        
        if file_path:
            self.load_project(file_path)
    
    def load_project(self, file_path):
        """Load a project from file"""
        try:
            self.current_project_path = file_path
            self.db_manager = DatabaseManager(file_path)
            
            # Get project info
            with self.db_manager as db:
                project = db.get_project()
                if project:
                    self.project_id = project['id']
                    self.setWindowTitle(f"Supplier Selection - {project['name']}")
                    self.status_bar.showMessage(f"Project loaded: {project['name']}")
                    
                    # Load data into tabs (with individual error handling)
                    try:
                        self.project_tab.load_data()
                    except Exception:
                        pass
                    try:
                        self.ahp_tab.load_data()
                    except Exception:
                        pass
                    try:
                        self.topsis_tab.load_data()
                    except Exception:
                        pass
                    try:
                        self.results_tab.load_data()
                    except Exception:
                        pass
                    # Enable tabs
                    self.set_tabs_enabled(True)
                    
                    # NEW: Enable and load scenarios (ALWAYS RUN THIS)
                    self.scenario_combo.setEnabled(True)
                    self.scenario_new_btn.setEnabled(True)
                    # Delete button enabled only for non-base scenarios (will update in load_scenarios)
                    self.scenario_delete_btn.setEnabled(False)
                    self.current_scenario_id = 1  # Reset to Base Scenario
                    
                    try:
                        self.load_scenarios()
                    except Exception:
                        pass
                    # Add to recent projects
                    self.project_manager.add_project(project['name'], file_path)
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load project:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def save_project(self):
        """Save the current project"""
        if self.current_project_path:
            self.status_bar.showMessage(f"Project saved: {self.current_project_path}")
            QMessageBox.information(self, "Success", "Project saved successfully!")
        else:
            self.save_project_as()
    
    def save_project_as(self):
        """Save project with a new name"""
        if not self.db_manager:
            QMessageBox.warning(self, "Warning", "No project to save!")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Project As", "", "MCDM Project Files (*.mcdm)"
        )
        
        if file_path:
            # Copy current database to new location
            import shutil
            shutil.copy(self.current_project_path, file_path)
            self.current_project_path = file_path
            
            # Update project manager
            with self.db_manager as db:
                project = db.get_project()
                if project:
                    self.project_manager.add_project(project['name'], file_path)
                    # self.update_recent_projects_menu() # Removed from menu
            
            self.status_bar.showMessage(f"Project saved as: {file_path}")
            QMessageBox.information(self, "Success", "Project saved successfully!")
    
    def export_results(self):
        """Export results to Excel"""
        if not self.db_manager:
            QMessageBox.warning(self, "Warning", "No project loaded!")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Results", "results.xlsx", "Excel Files (*.xlsx)"
        )
        
        if file_path:
            try:
                self.results_tab.export_to_excel(file_path)
                QMessageBox.information(self, "Success", f"Results exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Supplier Selection App",
            "Supplier Selection Desktop Application\n\n"
            "Version 1.0\n\n"
            "A hybrid MCDM application using:\n"
            "- Fuzzy AHP for criteria weighting\n"
            "- Interval TOPSIS for alternative ranking\n\n"
            "Developed with PyQt6, NumPy, and Pandas"
        )
    
    def show_methodology(self, initial_tab=None):
        """Show methodology dialog
        
        Args:
            initial_tab: Index of tab to show initially (0=Fuzzy AHP, 1=Interval TOPSIS)
                        If None, shows the first tab
        """
        dialog = MethodologyDialog(self)
        if initial_tab is not None:
            dialog.findChild(QTabWidget).setCurrentIndex(initial_tab)
        dialog.exec()

    def show_user_guide(self):
        """Show user guide dialog"""
        dialog = UserGuideDialog(self)
        dialog.exec()

    def set_tabs_enabled(self, enabled: bool):
        """Enable or disable tabs"""
        for i in range(1, self.tabs.count()):
            self.tabs.setTabEnabled(i, enabled)
    
    def refresh_all_tabs(self):
        """Refresh all tabs with current data"""
        self.project_tab.load_data()
        self.ahp_tab.load_data()
        self.topsis_tab.load_data()
        self.results_tab.load_data()
        if hasattr(self, 'sensitivity_tab'):
            self.sensitivity_tab.load_data()
    
    def get_db_manager(self):
        """Get the database manager"""
        return self.db_manager
    
    def get_project_id(self):
        """Get the current project ID"""
        return self.project_id
        
    def get_undo_manager(self):
        """Get the undo manager"""
        return self.undo_manager
    
    def undo(self):
        """Execute undo"""
        if self.undo_manager.undo():
            self.refresh_all_tabs()
            self.status_bar.showMessage("Undone last action")
            
    def redo(self):
        """Execute redo"""
        if self.undo_manager.redo():
            self.refresh_all_tabs()
            self.status_bar.showMessage("Redone last action")
            
    def update_undo_redo_actions(self):
        """Update state of undo/redo actions"""
        can_undo = self.undo_manager.can_undo()
        can_redo = self.undo_manager.can_redo()
        
        self.undo_action.setEnabled(can_undo)
        self.undo_action.setText(self.undo_manager.undo_description())
        self.undo_tool_action.setEnabled(can_undo)
        self.undo_tool_action.setToolTip(self.undo_manager.undo_description())
        
        self.redo_action.setEnabled(can_redo)
        self.redo_action.setText(self.undo_manager.redo_description())
        self.redo_tool_action.setEnabled(can_redo)
        self.redo_tool_action.setToolTip(self.undo_manager.redo_description())
    
    
    # ============================================================================
    # Scenario Management Methods (Option B+ Implementation)
    # ============================================================================
    
    def load_scenarios(self):
        """Load all scenarios for current project into ComboBox"""
        if not self.project_id:
            return
        
        # Block signals to prevent triggering on_scenario_changed during load
        self.scenario_combo.blockSignals(True)
        self.scenario_combo.clear()
        
        try:
            from utils.scenario_manager import ScenarioManager
            
            scenario_manager = ScenarioManager(self.db_manager, self.project_id)
            scenarios = scenario_manager.get_all_scenarios()
            
            for scenario in scenarios:
                display_name = scenario['name']
                if scenario['is_base']:
                    display_name += " (Base)"
                self.scenario_combo.addItem(display_name, scenario['id'])
            
            # Select current scenario
            for i in range(self.scenario_combo.count()):
                if self.scenario_combo.itemData(i) == self.current_scenario_id:
                    self.scenario_combo.setCurrentIndex(i)
                    break
                    
        except Exception:
            pass
        finally:
            self.scenario_combo.blockSignals(False)
    
    def on_scenario_changed(self, index):
        """Handle scenario selection change"""
        if index < 0:
            return
        
        new_scenario_id = self.scenario_combo.itemData(index)
        if new_scenario_id is None or new_scenario_id == self.current_scenario_id:
            return
        
        self.current_scenario_id = new_scenario_id
        
        # Clear TOPSIS results - they are scenario-specific but not stored in DB
        # User must recalculate TOPSIS for each scenario
        if hasattr(self, 'topsis_results'):
            delattr(self, 'topsis_results')
        
        # CHANGED: Refresh ALL tabs instead of just current tab
        # This ensures auto-load works regardless of which tab user is on
        if hasattr(self, 'project_tab'):
            self.project_tab.load_data()
        if hasattr(self, 'ahp_tab'):
            self.ahp_tab.load_data()
        if hasattr(self, 'topsis_tab'):
            self.topsis_tab.load_data()
        if hasattr(self, 'results_tab'):
            self.results_tab.load_data()
        if hasattr(self, 'sensitivity_tab'):
            self.sensitivity_tab.load_data()
        
        # Update status bar
        scenario_name = self.scenario_combo.currentText()
        self.status_bar.showMessage(f"Switched to: {scenario_name}", 3000)
        
        # Enable/disable delete button (cannot delete base scenario)
        if hasattr(self, 'scenario_delete_btn'):
            self.scenario_delete_btn.setEnabled(new_scenario_id != 1)
    
    def create_new_scenario(self):
        """Create new scenario via QInputDialog"""
        from PyQt6.QtWidgets import QInputDialog
        from utils.scenario_manager import ScenarioManager
        
        if not self.project_id:
            QMessageBox.warning(self, "No Project", "Please load a project first.")
            return
        
        scenario_manager = ScenarioManager(self.db_manager, self.project_id)
        
        # Get existing scenario names for validation
        existing_scenarios = scenario_manager.get_all_scenarios()
        existing_names = {s['name'].lower() for s in existing_scenarios}
        
        # Ask for scenario name with validation loop
        while True:
            name, ok = QInputDialog.getText(
                self,
                "New Scenario",
                "Enter scenario name:",
                text=f"Scenario {len(existing_scenarios) + 1}"
            )
            
            if not ok or not name.strip():
                return  # User cancelled
            
            # Validate name
            name = name.strip()
            
            if name.lower() in existing_names:
                QMessageBox.warning(
                    self,
                    "Duplicate Name",
                    f"A scenario named '{name}' already exists.\nPlease choose a different name."
                )
                continue  # Ask again
            
            if len(name) > 100:
                QMessageBox.warning(
                    self,
                    "Name Too Long",
                    "Scenario name must be 100 characters or less."
                )
                continue
            
            # Name is valid, break loop
            break
        
        try:
            # Duplicate from current scenario
            new_id = scenario_manager.duplicate_scenario(
                source_scenario_id=self.current_scenario_id,
                new_name=name,
                new_description=f"Created from {self.scenario_combo.currentText()}"
            )
            
            # Reload combo and switch to new scenario
            self.load_scenarios()
            
            # Select the new scenario
            for i in range(self.scenario_combo.count()):
                if self.scenario_combo.itemData(i) == new_id:
                    self.scenario_combo.setCurrentIndex(i)
                    break
            
            QMessageBox.information(
                self,
                "Success",
                f"Scenario '{name}' created successfully!"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to create scenario:\n{str(e)}"
            )
    
    def delete_current_scenario(self):
        """Delete the currently selected scenario"""
        from PyQt6.QtWidgets import QMessageBox
        from utils.scenario_manager import ScenarioManager
        
        if not self.project_id:
            QMessageBox.warning(self, "No Project", "Please load a project first.")
            return
        
        current_scenario_id = self.current_scenario_id
        current_scenario_name = self.scenario_combo.currentText()
        
        # Prevent deleting base scenario
        if current_scenario_id == 1:
            QMessageBox.warning(
                self,
                "Cannot Delete Base Scenario",
                "The base scenario cannot be deleted.\n\n"
                "It serves as the foundation for all other scenarios."
            )
            return
        
        # Confirmation dialog
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete scenario:\n\n"
            f"'{current_scenario_name}'?\n\n"
            f"This will permanently delete:\n"
            f"• All AHP comparisons\n"
            f"• All TOPSIS ratings\n"
            f"• All associated data\n\n"
            f"This action cannot be undone!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            scenario_manager = ScenarioManager(self.db_manager, self.project_id)
            
            # Delete scenario
            scenario_manager.delete_scenario(current_scenario_id)
            
            # Reload scenarios and switch to base
            self.load_scenarios()
            
            # Select base scenario (index 0)
            self.scenario_combo.setCurrentIndex(0)
            
            QMessageBox.information(
                self,
                "Success",
                f"Scenario '{current_scenario_name}' has been deleted successfully."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to delete scenario:\n{str(e)}"
            )
    
    def refresh_current_tab(self):
        """Refresh data in currently active tab"""
        current_index = self.tabs.currentIndex()
        
        
        if current_index == 0:  # Project tab
            self.project_tab.load_data()
        elif current_index == 1:  # AHP tab
            self.ahp_tab.load_data()
        elif current_index == 2:  # TOPSIS tab
            self.topsis_tab.load_data()
        elif current_index == 3:  # Results tab
            self.results_tab.load_data()
    
    # ============================================================================
    
    def closeEvent(self, event):
        """Handle window close event - ask to save project"""
        # If no project is loaded, just close
        if not self.current_project_path:
            event.accept()
            return
        
        # Ask user if they want to save
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle('Xác nhận thoát')
        msg_box.setText('Bạn có muốn lưu project hiện tại trước khi thoát?')
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | 
                                 QMessageBox.StandardButton.No | 
                                 QMessageBox.StandardButton.Cancel)
        msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)
        
        # Style No button to be white
        no_btn = msg_box.button(QMessageBox.StandardButton.No)
        if no_btn:
            no_btn.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    color: #2c3e50;
                    border: 1px solid #bdc3c7;
                    min-width: 80px;
                    padding: 6px 16px;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #f5f6fa;
                    border: 1px solid #3498db;
                }
            """)

        reply = msg_box.exec()
        
        if reply == QMessageBox.StandardButton.Yes:
            # Save project
            self.save_project()
            event.accept()
        elif reply == QMessageBox.StandardButton.No:
            # Don't save, just exit
            event.accept()
        else:
            # Cancel - don't exit
            event.ignore()
