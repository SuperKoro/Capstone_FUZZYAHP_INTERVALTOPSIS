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
        self.undo_manager = UndoManager()
        self.undo_manager.on_stack_change = self.update_undo_redo_actions
        self.project_manager = ProjectManager()
        
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
        
        self.tabs.addTab(self.project_tab, "Project Setup")
        self.tabs.addTab(self.ahp_tab, "Fuzzy AHP Evaluation")
        self.tabs.addTab(self.topsis_tab, "TOPSIS Rating")
        self.tabs.addTab(self.results_tab, "Results")
        
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
        """Load a project from path"""
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "Error", "Project file not found!")
            self.project_manager.remove_project(file_path)
            # self.update_recent_projects_menu() # Removed from menu
            return
            
        self.current_project_path = file_path
        self.db_manager = DatabaseManager(file_path)
        self.undo_manager.clear()
        
        # Get project info
        with self.db_manager as db:
            project = db.get_project()
            if project:
                self.project_id = project['id']
                
                # Add to project manager
                self.project_manager.add_project(project['name'], file_path)
                # self.update_recent_projects_menu() # Removed from menu
                
                # Clear previous results
                if hasattr(self, 'topsis_results'):
                    del self.topsis_results
                
                self.set_tabs_enabled(True)
                self.refresh_all_tabs()
                self.status_bar.showMessage(f"Project: {project['name']} - {file_path}")
            else:
                QMessageBox.warning(self, "Error", "Invalid project file!")
    
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
    
    def closeEvent(self, event):
        """Handle window close event - ask to save project"""
        # If no project is loaded, just close
        if not self.current_project_path:
            event.accept()
            return
        
        # Ask user if they want to save
        reply = QMessageBox.question(
            self,
            'Xác nhận thoát',
            'Bạn có muốn lưu project hiện tại trước khi thoát?',
            QMessageBox.StandardButton.Yes | 
            QMessageBox.StandardButton.No | 
            QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Yes
        )
        
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
