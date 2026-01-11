"""
TOPSIS Tab Module
Handles Interval TOPSIS rating input and calculation
With frozen Criterion column (Excel-like freeze panes)
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QTableWidget,
                             QTableWidgetItem, QPushButton, QLabel, QComboBox, QMessageBox,
                             QHeaderView, QListView, QAbstractItemView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush
import numpy as np

from algorithms.interval_topsis import IntervalTOPSIS


FROZEN_BG_COLOR = QColor(240, 244, 248)


class NoScrollComboBox(QComboBox):
    """Custom QComboBox that disables mouse wheel scrolling"""
    
    def wheelEvent(self, event):
        """Ignore wheel events to prevent accidental selection changes"""
        event.ignore()


class TOPSISTab(QWidget):
    """Interval TOPSIS rating tab with frozen Criterion column"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.criteria = []
        self.alternatives = []
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Instructions
        info_label = QLabel(
            "Enter performance ratings for each alternative against each criterion.\n"
            "Use linguistic ratings: Very Poor, Poor, Medium Poor, Fair, Medium Good, Good, Very Good"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Expert Selection
        expert_group = QGroupBox("Expert Selection")
        expert_layout = QHBoxLayout()
        
        expert_layout.addWidget(QLabel("Select Expert:"))
        self.expert_combo = QComboBox()
        self.expert_combo.setView(QListView())
        self.expert_combo.setStyleSheet("""
            QComboBox {
                font-size: 12px;
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox QListView {
                border: 1px solid #ccc;
                background-color: white;
                outline: none;
            }
            QComboBox QListView::item {
                border-bottom: 1px solid #e0e0e0;
                padding: 8px;
                min-height: 25px;
                color: black;
            }
            QComboBox QListView::item:hover {
                background-color: #00CED1;
                color: white;
            }
            QComboBox QListView::item:selected {
                background-color: #00CED1;
                color: white;
            }
        """)
        self.expert_combo.currentIndexChanged.connect(self.on_expert_changed)
        expert_layout.addWidget(self.expert_combo)
        expert_layout.addStretch()
        
        expert_group.setLayout(expert_layout)
        layout.addWidget(expert_group)
        
        # Rating matrix section with frozen column
        matrix_group = QGroupBox("Performance Rating Matrix")
        matrix_layout = QHBoxLayout()
        matrix_layout.setSpacing(0)
        matrix_layout.setContentsMargins(5, 5, 5, 5)
        
        # FROZEN TABLE (Criterion column only)
        self.frozen_table = QTableWidget()
        self.frozen_table.setColumnCount(1)
        self.frozen_table.setHorizontalHeaderLabels(["Criterion"])
        self.frozen_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.frozen_table.setColumnWidth(0, 200)
        self.frozen_table.setFixedWidth(220)
        self.frozen_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.frozen_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.frozen_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.frozen_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.frozen_table.setStyleSheet("""
            QTableWidget {
                background-color: #f0f4f8;
                border: 1px solid #3498db;
                border-right: 2px solid #3498db;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 8px;
                border: none;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #ddd;
            }
        """)
        
        # SCROLLABLE TABLE (Supplier columns)
        self.rating_table = QTableWidget()
        self.rating_table.cellClicked.connect(self.on_rating_cell_clicked)
        self.rating_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.rating_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.rating_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #3498db;
                border-left: none;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 8px;
                border: none;
            }
        """)
        
        # Synchronize vertical scrolling between tables
        self.rating_table.verticalScrollBar().valueChanged.connect(
            self.frozen_table.verticalScrollBar().setValue
        )
        self.frozen_table.verticalScrollBar().valueChanged.connect(
            self.rating_table.verticalScrollBar().setValue
        )
        
        # Hide row headers on scrollable table (show only on frozen)
        self.rating_table.verticalHeader().setVisible(False)
        
        matrix_layout.addWidget(self.frozen_table)
        matrix_layout.addWidget(self.rating_table, 1)
        
        matrix_group.setLayout(matrix_layout)
        layout.addWidget(matrix_group)
        
        # Calculate button
        calc_btn = QPushButton("Calculate TOPSIS Ranking (All Experts)")
        calc_btn.clicked.connect(self.calculate_ranking)
        layout.addWidget(calc_btn)
        
        self.setLayout(layout)

    def _get_combo_style(self):
        """Return the default combobox style"""
        return """
            QComboBox {
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox QListView {
                border: 1px solid #ccc;
                background-color: white;
                outline: none;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
            }
            QComboBox QListView::item {
                border-bottom: 1px solid #e0e0e0;
                padding: 8px;
                min-height: 30px;
                color: black;
            }
            QComboBox QListView::item:hover {
                background-color: #00CED1;
                color: white;
            }
            QComboBox QListView::item:selected {
                background-color: #00CED1;
                color: white;
            }
        """
    
    def load_data(self):
        """Load data from database"""
        db = self.main_window.get_db_manager()
        if not db:
            return
        
        with db as database:
            # Load criteria - ONLY LEAF CRITERIA (no parents)
            self.criteria = database.get_leaf_criteria(self.main_window.get_project_id())
            
            # Load alternatives
            self.alternatives = database.get_alternatives(self.main_window.get_project_id())
            
            # Load experts
            self.experts = database.get_experts(self.main_window.get_project_id())
            
            # Update expert combo
            current_expert_id = self.expert_combo.currentData()
            self.expert_combo.blockSignals(True)
            self.expert_combo.clear()
            
            if self.experts:
                for expert in self.experts:
                    self.expert_combo.addItem(expert['name'], expert['id'])
                
                if current_expert_id:
                    index = self.expert_combo.findData(current_expert_id)
                    if index >= 0:
                        self.expert_combo.setCurrentIndex(index)
                    else:
                        self.expert_combo.setCurrentIndex(0)
                else:
                    self.expert_combo.setCurrentIndex(0)
                
                self.expert_combo.setEnabled(True)
            else:
                self.expert_combo.addItem("(No experts - add in AHP tab)", None)
                self.expert_combo.setEnabled(False)
            
            self.expert_combo.blockSignals(False)
            
            # Setup rating table
            self.setup_rating_table()
            
            # Load existing ratings for current expert
            self.load_existing_ratings(database)
            
    def on_expert_changed(self):
        """Handle expert selection change"""
        db = self.main_window.get_db_manager()
        if db:
            with db as database:
                self.load_existing_ratings(database)

    def on_rating_cell_clicked(self, row, col):
        """Handle click on rating cell - open dropdown"""
        combo = self.rating_table.cellWidget(row, col)
        if combo:
            combo.showPopup()

    def setup_rating_table(self):
        """Setup the rating matrix table with frozen Criterion column"""
        if not self.criteria or not self.alternatives:
            self.frozen_table.setRowCount(0)
            self.rating_table.setRowCount(0)
            self.rating_table.setColumnCount(0)
            return
        
        n_alternatives = len(self.alternatives)
        n_criteria = len(self.criteria)
        
        # Setup FROZEN table (Criterion names only)
        self.frozen_table.setRowCount(n_criteria)
        self.frozen_table.verticalHeader().setDefaultSectionSize(50)
        
        for i, criterion in enumerate(self.criteria):
            item = QTableWidgetItem(criterion['name'])
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item.setBackground(QBrush(FROZEN_BG_COLOR))
            self.frozen_table.setItem(i, 0, item)
        
        # Setup SCROLLABLE table (Supplier ratings)
        self.rating_table.setRowCount(n_criteria)
        self.rating_table.setColumnCount(n_alternatives)
        
        # Set headers (Supplier names)
        headers = [a['name'] for a in self.alternatives]
        self.rating_table.setHorizontalHeaderLabels(headers)
        
        # Configure header resizing
        header = self.rating_table.horizontalHeader()
        header.setMinimumSectionSize(130)
        for i in range(n_alternatives):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        # Make rows taller for better visibility
        self.rating_table.verticalHeader().setDefaultSectionSize(50)
        
        # Populate rating combos
        for i, criterion in enumerate(self.criteria):
            for j, alternative in enumerate(self.alternatives):
                rating_combo = NoScrollComboBox()
                rating_combo.setEditable(False)
                rating_combo.setView(QListView())
                rating_combo.setStyleSheet(self._get_combo_style())
                # Add items with interval notation
                for rating_name in ["Very Poor", "Poor", "Medium Poor", "Fair", "Medium Good", "Good", "Very Good"]:
                    lower, upper = IntervalTOPSIS.LINGUISTIC_RATINGS[rating_name]
                    interval_str = f"({int(lower):2}, {int(upper):2})"
                    label = f"{rating_name:13} {interval_str:8}"
                    rating_combo.addItem(label)
                rating_combo.setCurrentIndex(3)  # Default to "Fair"
                # Connect signal to save immediately
                rating_combo.currentIndexChanged.connect(lambda index, c=i, a=j: self.save_single_rating(c, a))
                self.rating_table.setCellWidget(i, j, rating_combo)
    
    def save_single_rating(self, criterion_idx, alternative_idx):
        """Save a single rating change immediately"""
        expert_id = self.expert_combo.currentData()
        if expert_id is None:
            return

        criterion = self.criteria[criterion_idx]
        alternative = self.alternatives[alternative_idx]
        
        combo = self.rating_table.cellWidget(criterion_idx, alternative_idx)
        rating_text = combo.currentText()
        rating_name = rating_text.split('(')[0].strip()
        lower, upper = IntervalTOPSIS.get_interval_rating(rating_name)
        
        db = self.main_window.get_db_manager()
        if db:
            with db as database:
                database.add_topsis_rating(
                    self.main_window.get_project_id(),
                    alternative['id'],
                    criterion['id'],
                    lower,
                    upper,
                    expert_id,
                    scenario_id=self.main_window.current_scenario_id
                )

    def load_existing_ratings(self, database):
        """Load existing ratings from database for selected expert"""
        expert_id = self.expert_combo.currentData()
        if expert_id is None:
            self.rating_table.blockSignals(True)
            for i in range(self.rating_table.rowCount()):
                for j in range(self.rating_table.columnCount()):
                    combo = self.rating_table.cellWidget(i, j)
                    if combo:
                        combo.setCurrentIndex(3)  # Default to Fair
            self.rating_table.blockSignals(False)
            return
            
        ratings = database.get_topsis_ratings(
            self.main_window.get_project_id(),
            expert_id,
            scenario_id=self.main_window.current_scenario_id
        )
        
        # Create mapping for quick lookup
        rating_map = {}
        for rating in ratings:
            key = (rating['alternative_id'], rating['criterion_id'])
            rating_map[key] = (rating['rating_lower'], rating['rating_upper'])
        
        # Apply to table
        self.rating_table.blockSignals(True)
        for i, criterion in enumerate(self.criteria):
            for j, alternative in enumerate(self.alternatives):
                key = (alternative['id'], criterion['id'])
                combo = self.rating_table.cellWidget(i, j)
                
                if not combo:
                    continue
                
                if key in rating_map:
                    lower, upper = rating_map[key]
                    rating_name = self.interval_to_linguistic(lower, upper)
                    index = -1
                    for idx in range(combo.count()):
                        if combo.itemText(idx).startswith(rating_name):
                            index = idx
                            break
                    if index >= 0:
                        combo.setCurrentIndex(index)
                else:
                    combo.setCurrentIndex(3)
        self.rating_table.blockSignals(False)
    
    def interval_to_linguistic(self, lower, upper):
        """Convert interval to linguistic rating"""
        for name, (l, u) in IntervalTOPSIS.LINGUISTIC_RATINGS.items():
            if abs(l - lower) < 0.1 and abs(u - upper) < 0.1:
                return name
        return "Fair"
    
    def calculate_ranking(self):
        """Calculate TOPSIS ranking using aggregated expert ratings"""
        if len(self.criteria) < 2:
            QMessageBox.warning(self, "Warning", "At least 2 criteria are required!")
            return
        
        if len(self.alternatives) < 2:
            QMessageBox.warning(self, "Warning", "At least 2 alternatives are required!")
            return
            
        if not self.experts:
             QMessageBox.warning(self, "Warning", "No experts defined!")
             return
        
        # Check if weights are calculated
        weights_calculated = all(
            c.get('weight') is not None and c['weight'] > 0 
            for c in self.criteria
        )
        if not weights_calculated:
            QMessageBox.warning(
                self, "Warning",
                "Please calculate AHP weights first in the AHP Evaluation tab!"
            )
            return
        
        try:
            db = self.main_window.get_db_manager()
            if not db:
                return
                
            expert_matrices = []
            
            with db as database:
                for expert in self.experts:
                    ratings = database.get_topsis_ratings(
                        self.main_window.get_project_id(),
                        expert['id'],
                        scenario_id=self.main_window.current_scenario_id
                    )
                    
                    n_alternatives = len(self.alternatives)
                    n_criteria = len(self.criteria)
                    matrix = np.zeros((n_alternatives, n_criteria, 2))
                    
                    rating_map = {(r['alternative_id'], r['criterion_id']): (r['rating_lower'], r['rating_upper']) for r in ratings}
                    
                    for i, alt in enumerate(self.alternatives):
                        for j, crit in enumerate(self.criteria):
                            if (alt['id'], crit['id']) in rating_map:
                                matrix[i, j] = rating_map[(alt['id'], crit['id'])]
                            else:
                                matrix[i, j] = [4, 5]
                    
                    expert_matrices.append(matrix)
            
            aggregated_matrix = IntervalTOPSIS.aggregate_expert_ratings(expert_matrices)
            weights = np.array([c['weight'] for c in self.criteria])
            is_benefit = np.array([c['is_benefit'] for c in self.criteria])
            
            CC, results = IntervalTOPSIS.rank_alternatives(aggregated_matrix, weights, is_benefit)
            
            self.main_window.topsis_results = {
                'closeness_coefficients': CC,
                'ranking': results['ranking'],
                'distances_to_PIS': results['distances_to_PIS'],
                'distances_to_NIS': results['distances_to_NIS'],
                'alternatives': self.alternatives,
                'criteria': self.criteria,
                'aggregated_matrix': aggregated_matrix
            }
            
            self.main_window.results_tab.load_data()
            self.main_window.tabs.setCurrentIndex(3)
            
            QMessageBox.information(self, "Success", f"TOPSIS ranking calculated successfully!\nAggregated ratings from {len(self.experts)} experts.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to calculate ranking: {str(e)}")
