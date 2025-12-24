"""
Project Tab Module
Handles project configuration: criteria and alternatives management
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QTableWidget,
                             QTableWidgetItem, QPushButton, QLabel, QLineEdit, QTextEdit,
                             QMessageBox, QComboBox, QHeaderView, QSizePolicy, QScrollArea)
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
        # ============================================================
        # PART 1: Create QScrollArea for tab-level scrolling
        # ============================================================
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)  # CRITICAL: allows content to grow
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)  # Remove border
        
        # Create content widget that will go inside scroll area
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Project info section
        info_group = QGroupBox("Project Information")
        info_layout = QVBoxLayout()
        
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Project Name:"))
        self.name_input = QLineEdit()
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
        content_layout.addWidget(info_group)
        
        # ============================================================
        # Horizontal layout for Criteria (LEFT) and Alternatives (RIGHT)
        # ============================================================
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(10)
        
        # LEFT: Criteria section
        criteria_group = QGroupBox("Criteria Hierarchy")
        criteria_layout = QVBoxLayout()
        criteria_layout.setContentsMargins(5, 5, 5, 5)
        
        from gui.criteria_tree import CriteriaTreeWidget
        self.criteria_tree = None  # Will be initialized in load_data
        
        criteria_layout_placeholder = QVBoxLayout()
        self.criteria_placeholder = QWidget()
        self.criteria_placeholder.setLayout(criteria_layout_placeholder)
        criteria_layout.addWidget(self.criteria_placeholder)
        
        criteria_group.setLayout(criteria_layout)
        columns_layout.addWidget(criteria_group, stretch=1)
        
        # RIGHT: Alternatives section
        alternatives_group = QGroupBox("Alternatives (Suppliers) Management")
        alternatives_layout = QVBoxLayout()
        
        # Add Alternative button at the TOP (before table)
        alternatives_btn_layout = QHBoxLayout()
        add_alternative_btn = QPushButton("+ Add Alternative")
        add_alternative_btn.clicked.connect(self.add_alternative)
        add_alternative_btn.setMinimumHeight(32)
        add_alternative_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-weight: bold;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        alternatives_btn_layout.addWidget(add_alternative_btn)
        alternatives_btn_layout.addStretch()
        alternatives_layout.addLayout(alternatives_btn_layout)
        
        # Table below the button
        self.alternatives_table = QTableWidget()
        self.alternatives_table.setColumnCount(4)
        self.alternatives_table.setHorizontalHeaderLabels(["ID", "Name", "Description", "Actions"])
        self.alternatives_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.alternatives_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.alternatives_table.setColumnWidth(0, 50)
        self.alternatives_table.setColumnWidth(3, 220)
        
        # PART 2: Disable internal scrollbar on table
        self.alternatives_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.alternatives_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        alternatives_layout.addWidget(self.alternatives_table)
        
        alternatives_group.setLayout(alternatives_layout)
        columns_layout.addWidget(alternatives_group, stretch=1)
        
        # Add columns to content layout
        content_layout.addLayout(columns_layout)
        
        # Set layout on content widget
        content_widget.setLayout(content_layout)
        
        # Put content widget inside scroll area
        scroll_area.setWidget(content_widget)
        
        # Set scroll area as the main widget of this tab
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_area)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)
    
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
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)
            
            edit_btn = QPushButton("✎ Edit")
            edit_btn.setProperty("class", "warning")
            edit_btn.setMinimumHeight(30)  # Reduced for better responsiveness
            edit_btn.setStyleSheet("border-radius: 0px; margin: 0px; font-size: 9pt;")
            edit_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            edit_btn.clicked.connect(lambda checked, a_id=alternative['id']: self.edit_alternative(a_id))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("− Delete")
            delete_btn.setProperty("class", "danger")
            delete_btn.setMinimumHeight(30)  # Reduced for better responsiveness
            delete_btn.setStyleSheet("border-radius: 0px; margin: 0px; font-size: 9pt;")
            delete_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            delete_btn.clicked.connect(lambda checked, a_id=alternative['id']: self.delete_alternative(a_id))
            actions_layout.addWidget(delete_btn)
            
            actions_widget.setLayout(actions_layout)
            self.alternatives_table.setCellWidget(row, 3, actions_widget)
            
            # Set row height to accommodate buttons
            self.alternatives_table.setRowHeight(row, 42)
        
        # PART 3: Update table height after populating
        self.update_alternatives_height()
    
    def update_alternatives_height(self):
        """PART 3: Recalculate table height based on content"""
        # Calculate total height needed
        total_height = 0
        
        # Add header height
        total_height += self.alternatives_table.horizontalHeader().height()
        
        # Add all row heights
        for row in range(self.alternatives_table.rowCount()):
            total_height += self.alternatives_table.rowHeight(row)
        
        # Add some padding for borders and scrollbar space
        total_height += 50
        
        # Set minimum height (allows growth, not fixed)
        self.alternatives_table.setMinimumHeight(total_height)
    
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
