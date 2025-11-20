"""
Project Tab Module
Handles project configuration: criteria and alternatives management
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QTableWidget,
                             QTableWidgetItem, QPushButton, QLabel, QLineEdit, QTextEdit,
                             QMessageBox, QComboBox, QHeaderView)
from PyQt6.QtCore import Qt

from utils.validators import Validators


class ProjectTab(QWidget):
    """Project configuration tab"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Project info section
        info_group = QGroupBox("Project Information")
        info_layout = QVBoxLayout()
        
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Project Name:"))
        self.name_input = QLineEdit()
        self.name_input.setReadOnly(True)
        name_layout.addWidget(self.name_input)
        info_layout.addLayout(name_layout)
        
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("Description:"))
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(60)
        desc_layout.addWidget(self.desc_input)
        info_layout.addLayout(desc_layout)
        
        update_btn = QPushButton("Update Project Info")
        update_btn.clicked.connect(self.update_project_info)
        info_layout.addWidget(update_btn)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Criteria section - using hierarchical tree
        criteria_group = QGroupBox("Criteria Hierarchy")
        criteria_layout = QVBoxLayout()
        criteria_layout.setContentsMargins(5, 5, 5, 5)  # Minimal margins
        criteria_layout.setSpacing(2)  # Minimal spacing
        
        from gui.criteria_tree import CriteriaTreeWidget
        self.criteria_tree = None  # Will be initialized in load_data
        
        criteria_layout_placeholder = QVBoxLayout()
        self.criteria_placeholder = QWidget()
        self.criteria_placeholder.setLayout(criteria_layout_placeholder)
        criteria_layout.addWidget(self.criteria_placeholder)
        
        # Remove minimum height to allow flexible sizing
        
        criteria_group.setLayout(criteria_layout)
        layout.addWidget(criteria_group, stretch=1)  # Allow criteria to stretch
        
        # Alternatives section
        alternatives_group = QGroupBox("Alternatives (Suppliers) Management")
        alternatives_layout = QVBoxLayout()
        
        self.alternatives_table = QTableWidget()
        self.alternatives_table.setColumnCount(4)
        self.alternatives_table.setHorizontalHeaderLabels(["ID", "Name", "Description", "Actions"])
        self.alternatives_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.alternatives_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.alternatives_table.setColumnWidth(0, 50)
        self.alternatives_table.setColumnWidth(3, 150)
        alternatives_layout.addWidget(self.alternatives_table)
        
        alternatives_btn_layout = QHBoxLayout()
        add_alternative_btn = QPushButton("Add Alternative")
        add_alternative_btn.clicked.connect(self.add_alternative)
        alternatives_btn_layout.addWidget(add_alternative_btn)
        alternatives_btn_layout.addStretch()
        alternatives_layout.addLayout(alternatives_btn_layout)
        
        alternatives_group.setLayout(alternatives_layout)
        layout.addWidget(alternatives_group, stretch=1)  # Allow alternatives to stretch equally
        
        self.setLayout(layout)
    
    def load_data(self):
        """Load project data from database"""
        db = self.main_window.get_db_manager()
        if not db:
            return
        
        with db as database:
            # Load project info
            project = database.get_project()
            if project:
                self.name_input.setText(project['name'])
                self.desc_input.setPlainText(project.get('description', ''))
        
        # Initialize criteria tree if not already done
        if self.criteria_tree is None:
            from gui.criteria_tree import CriteriaTreeWidget
            self.criteria_tree = CriteriaTreeWidget(
                self.main_window.get_db_manager(),
                self.main_window.get_project_id(),
                self
            )
            # Connect signal to refresh other tabs when criteria change
            self.criteria_tree.criteria_changed.connect(self.on_criteria_changed)
            
            # Add to layout with stretch to fill space
            self.criteria_placeholder.layout().addWidget(self.criteria_tree, stretch=1)
        else:
            # Update DB manager and project ID for existing tree
            self.criteria_tree.db_manager = self.main_window.get_db_manager()
            self.criteria_tree.project_id = self.main_window.get_project_id()
        
        # Load criteria into tree
        self.criteria_tree.load_criteria()
        
        # Load alternatives
        with db as database:
            alternatives = database.get_alternatives(self.main_window.get_project_id())
            self.populate_alternatives_table(alternatives)
    
    def on_criteria_changed(self):
        """Handle criteria changes - refresh other tabs"""
        # Refresh AHP and TOPSIS tabs
        if hasattr(self.main_window, 'ahp_tab'):
            self.main_window.ahp_tab.load_data()
        if hasattr(self.main_window, 'topsis_tab'):
            self.main_window.topsis_tab.load_data()

    
    def populate_alternatives_table(self, alternatives):
        """Populate alternatives table"""
        self.alternatives_table.setRowCount(len(alternatives))
        
        for row, alternative in enumerate(alternatives):
            # ID
            self.alternatives_table.setItem(row, 0, QTableWidgetItem(str(alternative['id'])))
            
            # Name
            self.alternatives_table.setItem(row, 1, QTableWidgetItem(alternative['name']))
            
            # Description
            self.alternatives_table.setItem(row, 2, QTableWidgetItem(alternative.get('description', '')))
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(2, 2, 2, 2)
            
            edit_btn = QPushButton("Edit")
            edit_btn.setProperty("class", "warning")
            edit_btn.clicked.connect(lambda checked, a_id=alternative['id']: self.edit_alternative(a_id))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("Delete")
            delete_btn.setProperty("class", "danger")
            delete_btn.clicked.connect(lambda checked, a_id=alternative['id']: self.delete_alternative(a_id))
            actions_layout.addWidget(delete_btn)
            
            actions_widget.setLayout(actions_layout)
            self.alternatives_table.setCellWidget(row, 3, actions_widget)
    
    def update_project_info(self):
        """Update project information"""
        name = self.name_input.text()
        description = self.desc_input.toPlainText()
        
        valid, error = Validators.validate_project_name(name)
        if not valid:
            QMessageBox.warning(self, "Validation Error", error)
            return
        
        db = self.main_window.get_db_manager()
        with db as database:
            database.update_project(name, description)
        
        QMessageBox.information(self, "Success", "Project information updated!")
    
    def on_alternatives_changed(self):
        """Handle alternative changes - refresh other tabs"""
        # Refresh TOPSIS tab (AHP doesn't depend on alternatives directly, but good to keep in sync if needed)
        if hasattr(self.main_window, 'topsis_tab'):
            self.main_window.topsis_tab.load_data()
            
    def add_alternative(self):
        """Add a new alternative"""
        from PyQt6.QtWidgets import QDialog, QFormLayout, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Alternative")
        layout = QFormLayout()
        
        name_input = QLineEdit()
        layout.addRow("Alternative Name:", name_input)
        
        desc_input = QTextEdit()
        desc_input.setMaximumHeight(60)
        layout.addRow("Description:", desc_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = name_input.text()
            description = desc_input.toPlainText()
            
            valid, error = Validators.validate_alternative_name(name)
            if not valid:
                QMessageBox.warning(self, "Validation Error", error)
                return
            
            db = self.main_window.get_db_manager()
            with db as database:
                try:
                    database.add_alternative(self.main_window.get_project_id(), name, description)
                    self.load_data()
                    self.on_alternatives_changed()
                    QMessageBox.information(self, "Success", "Alternative added!")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to add alternative: {str(e)}")
    
    def edit_alternative(self, alternative_id):
        """Edit an existing alternative"""
        # Get current alternative data
        db = self.main_window.get_db_manager()
        current_alt = None
        with db as database:
            alternatives = database.get_alternatives(self.main_window.get_project_id())
            for alt in alternatives:
                if alt['id'] == alternative_id:
                    current_alt = alt
                    break
        
        if not current_alt:
            return

        from PyQt6.QtWidgets import QDialog, QFormLayout, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Alternative")
        layout = QFormLayout()
        
        name_input = QLineEdit(current_alt['name'])
        layout.addRow("Alternative Name:", name_input)
        
        desc_input = QTextEdit()
        desc_input.setPlainText(current_alt.get('description', ''))
        desc_input.setMaximumHeight(60)
        layout.addRow("Description:", desc_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = name_input.text()
            description = desc_input.toPlainText()
            
            valid, error = Validators.validate_alternative_name(name)
            if not valid:
                QMessageBox.warning(self, "Validation Error", error)
                return
            
            with db as database:
                try:
                    database.update_alternative(alternative_id, name, description)
                    self.load_data()
                    self.on_alternatives_changed()
                    QMessageBox.information(self, "Success", "Alternative updated!")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to update alternative: {str(e)}")
    
    def delete_alternative(self, alternative_id):
        """Delete an alternative"""
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this alternative?\nAll related data will be removed.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            db = self.main_window.get_db_manager()
            with db as database:
                database.delete_alternative(alternative_id)
                self.load_data()
                self.on_alternatives_changed()
                QMessageBox.information(self, "Success", "Alternative deleted!")
