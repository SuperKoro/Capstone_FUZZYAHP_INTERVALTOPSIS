"""
TOPSIS Tab Module
Handles Interval TOPSIS rating input and calculation
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QTableWidget,
                             QTableWidgetItem, QPushButton, QLabel, QComboBox, QMessageBox,
                             QHeaderView, QListView)
from PyQt6.QtCore import Qt
import numpy as np

from algorithms.interval_topsis import IntervalTOPSIS


class NoScrollComboBox(QComboBox):
    """Custom QComboBox that disables mouse wheel scrolling"""
    
    def wheelEvent(self, event):
        """Ignore wheel events to prevent accidental selection changes"""
        event.ignore()


class TOPSISTab(QWidget):
    """Interval TOPSIS rating tab"""
    
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
            "Use linguistic ratings: Very Poor, Poor, Fair, Good, Very Good, Excellent"
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
        
        # Rating matrix section
        matrix_group = QGroupBox("Performance Rating Matrix")
        matrix_layout = QVBoxLayout()
        
        self.rating_table = QTableWidget()
        self.rating_table.cellClicked.connect(self.on_rating_cell_clicked)
        matrix_layout.addWidget(self.rating_table)
        
        matrix_group.setLayout(matrix_layout)
        layout.addWidget(matrix_group)
        
        # Calculate button
        calc_btn = QPushButton("Calculate TOPSIS Ranking (All Experts)")
        calc_btn.clicked.connect(self.calculate_ranking)
        layout.addWidget(calc_btn)
        
        self.setLayout(layout)
    
    def load_data(self):
        """Load data from database"""
        db = self.main_window.get_db_manager()
        if not db:
            return
        
        with db as database:
            # Load criteria - ONLY LEAF CRITERIA (no parents)
            # Parent criteria should not be rated in TOPSIS to avoid double counting
            # Their weights are already incorporated through hierarchical AHP
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
                # Add experts to combo
                for expert in self.experts:
                    self.expert_combo.addItem(expert['name'], expert['id'])
                
                # Restore selection if possible, otherwise select first
                if current_expert_id:
                    index = self.expert_combo.findData(current_expert_id)
                    if index >= 0:
                        self.expert_combo.setCurrentIndex(index)
                    else:
                        self.expert_combo.setCurrentIndex(0)  # Select first if previous not found
                else:
                    self.expert_combo.setCurrentIndex(0)  # Select first expert by default
                
                # Ensure combo is enabled
                self.expert_combo.setEnabled(True)
            else:
                # No experts available
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
        # Columns start from 1 (0 is Alternative name)
        if col > 0:
            combo = self.rating_table.cellWidget(row, col)
            if combo:
                combo.showPopup()

    def setup_rating_table(self):
        """Setup the rating matrix table"""
        if not self.criteria or not self.alternatives:
            self.rating_table.setRowCount(0)
            self.rating_table.setColumnCount(0)
            return
        
        n_alternatives = len(self.alternatives)
        n_criteria = len(self.criteria)
        
        self.rating_table.setRowCount(n_alternatives)
        self.rating_table.setColumnCount(n_criteria + 1)
        
        # Set headers
        headers = ["Alternative"] + [c['name'] for c in self.criteria]
        self.rating_table.setHorizontalHeaderLabels(headers)
        
        # Configure header resizing
        header = self.rating_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.rating_table.setColumnWidth(0, 150)
        
        for i in range(1, n_criteria + 1):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
            
        header.setMinimumSectionSize(130)
        
        # Make rows taller for better visibility
        self.rating_table.verticalHeader().setDefaultSectionSize(50)
        
        # Populate rows
        for i, alternative in enumerate(self.alternatives):
            self.rating_table.setItem(i, 0, QTableWidgetItem(alternative['name']))
            
            for j, criterion in enumerate(self.criteria):
                rating_combo = NoScrollComboBox()
                rating_combo.setEditable(False)
                rating_combo.setView(QListView())
                rating_combo.setStyleSheet("""
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
                rating_combo.addItems([
                    "Very Poor", "Poor", "Fair", "Good", "Very Good", "Excellent"
                ])
                rating_combo.setCurrentIndex(2)  # Default to "Fair"
                # Connect signal to save immediately
                rating_combo.currentIndexChanged.connect(lambda index, r=i, c=j: self.save_single_rating(r, c))
                self.rating_table.setCellWidget(i, j + 1, rating_combo)
    
    def save_single_rating(self, row, col):
        """Save a single rating change immediately"""
        expert_id = self.expert_combo.currentData()
        if expert_id is None:
            return

        alternative = self.alternatives[row]
        criterion = self.criteria[col]
        
        combo = self.rating_table.cellWidget(row, col + 1)
        rating_name = combo.currentText()
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
                    expert_id
                )

    def load_existing_ratings(self, database):
        """Load existing ratings from database for selected expert"""
        expert_id = self.expert_combo.currentData()
        if expert_id is None:
            # No expert selected - clear all ratings to default
            self.rating_table.blockSignals(True)
            for i in range(self.rating_table.rowCount()):
                for j in range(self.rating_table.columnCount() - 1):
                    combo = self.rating_table.cellWidget(i, j + 1)
                    if combo:
                        combo.setCurrentIndex(2)  # Default to Fair
            self.rating_table.blockSignals(False)
            return
            
        ratings = database.get_topsis_ratings(self.main_window.get_project_id(), expert_id)
        
        # Create mapping for quick lookup
        rating_map = {}
        for rating in ratings:
            key = (rating['alternative_id'], rating['criterion_id'])
            rating_map[key] = (rating['rating_lower'], rating['rating_upper'])
        
        # Apply to table
        self.rating_table.blockSignals(True) # Prevent auto-save triggering
        for i, alternative in enumerate(self.alternatives):
            for j, criterion in enumerate(self.criteria):
                key = (alternative['id'], criterion['id'])
                combo = self.rating_table.cellWidget(i, j + 1)
                
                if not combo:  # Safety check
                    continue
                
                if key in rating_map:
                    lower, upper = rating_map[key]
                    rating_name = self.interval_to_linguistic(lower, upper)
                    index = combo.findText(rating_name)
                    if index >= 0:
                        combo.setCurrentIndex(index)
                else:
                    # Default to Fair if no rating
                    combo.setCurrentIndex(2)
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
        weights_calculated = all(c['weight'] > 0 for c in self.criteria)
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
                # Collect matrices for each expert
                for expert in self.experts:
                    ratings = database.get_topsis_ratings(self.main_window.get_project_id(), expert['id'])
                    
                    # Build matrix for this expert
                    n_alternatives = len(self.alternatives)
                    n_criteria = len(self.criteria)
                    matrix = np.zeros((n_alternatives, n_criteria, 2))
                    
                    # Fill with ratings or defaults
                    rating_map = {(r['alternative_id'], r['criterion_id']): (r['rating_lower'], r['rating_upper']) for r in ratings}
                    
                    for i, alt in enumerate(self.alternatives):
                        for j, crit in enumerate(self.criteria):
                            if (alt['id'], crit['id']) in rating_map:
                                matrix[i, j] = rating_map[(alt['id'], crit['id'])]
                            else:
                                # Default to Fair [3, 5] if missing
                                matrix[i, j] = [3, 5]
                    
                    expert_matrices.append(matrix)
            
            # Aggregate ratings
            aggregated_matrix = IntervalTOPSIS.aggregate_expert_ratings(expert_matrices)
            
            # Get weights
            weights = np.array([c['weight'] for c in self.criteria])
            
            # Get benefit/cost indicators
            is_benefit = np.array([c['is_benefit'] for c in self.criteria])
            
            # Calculate TOPSIS
            CC, results = IntervalTOPSIS.rank_alternatives(aggregated_matrix, weights, is_benefit)
            
            # Store results for the Results tab
            self.main_window.topsis_results = {
                'closeness_coefficients': CC,
                'ranking': results['ranking'],
                'distances_to_PIS': results['distances_to_PIS'],
                'distances_to_NIS': results['distances_to_NIS'],
                'alternatives': self.alternatives,
                'criteria': self.criteria,
                'aggregated_matrix': aggregated_matrix # Optional: store for display
            }
            
            # Refresh results tab
            self.main_window.results_tab.load_data()
            
            # Switch to results tab
            self.main_window.tabs.setCurrentIndex(3)
            
            QMessageBox.information(self, "Success", f"TOPSIS ranking calculated successfully!\nAggregated ratings from {len(self.experts)} experts.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to calculate ranking: {str(e)}")
