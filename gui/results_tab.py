"""
Results Tab Module
Displays final TOPSIS ranking results with visualization
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QTableWidget,
                             QTableWidgetItem, QPushButton, QLabel, QMessageBox,
                             QHeaderView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from utils.excel_handler import ExcelHandler


class ResultsTab(QWidget):
    """Results display tab"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Results table section
        table_group = QGroupBox("Final Rankings")
        table_layout = QVBoxLayout()
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels([
            "Rank", "Alternative", "Closeness Coefficient", "Distance to PIS", "Distance to NIS"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        table_layout.addWidget(self.results_table)
        
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        
        # Chart section
        chart_group = QGroupBox("Visualization")
        chart_layout = QVBoxLayout()
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(10, 4))
        self.canvas = FigureCanvas(self.figure)
        chart_layout.addWidget(self.canvas)
        
        chart_group.setLayout(chart_layout)
        layout.addWidget(chart_group)
        
        # Export button
        export_btn = QPushButton("Export Results to Excel")
        export_btn.clicked.connect(self.export_results)
        layout.addWidget(export_btn)
        
        self.setLayout(layout)
    
    def load_data(self):
        """Load and display results"""
        if not hasattr(self.main_window, 'topsis_results'):
            self.results_table.setRowCount(0)
            self.figure.clear()
            self.canvas.draw()
            return
        
        results = self.main_window.topsis_results
        
        # Populate results table
        alternatives = results['alternatives']
        ranking = results['ranking']
        CC = results['closeness_coefficients']
        dist_PIS = results['distances_to_PIS']
        dist_NIS = results['distances_to_NIS']
        
        self.results_table.setRowCount(len(alternatives))
        
        for rank, alt_idx in enumerate(ranking):
            alternative = alternatives[alt_idx]
            
            self.results_table.setItem(rank, 0, QTableWidgetItem(str(rank + 1)))
            self.results_table.setItem(rank, 1, QTableWidgetItem(alternative['name']))
            self.results_table.setItem(rank, 2, QTableWidgetItem(f"{CC[alt_idx]:.4f}"))
            self.results_table.setItem(rank, 3, QTableWidgetItem(f"{dist_PIS[alt_idx]:.4f}"))
            self.results_table.setItem(rank, 4, QTableWidgetItem(f"{dist_NIS[alt_idx]:.4f}"))
            
            # Highlight top 3
            if rank < 3:
                for col in range(5):
                    item = self.results_table.item(rank, col)
                    if rank == 0:
                        item.setBackground(QColor("#00CC66"))
                    elif rank == 1:
                        item.setBackground(Qt.GlobalColor.lightGray)
                    elif rank == 2:
                        item.setBackground(Qt.GlobalColor.yellow)
        
        # Create chart
        self.create_chart(results)
    
    def create_chart(self, results):
        """Create bar chart of closeness coefficients"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        alternatives = results['alternatives']
        ranking = results['ranking']
        CC = results['closeness_coefficients']
        
        # Prepare data in ranked order
        names = [alternatives[i]['name'] for i in ranking]
        scores = [CC[i] for i in ranking]
        
        # Create bar chart
        colors = ['#00CC66' if i == 0 else '#95a5a6' if i == 1 else '#f39c12' if i == 2 else '#3498db' 
                 for i in range(len(names))]
        
        bars = ax.barh(names, scores, color=colors)
        
        ax.set_xlabel('Closeness Coefficient (CCi)', fontsize=10, fontweight='bold')
        ax.set_ylabel('Alternatives', fontsize=10, fontweight='bold')
        ax.set_title('TOPSIS Ranking Results', fontsize=12, fontweight='bold')
        ax.set_xlim(0, 1)
        
        # Add value labels on bars
        for i, (bar, score) in enumerate(zip(bars, scores)):
            ax.text(score + 0.01, bar.get_y() + bar.get_height()/2, 
                   f'{score:.4f}', va='center', fontsize=9)
        
        ax.grid(axis='x', alpha=0.3)
        self.figure.tight_layout()
        self.canvas.draw()
    
    def export_results(self):
        """Export results to Excel"""
        if not hasattr(self.main_window, 'topsis_results'):
            QMessageBox.warning(self, "Warning", "No results to export!")
            return
        
        from PyQt6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Results", "TOPSIS_Results.xlsx", "Excel Files (*.xlsx)"
        )
        
        if file_path:
            self.export_to_excel(file_path)
    
    def export_to_excel(self, file_path):
        """Export results to Excel file"""
        if not hasattr(self.main_window, 'topsis_results'):
            raise ValueError("No results available")
        
        db = self.main_window.get_db_manager()
        with db as database:
            # Get project info
            project = database.get_project()
            
            # Get criteria with weights
            criteria = database.get_criteria(self.main_window.get_project_id())
            
            # Get alternatives
            alternatives = database.get_alternatives(self.main_window.get_project_id())
            
            # Prepare weights dict
            weights = {
                'cr': getattr(self.main_window, 'ahp_cr', 0.0)
            }
            
            # Get TOPSIS results
            topsis_results = self.main_window.topsis_results
            
            # Export
            ExcelHandler.export_results(
                project, criteria, alternatives, weights, topsis_results, file_path
            )
