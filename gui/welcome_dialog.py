"""
Welcome Dialog Module
Startup screen for project selection (Excel-style)
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QListWidget, QListWidgetItem, 
                             QWidget, QFrame, QScrollArea, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt, QSize, QDateTime
from PyQt6.QtGui import QFont, QIcon, QColor, QCursor
import os
from datetime import datetime

class WelcomeDialog(QDialog):
    """Startup dialog to select or create project"""
    
    def __init__(self, project_manager, parent=None):
        super().__init__(parent)
        self.project_manager = project_manager
        self.selected_project_path = None
        self.action = None  # 'new', 'open', or None
        
        self.setWindowTitle("Welcome - Supplier Selection App")
        self.setFixedSize(1100, 700)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- Left Sidebar ---
        left_panel = QFrame()
        # Using app theme colors: #2c3e50 (Dark Blue/Gray) and #3498db (Blue)
        left_panel.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                color: white;
                border: none;
            }
            QPushButton {
                background-color: transparent;
                color: white;
                text-align: left;
                padding: 15px 20px;
                border: none;
                font-size: 11pt;
                border-radius: 0px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton#ActiveButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
            }
        """)
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 40, 0, 20)
        left_layout.setSpacing(5)
        
        # App Title
        title_label = QLabel("  Supplier\n  Selection")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white; margin-bottom: 40px; margin-left: 20px;")
        left_layout.addWidget(title_label)
        
        # Home Button (Active)
        home_btn = QPushButton("🏠  Home")
        home_btn.setObjectName("ActiveButton")
        home_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        left_layout.addWidget(home_btn)
        
        # New Button
        new_btn = QPushButton("📄  New")
        new_btn.clicked.connect(self.create_new_project)
        new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        left_layout.addWidget(new_btn)
        
        # Open Button
        open_btn = QPushButton("📂  Open")
        open_btn.clicked.connect(self.open_project_dialog)
        open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        left_layout.addWidget(open_btn)
        
        left_layout.addStretch()
        
        # Account/Options removed as requested
        
        # Exit Button
        exit_btn = QPushButton("❌  Exit")
        exit_btn.clicked.connect(self.reject)
        exit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        left_layout.addWidget(exit_btn)
        
        left_panel.setLayout(left_layout)
        left_panel.setFixedWidth(250)
        main_layout.addWidget(left_panel)
        
        # --- Main Content Area ---
        right_panel = QFrame()
        right_panel.setStyleSheet("background-color: #fafafa;")
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(40, 40, 40, 0)
        right_layout.setSpacing(20)
        
        # Greeting
        hour = datetime.now().hour
        greeting = "Good morning" if 5 <= hour < 12 else "Good afternoon" if 12 <= hour < 18 else "Good evening"
        greeting_label = QLabel(greeting)
        greeting_label.setFont(QFont("Segoe UI", 20, QFont.Weight.DemiBold))
        greeting_label.setStyleSheet("color: #2c3e50;")
        right_layout.addWidget(greeting_label)
        
        # New Project Section
        new_section = QWidget()
        new_layout = QHBoxLayout()
        new_layout.setContentsMargins(0, 0, 0, 0)
        new_layout.setSpacing(20)
        
        # Blank Workbook Card
        blank_card = QPushButton()
        blank_card.setFixedSize(160, 200)
        blank_card.setCursor(Qt.CursorShape.PointingHandCursor)
        blank_card.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                text-align: center;
            }
            QPushButton:hover {
                border: 1px solid #3498db;
                background-color: #eef5ff;
            }
        """)
        blank_card_layout = QVBoxLayout()
        blank_card_layout.setContentsMargins(10, 20, 10, 10)
        
        # Grid Icon
        grid_icon = QLabel("▦")
        grid_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grid_icon.setFont(QFont("Segoe UI", 48))
        grid_icon.setStyleSheet("color: #3498db;")
        blank_card_layout.addWidget(grid_icon)
        
        blank_card_layout.addStretch()
        
        blank_label = QLabel("Blank project")
        blank_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        blank_label.setFont(QFont("Segoe UI", 11))
        blank_label.setStyleSheet("color: #2c3e50;")
        blank_card_layout.addWidget(blank_label)
        
        blank_card.setLayout(blank_card_layout)
        blank_card.clicked.connect(self.create_new_project)
        new_layout.addWidget(blank_card)
        
        # Add some placeholder templates (visual only)
        for name in ["Fuzzy AHP Template", "TOPSIS Ranking"]:
            template_card = QPushButton()
            template_card.setFixedSize(160, 200)
            template_card.setCursor(Qt.CursorShape.PointingHandCursor)
            template_card.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    border: 1px solid #bdc3c7;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    border: 1px solid #3498db;
                }
            """)
            t_layout = QVBoxLayout()
            t_label = QLabel(name)
            t_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            t_label.setStyleSheet("color: #2c3e50;")
            t_layout.addStretch()
            t_layout.addWidget(t_label)
            template_card.setLayout(t_layout)
            # Connect templates to new project for now
            template_card.clicked.connect(self.create_new_project)
            new_layout.addWidget(template_card)
            
        new_layout.addStretch()
        right_layout.addWidget(new_section)
        
        # Recent Projects Section
        recent_header = QHBoxLayout()
        recent_label = QLabel("Recent")
        recent_label.setFont(QFont("Segoe UI", 14, QFont.Weight.DemiBold))
        recent_label.setStyleSheet("color: #2c3e50;")
        recent_header.addWidget(recent_label)
        
        recent_header.addStretch()
        
        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Search")
        search_bar.setFixedWidth(200)
        search_bar.setStyleSheet("""
            QLineEdit {
                padding: 5px 10px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background-color: white;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        """)
        recent_header.addWidget(search_bar)
        right_layout.addLayout(recent_header)
        
        # Recent List (Table)
        self.recent_table = QTableWidget()
        self.recent_table.setColumnCount(3)
        self.recent_table.setHorizontalHeaderLabels(["Name", "Date Modified", "Path"])
        self.recent_table.verticalHeader().setVisible(False)
        self.recent_table.setShowGrid(False)
        self.recent_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.recent_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.recent_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.recent_table.setAlternatingRowColors(False)
        self.recent_table.setStyleSheet("""
            QTableWidget {
                background-color: transparent;
                border: none;
                font-family: "Segoe UI";
                color: #2c3e50;
            }
            QHeaderView::section {
                background-color: transparent;
                border: none;
                font-weight: bold;
                color: #7f8c8d;
                padding: 5px;
                text-align: left;
            }
            QTableWidget::item {
                padding: 10px 5px;
                border-bottom: 1px solid #eee;
            }
            QTableWidget::item:selected {
                background-color: #eef5ff;
                color: #2c3e50;
            }
            QTableWidget::item:hover {
                background-color: #f8f9fa;
            }
        """)
        
        header = self.recent_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        self.recent_table.itemDoubleClicked.connect(self.on_project_double_clicked)
        
        right_layout.addWidget(self.recent_table)
        
        self.populate_recent_projects()
        
        right_panel.setLayout(right_layout)
        main_layout.addWidget(right_panel)
        
        self.setLayout(main_layout)
        
    def populate_recent_projects(self):
        """Populate the list of recent projects"""
        projects = self.project_manager.get_recent_projects()
        self.recent_table.setRowCount(len(projects))
        
        for i, project in enumerate(projects):
            # Name with Icon
            name_item = QTableWidgetItem(f"📊  {project['name']}")
            name_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            name_item.setData(Qt.ItemDataRole.UserRole, project['path'])
            self.recent_table.setItem(i, 0, name_item)
            
            # Date
            last_mod = project.get('last_modified', project.get('last_opened', ''))
            try:
                dt = datetime.fromisoformat(last_mod)
                date_str = dt.strftime("%b %d, %Y %I:%M %p")
            except:
                date_str = last_mod
            
            date_item = QTableWidgetItem(date_str)
            date_item.setForeground(QColor("#7f8c8d"))
            self.recent_table.setItem(i, 1, date_item)
            
            # Path
            path_item = QTableWidgetItem(project['path'])
            path_item.setForeground(QColor("#95a5a6"))
            self.recent_table.setItem(i, 2, path_item)
            
    def create_new_project(self):
        """Handle new project creation"""
        self.action = 'new'
        self.accept()
        
    def open_project_dialog(self):
        """Handle opening project via dialog"""
        self.action = 'open'
        self.accept()
        
    def on_project_double_clicked(self, item):
        """Handle opening project from list"""
        # Get the row of the clicked item
        row = item.row()
        # Get the first item in that row (which holds the path data)
        name_item = self.recent_table.item(row, 0)
        path = name_item.data(Qt.ItemDataRole.UserRole)
        
        if path:
            self.selected_project_path = path
            self.action = 'open_recent'
            self.accept()
