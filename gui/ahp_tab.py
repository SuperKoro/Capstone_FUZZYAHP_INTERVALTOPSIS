"""
AHP Tab Module
Handles Fuzzy AHP evaluation and weight calculation
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QTableWidget,
                             QTableWidgetItem, QPushButton, QLabel, QComboBox, QMessageBox,
                             QFileDialog, QRadioButton, QButtonGroup, QHeaderView, QLineEdit,
                             QTreeWidget, QTreeWidgetItem, QTextEdit, QTabWidget, QListView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
import numpy as np
import sqlite3
from database.manager import DatabaseManager
from algorithms.fuzzy_ahp import FuzzyAHP
from algorithms.hierarchical_ahp import HierarchicalFuzzyAHP
from commands.expert_commands import AddExpertCommand, DeleteExpertCommand, SetExpertWeightCommand, RenameExpertCommand
from commands.ahp_commands import BatchSaveComparisonsCommand, ImportExpertCommand
from utils.excel_handler import ExcelHandler
from utils.validators import Validators


class NoScrollComboBox(QComboBox):
    """Custom QComboBox that disables mouse wheel scrolling"""
    
    def wheelEvent(self, event):
        """Ignore wheel events to prevent accidental selection changes"""
        event.ignore()


class AHPTab(QWidget):
    """Fuzzy AHP evaluation tab"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.criteria = []
        self.experts = []
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface with sub-tabs"""
        # Main layout for the entire AHP tab
        main_layout = QVBoxLayout()
        
        # Create tab widget for Input and Results
        self.tab_widget = QTabWidget()
        
        # Create Input tab
        input_tab = self.create_input_tab()
        self.tab_widget.addTab(input_tab, "Input & Comparisons")
        
        # Create Results tab
        results_tab = self.create_results_tab()
        self.tab_widget.addTab(results_tab, "Results")
        
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)
    
    def create_input_tab(self):
        """Create the input and comparisons tab"""
        input_widget = QWidget()
        
        # Left panel: Criteria Tree Navigation
        left_panel = QVBoxLayout()
        left_panel_widget = QWidget()
        left_panel_widget.setMaximumWidth(350)
        
        tree_label = QLabel("Criteria Hierarchy")
        tree_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        left_panel.addWidget(tree_label)
        
        # Tree widget for navigation
        self.criteria_tree = QTreeWidget()
        self.criteria_tree.setHeaderLabel("Select to Compare")
        self.criteria_tree.itemClicked.connect(self.on_tree_item_clicked)
        left_panel.addWidget(self.criteria_tree)
        
        instructions = QLabel(
            "Click on a node to compare its children.\n"
            "✓ = Comparisons completed"
        )
        instructions.setStyleSheet("color: gray; font-size: 10px;")
        instructions.setWordWrap(True)
        left_panel.addWidget(instructions)
        
        # Expert Management Section in Left Panel (bottom)
        experts_group = QGroupBox("Experts")
        experts_layout = QVBoxLayout()
        
        self.expert_table = QTableWidget()
        self.expert_table.setColumnCount(4)  # Added Weight columnp
        self.expert_table.setHorizontalHeaderLabels(["ID", "Name", "Weight", "Delete"])
        
        # Set resize modes for better visibility
        header = self.expert_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Name stretches
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)     # Weight fixed
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)     # Actions fixed
        
        # Set column widths
        self.expert_table.setColumnWidth(2, 70)   # Weight column
        self.expert_table.setColumnWidth(3, 60)   # Actions column - compact for "-" button
        
        self.expert_table.hideColumn(0) # Hide ID
        self.expert_table.setMinimumHeight(150)
        self.expert_table.itemChanged.connect(self.on_expert_table_item_changed)
        experts_layout.addWidget(self.expert_table)
        
        # Weight status label
        self.weight_status_label = QLabel("")
        self.weight_status_label.setStyleSheet("color: #666; font-size: 10px; font-style: italic;")
        self.weight_status_label.setWordWrap(True)
        experts_layout.addWidget(self.weight_status_label)
        
        add_expert_btn = QPushButton("Add New Expert")
        add_expert_btn.clicked.connect(self.add_expert)
        experts_layout.addWidget(add_expert_btn)
        
        import_expert_btn = QPushButton("Import Expert (.mcdm)")
        import_expert_btn.clicked.connect(self.import_expert_from_mcdm)
        experts_layout.addWidget(import_expert_btn)
        
        experts_group.setLayout(experts_layout)
        left_panel.addWidget(experts_group)
        
        left_panel_widget.setLayout(left_panel)
        
        # Right panel: Comparison area
        right_layout = QVBoxLayout()
        
        # Instruction Labels (English & Vietnamese)
        guide_layout = QHBoxLayout()
        
        # English Guide
        guide_label_en = QLabel(
            "<b>How to Compare:</b> How important is <b>Criterion 1</b> compared to <b>Criterion 2</b>?<br>"
            "• Select <b>2 to 9</b> if Criterion 1 is more important.<br>"
            "• Select <b>-2 to -9</b> if Criterion 2 is more important.<br>"
            "• Select <b>1</b> if they are equal."
        )
        guide_label_en.setStyleSheet("""
            QLabel {
                background-color: #e8f4f8;
                color: #2c3e50;
                padding: 8px;
                border-radius: 4px;
                border: 1px solid #b3e5fc;
                font-size: 12px;
            }
        """)
        guide_label_en.setWordWrap(True)
        guide_layout.addWidget(guide_label_en)
        
        # Vietnamese Guide
        guide_label_vn = QLabel(
            "<b>Hướng dẫn so sánh:</b> <b>Tiêu chí 1</b> quan trọng như thế nào so với <b>Tiêu chí 2</b>?<br>"
            "• Chọn <b>2 đến 9</b> nếu Tiêu chí 1 quan trọng hơn.<br>"
            "• Chọn <b>-2 đến -9</b> nếu Tiêu chí 2 quan trọng hơn.<br>"
            "• Chọn <b>1</b> nếu hai tiêu chí quan trọng như nhau."
        )
        guide_label_vn.setStyleSheet("""
            QLabel {
                background-color: #e8f4f8;
                color: #2c3e50;
                padding: 8px;
                border-radius: 4px;
                border: 1px solid #b3e5fc;
                font-size: 12px;
            }
        """)
        guide_label_vn.setWordWrap(True)
        guide_layout.addWidget(guide_label_vn)
        
        right_layout.addLayout(guide_layout)
        
        # Top bar: Expert Selection
        top_bar = QHBoxLayout()
        top_bar.addWidget(QLabel("Current Expert:"))
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
        top_bar.addWidget(self.expert_combo, 1)
        right_layout.addLayout(top_bar)
        
        # Pairwise Comparisons section
        comp_group = QGroupBox("Pairwise Comparisons")
        comp_layout = QVBoxLayout()
        
        self.context_label = QLabel("Select a criterion from the tree to begin comparisons")
        self.context_label.setStyleSheet("font-weight: bold; color: #333;")
        comp_layout.addWidget(self.context_label)
        
        self.comparison_table = QTableWidget()
        self.comparison_table.itemClicked.connect(self.on_comparison_cell_clicked)
        
        # Disable auto-scroll behavior
        self.comparison_table.setAutoScroll(False)
        comp_layout.addWidget(self.comparison_table)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save Comparisons")
        save_btn.clicked.connect(self.save_comparisons)
        button_layout.addWidget(save_btn)
        
        calc_btn = QPushButton("Calculate All Weights")
        calc_btn.clicked.connect(self.calculate_weights)
        calc_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        button_layout.addWidget(calc_btn)
        
        comp_layout.addLayout(button_layout)
        
        # Inconsistent Pairs Section
        self.inconsistency_text = QTextEdit()
        self.inconsistency_text.setReadOnly(True)
        self.inconsistency_text.setMaximumHeight(50)  # Reduced from 80 to save space
        self.inconsistency_text.setPlaceholderText("Inconsistent comparison pairs will be displayed here after weight calculation...")
        self.inconsistency_text.setStyleSheet("background-color: #FFF3CD; border: 1px solid #FFC107; padding: 5px;")
        comp_layout.addWidget(QLabel("Inconsistent Comparisons:"))
        comp_layout.addWidget(self.inconsistency_text)
        
        comp_group.setLayout(comp_layout)
        right_layout.addWidget(comp_group, 1)
        
        # Assemble input tab layout
        tab_layout = QHBoxLayout()
        tab_layout.addWidget(left_panel_widget)
        tab_layout.addLayout(right_layout, stretch=1)
        input_widget.setLayout(tab_layout)
        
        # Track current comparison context
        self.current_node = None
        self.current_children = []
        
        return input_widget
    
    def create_results_tab(self):
        """Create the results display tab"""
        results_widget = QWidget()
        results_main_layout = QVBoxLayout()
        
        # Results section
        results_group = QGroupBox("Calculated Weights")
        results_layout = QVBoxLayout()
        
        self.weights_table = QTableWidget()
        self.weights_table.setColumnCount(3)
        self.weights_table.setHorizontalHeaderLabels(["Criterion", "Weight", "Percentage"])
        
        # Better column sizing for easier viewing
        self.weights_table.setColumnWidth(0, 400)  # Criterion name column - wider
        self.weights_table.setColumnWidth(1, 150)  # Weight column
        self.weights_table.setColumnWidth(2, 150)  # Percentage column
        self.weights_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.weights_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.weights_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        
        # Much larger rows for better visibility
        self.weights_table.verticalHeader().setDefaultSectionSize(40)
        
        # Much larger font for results
        self.weights_table.setStyleSheet("""
            QTableWidget {
                font-size: 14px;
            }
            QHeaderView::section {
                font-size: 12px;
                font-weight: bold;
            }
        """)
        
        # Make the table take more space
        self.weights_table.setMinimumHeight(200)
        results_layout.addWidget(self.weights_table)
        
        # Consistency Metrics Group
        metrics_group = QGroupBox("Consistency Metrics")
        metrics_layout = QHBoxLayout()
        
        # Lambda Max
        self.lambda_label = QLabel("λmax: -")
        self.lambda_label.setStyleSheet("font-weight: bold;")
        metrics_layout.addWidget(self.lambda_label)
        
        # n (Matrix Size)
        self.n_label = QLabel("n: -")
        self.n_label.setStyleSheet("font-weight: bold;")
        metrics_layout.addWidget(self.n_label)
        
        # CI
        self.ci_label = QLabel("CI: -")
        self.ci_label.setStyleSheet("font-weight: bold;")
        metrics_layout.addWidget(self.ci_label)
        
        # CR
        self.cr_label = QLabel("CR: -")
        self.cr_label.setStyleSheet("font-weight: bold;")
        metrics_layout.addWidget(self.cr_label)
        
        metrics_group.setLayout(metrics_layout)
        results_layout.addWidget(metrics_group)  # Add metrics group to results layout
        
        results_group.setLayout(results_layout)
        results_main_layout.addWidget(results_group)
        
        results_widget.setLayout(results_main_layout)
        return results_widget
    
    
    def build_criteria_tree(self):
        """Build the criteria tree for navigation"""
        self.criteria_tree.clear()
        
        if not self.criteria:
            return
        
        # Create root node (Goal)
        root = QTreeWidgetItem(self.criteria_tree)
        root.setText(0, "Goal (Main Criteria)")
        root.setData(0, Qt.ItemDataRole.UserRole, {'type': 'root', 'children': []})
        
        # Make root bold and blue
        font = root.font(0)
        font.setBold(True)
        root.setFont(0, font)
        root.setForeground(0, QColor(52, 114, 196))
        
        # Build tree structure
        items_by_id = {}
        
        # First pass: create all items
        for criterion in self.criteria:
            item = QTreeWidgetItem()
            item.setText(0, criterion['name'])
            item.setData(0, Qt.ItemDataRole.UserRole, {
                'type': 'criterion',
                'id': criterion['id'],
                'name': criterion['name'],
                'parent_id': criterion.get('parent_id'),
                'children': []
            })
            items_by_id[criterion['id']] = item
        
        # Second pass: build hierarchy
        main_criteria = []
        for criterion in self.criteria:
            item = items_by_id[criterion['id']]
            parent_id = criterion.get('parent_id')
            
            if parent_id is None:
                # Main criterion - add to root
                root.addChild(item)
                main_criteria.append(criterion)
            elif parent_id in items_by_id:
                # Sub-criterion - add to parent
                items_by_id[parent_id].addChild(item)
        
        # Store children info in root
        root_data = root.data(0, Qt.ItemDataRole.UserRole)
        root_data['children'] = main_criteria
        root.setData(0, Qt.ItemDataRole.UserRole, root_data)
        
        # Store children info in each parent
        for criterion in self.criteria:
            if criterion['id'] in items_by_id:
                item = items_by_id[criterion['id']]
                children = [c for c in self.criteria if c.get('parent_id') == criterion['id']]
                item_data = item.data(0, Qt.ItemDataRole.UserRole)
                item_data['children'] = children
                item.setData(0, Qt.ItemDataRole.UserRole, item_data)
        
        root.setExpanded(True)
    
    def on_tree_item_clicked(self, item, column):
        """Handle tree item click - show comparison matrix for children"""
        # Safety check: widget might be deleted after refresh
        try:
            if not item:
                return
            
            # Access item properties - may raise RuntimeError if deleted
            node_name = item.text(0)
            data = item.data(0, Qt.ItemDataRole.UserRole)
        except RuntimeError:
            # Widget was deleted (happens after refresh)
            print("Tree item no longer valid, ignoring click")
            return
        
        if not data:
            return
        
        children = data.get('children', [])
        
        if len(children) < 2:
            # Leaf node or only one child
            self.context_label.setText(f"'{node_name}' has no children to compare")
            self.comparison_table.setRowCount(0)
            self.current_node = None
            self.current_children = []
            return
        
        # Check if experts exist before allowing comparisons
        if not self.experts:
            reply = QMessageBox.question(
                self,
                "No Experts Found",
                "You need to add at least one expert to perform comparisons.\n\nWould you like to add an expert now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.add_expert()
                # After adding expert, check again
                if not self.experts:
                    # User cancelled expert creation
                    self.context_label.setText("Please add an expert to begin comparisons")
                    self.comparison_table.setRowCount(0)
                    return
            else:
                self.context_label.setText("Please add an expert to begin comparisons")
                self.comparison_table.setRowCount(0)
                return
        
        # Show comparison matrix for children
        self.current_node = data
        self.current_children = children
        
        self.context_label.setText(f"Comparing children of: {node_name} ({len(children)} criteria)")
        
        self.setup_comparison_table_for_children(children)
    
    def load_data(self):
        """Load data from database"""
        db = self.main_window.get_db_manager()
        if not db:
            return
            
        # Reset view state
        self.current_node = None
        self.current_children = []
        self.comparison_table.setRowCount(0)
        self.weights_table.setRowCount(0)
        self.weights_table.setRowCount(0)
        self.lambda_label.setText("λmax: -")
        self.n_label.setText("n: -")
        self.ci_label.setText("CI: -")
        self.cr_label.setText("CR: -")
        self.cr_label.setStyleSheet("font-weight: bold;")
        
        # Get hierarchical criteria structure - ALWAYS from DB to get latest weights
        with db as database:
            # Load ALL criteria with weights from database
            self.criteria = database.get_criteria(self.main_window.get_project_id())
            # Leaf criteria are same for now
            criteria_ids = {c['id'] for c in self.criteria}
            parent_ids = {c['parent_id'] for c in self.criteria if c.get('parent_id') is not None}
            leaf_ids = criteria_ids - parent_ids
            self.leaf_criteria = [c for c in self.criteria if c['id'] in leaf_ids]
        
        with db as database:
            # Load experts
            self.experts = database.get_experts(self.main_window.get_project_id())
            self.populate_expert_table()
            
            # Update expert combo
            self.expert_combo.blockSignals(True)
            self.expert_combo.clear()
            for expert in self.experts:
                self.expert_combo.addItem(expert['name'], expert['id'])
            self.expert_combo.blockSignals(False)
        
        # Build criteria tree for navigation
        self.build_criteria_tree()
        
        # NEW: Auto-load weights if they exist for current scenario
        self.load_existing_weights()
    
    def load_existing_weights(self):
        """Load and display weights if already calculated for current scenario"""
        if not self.criteria:
            return
        
        # Check if any criteria have weights > 0
        has_weights = any(c.get('weight', 0) > 0 for c in self.criteria)
        
        if has_weights:
            # Build global_weights dict
            global_weights = {c['id']: c.get('weight', 0) for c in self.criteria}
            
            # Display results (consistency info not available from DB, will show as "-")
            self.display_hierarchical_weights(global_weights, consistency_info={})
    
    def populate_expert_table(self):
        """Populate expert table"""
        # Block signals while populating
        self.expert_table.blockSignals(True)
        self.expert_table.setRowCount(len(self.experts))
        
        for row, expert in enumerate(self.experts):
            # ID (hidden)
            self.expert_table.setItem(row, 0, QTableWidgetItem(str(expert['id'])))
            
            # Name (editable)
            name_item = QTableWidgetItem(expert['name'])
            # Name is now editable
            self.expert_table.setItem(row, 1, name_item)
            
            # Weight (editable)
            weight_item = QTableWidgetItem()
            weight = expert.get('weight')
            if weight is not None:
                weight_item.setText(f"{weight:.3f}")
            # Empty if NULL - user can enter or leave empty for auto
            self.expert_table.setItem(row, 2, weight_item)
            
            # Actions (Delete)
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(2, 2, 2, 2)
            actions_layout.setSpacing(0)
            
            delete_btn = QPushButton("")
            delete_btn.setProperty("class", "danger")
            delete_btn.setFixedSize(50, 30)  # Fit within column width (60)
            delete_btn.setStyleSheet("""
                QPushButton {
                    border-radius: 0px;
                    padding-left: 5px;
                    padding-top: 2px;
                    text-align: left;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #C82333;
                }
            """)
            delete_btn.setToolTip("Delete Expert")
            delete_btn.clicked.connect(lambda checked, e_id=expert['id']: self.delete_expert(e_id))
            
            # Center the button in the layout
            actions_layout.addStretch()
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            
            actions_widget.setLayout(actions_layout)
            self.expert_table.setCellWidget(row, 3, actions_widget)  # Column 3 now
        
        self.expert_table.blockSignals(False)
        self.update_weight_display()
    
    def on_expert_table_item_changed(self, item):
        """Handle changes in expert table (name or weight)"""
        column = item.column()
        
        if column == 1:  # Name column
            self.on_expert_name_changed(item)
        elif column == 2:  # Weight column
            self.on_expert_weight_changed(item)
    
    def on_expert_name_changed(self, item):
        """Handle expert name changes with validation"""
        row = item.row()
        expert_id = int(self.expert_table.item(row, 0).text())
        new_name = item.text().strip()
        
        # Get old name
        old_name = self.experts[row]['name']
        
        # If name hasn't changed, do nothing
        if new_name == old_name:
            return
        
        # Validate name
        valid, error = Validators.validate_expert_name(new_name)
        if not valid:
            QMessageBox.warning(self, "Validation Error", error)
            # Revert to old name
            self.expert_table.blockSignals(True)
            item.setText(old_name)
            self.expert_table.blockSignals(False)
            return
        
        # Update via UndoManager
        db = self.main_window.get_db_manager()
        undo_manager = self.main_window.get_undo_manager()
        
        command = RenameExpertCommand(db, expert_id, new_name)
        if undo_manager.execute(command):
            # Update local data and combo box
            self.load_data()
            # Refresh TOPSIS tab to update expert name there too
            if hasattr(self.main_window, 'topsis_tab'):
                self.main_window.topsis_tab.load_data()
            QMessageBox.information(self, "Success", f"Expert renamed to '{new_name}'")
        else:
            # Revert UI if failed
            self.expert_table.blockSignals(True)
            item.setText(old_name)
            self.expert_table.blockSignals(False)
            QMessageBox.critical(self, "Error", "Failed to rename expert.")
    
    def on_expert_weight_changed(self, item):
        """Handle weight cell changes with auto-distribution"""
        if item.column() != 2:  # Only handle weight column
            return
        
        row = item.row()
        expert_id = int(self.expert_table.item(row, 0).text())
        weight_text = item.text().strip()
        
        try:
            # Parse weight
            if weight_text == "":
                weight = None
            else:
                weight = float(weight_text)
                if weight < 0 or weight > 1:
                    raise ValueError("Weight must be between 0 and 1")
            
            # Update via UndoManager
            db = self.main_window.get_db_manager()
            undo_manager = self.main_window.get_undo_manager()
            
            command = SetExpertWeightCommand(db, expert_id, weight)
            if undo_manager.execute(command):
                self.update_weight_display()
            else:
                # Revert UI if failed
                self.update_weight_display()
                QMessageBox.critical(self, "Error", "Failed to update weight.")
                self.load_data()
            
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Weight", str(e))
            self.load_data()  # Revert
    
    def update_weight_display(self):
        """Update weight display with auto-calculated values and explanation"""
        db = self.main_window.get_db_manager()
        project_id = self.main_window.get_project_id()
        
        with db as database:
            weights = database.get_expert_weights(project_id)
        
        if not weights:
            self.weight_status_label.setText("")
            return
        
        # Update table display
        self.expert_table.blockSignals(True)
        for row in range(self.expert_table.rowCount()):
            expert_id = int(self.expert_table.item(row, 0).text())
            if expert_id in weights:
                weight = weights[expert_id]
                weight_item = self.expert_table.item(row, 2)
                if weight_item:
                    # Get database value
                    expert = next(e for e in self.experts if e['id'] == expert_id)
                    db_weight = expert.get('weight')
                    
                    if db_weight is None:
                        # Auto-calculated - show in italics
                        weight_item.setText(f"{weight:.3f}")
                        font = weight_item.font()
                        font.setItalic(True)
                        weight_item.setFont(font)
                        weight_item.setForeground(QColor(100, 100, 100))
                    else:
                        # User-entered
                        weight_item.setText(f"{weight:.3f}")
                        font = weight_item.font()
                        font.setItalic(False)
                        weight_item.setFont(font)
                        weight_item.setForeground(QColor(0, 0, 0))
        self.expert_table.blockSignals(False)
        
        # Generate explanation
        filled_count = sum(1 for e in self.experts if e.get('weight') is not None)
        total_count = len(self.experts)
        
        if filled_count == 0:
            msg = f"ℹ️ All {total_count} experts have equal weight (1/{total_count:.3f} each)"
        elif filled_count == total_count:
            total = sum(weights.values())
            if abs(total - 1.0) < 0.001:
                msg = "✓ All weights manually set and sum to 1.0"
            else:
                msg = f"⚠️ Warning: Manually set weights sum to {total:.3f} (should be 1.0)"
        else:
            filled_sum = sum(e.get('weight', 0) for e in self.experts if e.get('weight') is not None)
            remaining = 1.0 - filled_sum
            auto_count = total_count - filled_count
            auto_weight = remaining / auto_count if auto_count > 0 else 0
            msg = (f"ℹ️ {filled_count} weights set manually (sum={filled_sum:.3f}), "
                  f"{auto_count} auto-assigned ({auto_weight:.3f} each, italic)")
        
        self.weight_status_label.setText(msg)
            
    def on_expert_changed(self, index):
        """Handle expert selection change"""
        # Auto-save PREVIOUS expert's comparisons before switching
        # (We need to do this BEFORE the combo box changes)
        if hasattr(self, '_previous_expert_id') and self._previous_expert_id is not None:
            self.auto_save_comparisons_for_expert(self._previous_expert_id)
        
        # Update previous expert ID for next change
        if index >= 0:
            self._previous_expert_id = self.expert_combo.itemData(index)
        
        # Load new expert's comparisons
        if self.current_children:
            self.setup_comparison_table_for_children(self.current_children)
    
    def on_comparison_cell_clicked(self, item):
        """Handle click on any cell in comparison table - open dropdown for that row"""
        if item is None:
            return
        
        row = item.row()
        # Get the combobox widget in column 2 (Importance Scale)
        combo_widget = self.comparison_table.cellWidget(row, 2)
        
        if combo_widget:
            # Set focus and show dropdown
            combo_widget.setFocus()
            combo_widget.showPopup()
    
    
    def setup_comparison_table_for_children(self, children):
        """Setup comparison table for a specific set of children criteria"""
        n = len(children)
        if n < 2:
            return
        
        # Calculate number of comparisons
        num_comparisons = (n * (n - 1)) // 2
        
        self.comparison_table.setRowCount(num_comparisons)
        self.comparison_table.setColumnCount(3)
        self.comparison_table.setHorizontalHeaderLabels(["Criterion 1", "Criterion 2", "Importance Scale"])
        
        # Make columns resizable
        self.comparison_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.comparison_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.comparison_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        # Set column widths
        self.comparison_table.setColumnWidth(0, 200)
        self.comparison_table.setColumnWidth(1, 200)
        self.comparison_table.setColumnWidth(2, 400)
        
        # Enable stretching
        self.comparison_table.horizontalHeader().setStretchLastSection(True)
        
        # Make rows taller for better visibility
        self.comparison_table.verticalHeader().setDefaultSectionSize(50)
        
        row = 0
        for i in range(n):
            for j in range(i + 1, n):
                # Criterion names
                item1 = QTableWidgetItem(children[i]['name'])
                item1.setFlags(item1.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Read-only
                self.comparison_table.setItem(row, 0, item1)
                
                item2 = QTableWidgetItem(children[j]['name'])
                item2.setFlags(item2.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Read-only
                self.comparison_table.setItem(row, 1, item2)
                
                # Scale combo with autocomplete
                scale_combo = self.create_scale_combo()
                
                # Connect signal to save immediately on change
                scale_combo.currentIndexChanged.connect(lambda index, r=row: self.save_single_comparison(r))
                
                self.comparison_table.setCellWidget(row, 2, scale_combo)
                row += 1
        
        # Load existing comparisons for the selected expert
        self.load_existing_comparisons(children)

    def load_existing_comparisons(self, children):
        """Load existing comparisons into the table"""
        if self.expert_combo.currentIndex() < 0:
            return
            
        expert_id = self.expert_combo.currentData()
        project_id = self.main_window.get_project_id()
        
        db = self.main_window.get_db_manager()
        with db as database:
            # Get all comparisons for this expert
            comparisons = database.get_ahp_comparisons(
                project_id,
                scenario_id=self.main_window.current_scenario_id  # NEW
            )
            # Filter for this expert
            comparisons = [c for c in comparisons if c['expert_id'] == expert_id]
            
        if not comparisons:
            return
            
        # Create lookup map: (id1, id2) -> fuzzy_m
        comp_map = {}
        for comp in comparisons:
            comp_map[(comp['criterion1_id'], comp['criterion2_id'])] = comp['fuzzy_m']
            
        # Iterate table rows
        n = len(children)
        row = 0
        for i in range(n):
            for j in range(i + 1, n):
                c1_id = children[i]['id']
                c2_id = children[j]['id']
                
                val_m = None
                if (c1_id, c2_id) in comp_map:
                    val_m = comp_map[(c1_id, c2_id)]
                elif (c2_id, c1_id) in comp_map:
                    # Reciprocal found (c2 vs c1)
                    val_m = 1.0 / comp_map[(c2_id, c1_id)]
                
                if val_m is not None:
                    # Find closest scale value
                    closest_scale = 1
                    min_diff = float('inf')
                    
                    for scale_val, values in FuzzyAHP.LINGUISTIC_SCALE.items():
                        # values is (l, m, u, desc)
                        m = values[1]
                        diff = abs(m - val_m)
                        if diff < min_diff:
                            min_diff = diff
                            closest_scale = scale_val
                    
                    # Set combo box
                    scale_combo = self.comparison_table.cellWidget(row, 2)
                    if scale_combo:
                        # Find index for this scale value
                        index = scale_combo.findData(closest_scale)
                        if index >= 0:
                            scale_combo.setCurrentIndex(index)
                
                row += 1
    
    def create_scale_combo(self):
        """Create a scale combo box with autocomplete feature"""
        from PyQt6.QtWidgets import QCompleter, QListView
        from PyQt6.QtCore import Qt as QtCore
        
        scale_combo = NoScrollComboBox()
        scale_combo.setEditable(False)  # Disable typing - dropdown only
        
        # Set view to QListView to ensure styling works
        scale_combo.setView(QListView())
        
        scale_combo.setStyleSheet("""
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
            
            /* Style the view (dropdown list) */
            QComboBox QListView {
                border: 1px solid #ccc;
                background-color: white;
                outline: none;
            }
            QComboBox QListView::item {
                border-bottom: 1px solid #e0e0e0;  /* Separator line */
                padding: 8px;
                min-height: 25px;
                color: black;
            }
            QComboBox QListView::item:hover {
                background-color: #00CED1;  /* Cyan on hover */
                color: white;
            }
            QComboBox QListView::item:selected {
                background-color: #00CED1;  /* Cyan when selected */
                color: white;
            }
        """)
        
        scale_values = [-9, -8, -7, -6, -5, -4, -3, -2, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        
        # Build items with searchable text
        items = []
        for val in scale_values:
            desc = FuzzyAHP.LINGUISTIC_SCALE[val][3]
            label = f"{val:2d}: {desc}"
            scale_combo.addItem(label, val)
            items.append(label)
        
        # Set default to 1 (equal)
        scale_combo.setCurrentIndex(8)
        
        return scale_combo
    
    def save_single_comparison(self, row):
        """Save a single comparison change immediately"""
        expert_id = self.expert_combo.currentData()
        if expert_id is None or not self.current_node:
            return
        
        # Get the criteria IDs from the table
        criterion1_name = self.comparison_table.item(row, 0).text()
        criterion2_name = self.comparison_table.item(row, 1).text()
        
        # Find criterion IDs
        criterion1_id = None
        criterion2_id = None
        for c in self.criteria:
            if c['name'] == criterion1_name:
                criterion1_id = c['id']
            if c['name'] == criterion2_name:
                criterion2_id = c['id']
        
        if not criterion1_id or not criterion2_id:
            return
        
        # Get the comparison value
        combo = self.comparison_table.cellWidget(row, 2)
        if not combo:
            return
        
        value = combo.currentData()
        
        # Convert to fuzzy triangular number
        fuzzy_l, fuzzy_m, fuzzy_u = FuzzyAHP.get_fuzzy_number(value)
        
        # Save to database
        db = self.main_window.get_db_manager()
        if db:
            project_id = self.main_window.get_project_id()
            with db as database:
                database.add_ahp_comparison(
                    project_id,
                    expert_id,
                    criterion1_id,
                    criterion2_id,
                    fuzzy_l,
                    fuzzy_m,
                    fuzzy_u,
                    scenario_id=self.main_window.current_scenario_id
                )
    
    def add_expert(self):
        """Add a new expert"""
        from PyQt6.QtWidgets import QDialog, QFormLayout, QDialogButtonBox
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Expert")
        layout = QFormLayout()
        name_input = QLineEdit()
        layout.addRow("Expert Name:", name_input)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        dialog.setLayout(layout)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = name_input.text()
            valid, error = Validators.validate_expert_name(name)
            if not valid:
                QMessageBox.warning(self, "Validation Error", error)
                return
            # Add to database via UndoManager
            db = self.main_window.get_db_manager()
            project_id = self.main_window.get_project_id()
            undo_manager = self.main_window.get_undo_manager()
            
            command = AddExpertCommand(db, project_id, name)
            if undo_manager.execute(command):
                self.load_data()
                # Also refresh TOPSIS tab so expert appears there
                self.main_window.topsis_tab.load_data()
                QMessageBox.information(self, "Success", "Expert added successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to add expert.")
                return

    def delete_expert(self, expert_id):
        """Delete an expert"""
        reply = QMessageBox.question(
            self, "Confirm Delete", 
            "Are you sure you want to delete this expert? All their comparisons will be lost.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Delete via UndoManager
            db = self.main_window.get_db_manager()
            undo_manager = self.main_window.get_undo_manager()
            
            command = DeleteExpertCommand(db, expert_id)
            if undo_manager.execute(command):
                self.load_data()
                QMessageBox.information(self, "Success", "Expert deleted!")
            else:
                QMessageBox.critical(self, "Error", "Failed to delete expert.")

    def import_expert_from_mcdm(self):
        """Import all experts and comparisons from a .mcdm file with validation"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Expert Data", "", "MCDM Files (*.mcdm);;All Files (*)"
        )
        
        if not file_path:
            return
            
        try:
            # Connect to external DB
            ext_conn = sqlite3.connect(file_path)
            ext_conn.row_factory = sqlite3.Row
            ext_cursor = ext_conn.cursor()
            
            # Validate project structure - Check criteria
            ext_cursor.execute("SELECT name FROM criteria ORDER BY name")
            ext_criteria_names = sorted([row['name'] for row in ext_cursor.fetchall()])
            
            local_criteria_names = sorted([c['name'] for c in self.criteria])
            
            if ext_criteria_names != local_criteria_names:
                ext_conn.close()
                QMessageBox.critical(
                    self, "Import Failed",
                    "Cannot import: Criteria do not match between projects.\n\n"
                    f"This project has {len(local_criteria_names)} criteria.\n"
                    f"Import file has {len(ext_criteria_names)} criteria.\n\n"
                    "Both projects must have identical criteria (same names) for import to work."
                )
                return
            
            # Validate alternatives
            ext_cursor.execute("SELECT name FROM alternatives ORDER BY name")
            ext_alt_names = sorted([row['name'] for row in ext_cursor.fetchall()])
            
            db = self.main_window.get_db_manager()
            project_id = self.main_window.get_project_id()
            
            with db as database:
                local_alternatives = database.get_alternatives(project_id)
            local_alt_names = sorted([a['name'] for a in local_alternatives])
            
            if ext_alt_names != local_alt_names:
                ext_conn.close()
                QMessageBox.critical(
                    self, "Import Failed",
                    "Cannot import: Alternatives do not match between projects.\n\n"
                    f"This project has {len(local_alt_names)} alternatives.\n"
                    f"Import file has {len(ext_alt_names)} alternatives.\n\n"
                    "Both projects must have identical alternatives (same names) for import to work."
                )
                return
            
            # Get all experts from external DB
            ext_cursor.execute("SELECT * FROM experts")
            ext_experts = [dict(row) for row in ext_cursor.fetchall()]
            
            if not ext_experts:
                QMessageBox.warning(self, "Warning", "No experts found in the selected file.")
                ext_conn.close()
                return
            
            # Get criteria mapping (External Name -> Local ID)
            local_criteria_map = {c['name']: c['id'] for c in self.criteria}
            
            # Prepare data for command
            experts_to_import = []
            comparisons_to_import = []
            
            # Process experts
            for ext_expert in ext_experts:
                experts_to_import.append({
                    'name': ext_expert['name'],
                    'weight': ext_expert.get('weight'),
                    'external_id': ext_expert['id']
                })
                
                # Get comparisons for this expert
                ext_cursor.execute(
                    "SELECT * FROM ahp_comparisons WHERE expert_id = ?", 
                    (ext_expert['id'],)
                )
                ext_comparisons = [dict(row) for row in ext_cursor.fetchall()]
                
                # Get external criteria mapping
                ext_cursor.execute("SELECT * FROM criteria")
                ext_criteria = {c['id']: c['name'] for c in [dict(row) for row in ext_cursor.fetchall()]}
                
                # Process comparisons
                for comp in ext_comparisons:
                    c1_name = ext_criteria.get(comp['criterion1_id'])
                    c2_name = ext_criteria.get(comp['criterion2_id'])
                    
                    if c1_name in local_criteria_map and c2_name in local_criteria_map:
                        comparisons_to_import.append({
                            'external_expert_id': ext_expert['id'],
                            'c1_id': local_criteria_map[c1_name],
                            'c2_id': local_criteria_map[c2_name],
                            'l': comp['fuzzy_l'],
                            'm': comp['fuzzy_m'],
                            'u': comp['fuzzy_u']
                        })
            
            # ============================================================
            # IMPORTANT: Also import TOPSIS ratings for these experts
            # ============================================================
            topsis_ratings_to_import = []
            
            # Get local alternatives mapping
            with db as database:
                local_alternatives = database.get_alternatives(project_id)
            local_alt_map = {alt['name']: alt['id'] for alt in local_alternatives}
            
            # Get external alternatives mapping
            ext_cursor.execute("SELECT * FROM alternatives")
            ext_alternatives = {alt['id']: alt['name'] for alt in [dict(row) for row in ext_cursor.fetchall()]}
            
            # Process TOPSIS ratings for each expert
            for ext_expert in ext_experts:
                # Get TOPSIS ratings for this expert from external DB
                ext_cursor.execute(
                    "SELECT * FROM topsis_ratings WHERE expert_id = ?",
                    (ext_expert['id'],)
                )
                ext_ratings = [dict(row) for row in ext_cursor.fetchall()]
                
                for rating in ext_ratings:
                    # Map external IDs to local IDs via names
                    alt_name = ext_alternatives.get(rating['alternative_id'])
                    crit_name = ext_criteria.get(rating['criterion_id'])
                    
                    if alt_name in local_alt_map and crit_name in local_criteria_map:
                        topsis_ratings_to_import.append({
                            'external_expert_id': ext_expert['id'],
                            'alternative_id': local_alt_map[alt_name],
                            'criterion_id': local_criteria_map[crit_name],
                            'rating_lower': rating['rating_lower'],
                            'rating_upper': rating['rating_upper'],
                            'scenario_id': self.main_window.current_scenario_id  # Use current scenario ID
                        })
            
            ext_conn.close()
            
            if not experts_to_import:
                QMessageBox.warning(self, "Warning", "No valid experts to import.")
                return

            # Execute command
            db = self.main_window.get_db_manager()
            project_id = self.main_window.get_project_id()
            undo_manager = self.main_window.get_undo_manager()
            
            command = ImportExpertCommand(db, project_id, experts_to_import, comparisons_to_import, topsis_ratings_to_import)
            
            if undo_manager.execute(command):
                self.load_data()
                # IMPORTANT: Also refresh TOPSIS tab so imported experts appear there
                if hasattr(self.main_window, 'topsis_tab'):
                    self.main_window.topsis_tab.load_data()
                
                # Build success message
                msg = f"Imported {len(experts_to_import)} expert(s) with:\n"
                msg += f"• {len(comparisons_to_import)} AHP comparisons\n"
                
                # Show TOPSIS import stats
                if hasattr(command, 'topsis_import_count'):
                    msg += f"• {command.topsis_import_count} TOPSIS ratings imported\n"
                    if command.topsis_skip_count > 0:
                        msg += f"• {command.topsis_skip_count} TOPSIS ratings skipped (invalid data)\n"
                else:
                    msg += f"• {len(topsis_ratings_to_import)} TOPSIS ratings\n"
                
                msg += "Expert weights have been preserved."
                
                QMessageBox.information(self, "Import Successful", msg)
            else:
                QMessageBox.critical(self, "Error", "Failed to import experts.")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to import expert: {str(e)}")

    def show_inconsistency_analysis(self, metrics, criteria, weights=None):
        """Show analysis of inconsistency"""
        cr = metrics.get('cr', 0)
        matrix = metrics.get('matrix')
        
        msg = f"Consistency Ratio (CR) is {cr:.4f}, which is >= 0.1.\n"
        msg += "This indicates that the judgments are inconsistent.\n\n"
        
        if matrix is not None and weights is not None:
            # We have matrix and weights, run analysis
            criteria_names = [c['name'] for c in criteria]
            suggestion = FuzzyAHP.analyze_inconsistency(matrix, weights, criteria_names)
            msg += "Analysis:\n" + suggestion
        else:
            msg += "Please review your comparisons for the currently selected group."
            
        QMessageBox.warning(self, "Inconsistency Detected", msg)
    
    def display_weights(self, weights, cr, ci, lambda_max):
        """Display calculated weights"""
        self.weights_table.setRowCount(len(self.criteria))
        
        for i, criterion in enumerate(self.criteria):
            # Criterion name
            name_item = QTableWidgetItem(criterion['name'])
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.weights_table.setItem(i, 0, name_item)
            
            # Weight value - right aligned for better readability
            weight_item = QTableWidgetItem(f"{weights[i]:.4f}")
            weight_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            weight_item.setFlags(weight_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.weights_table.setItem(i, 1, weight_item)
        
        # Update CR label with detailed info
        self.lambda_label.setText(f"λmax: {lambda_max:.4f}")
        self.n_label.setText(f"n: {len(self.criteria)}")
        self.ci_label.setText(f"CI: {ci:.4f}")
        self.cr_label.setText(f"CR: {cr:.4f}")
        
        if cr < 0.1:
            self.cr_label.setStyleSheet("color: green; font-weight: bold;")
            self.inconsistency_text.setPlainText("✓ All comparisons are consistent (CR < 0.1)")
            self.inconsistency_text.setStyleSheet("background-color: #D4EDDA; border: 1px solid #28A745; padding: 5px; color: #155724;")
        else:
            self.cr_label.setStyleSheet("color: red; font-weight: bold;")
            # Analyze inconsistency
            criteria_names = [c['name'] for c in self.criteria]
            # Create simple matrix from middle values for analysis
            n = len(self.criteria)
            # We need to reconstruct the matrix - for now show a simple message
            suggestion = FuzzyAHP.analyze_inconsistency(
                np.eye(n),  # Placeholder - ideally we'd reconstruct the actual matrix
                weights,
                criteria_names
            )
            self.inconsistency_text.setPlainText(f"⚠ Inconsistency detected (CR = {cr:.4f})\n{suggestion}")
            self.inconsistency_text.setStyleSheet("background-color: #FFF3CD; border: 1px solid #FFC107; padding: 5px; color: #856404;")

    
    def display_hierarchical_weights(self, global_weights, consistency_info=None):
        """Display hierarchical weights with indentation"""
        # Clear existing table
        self.weights_table.setRowCount(0)
        
        # Build display with hierarchy
        def add_criterion_row(criterion, level=0):
            row = self.weights_table.rowCount()
            self.weights_table.insertRow(row)
            
            # Indent name based on level
            indent = "  " * level
            name = indent + criterion['name']
            
            weight = global_weights.get(criterion['id'], 0.0)
            percentage = weight * 100  # Convert to percentage
            
            # Create items
            name_item = QTableWidgetItem(name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            weight_item = QTableWidgetItem(f"{weight:.4f}")
            weight_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            weight_item.setFlags(weight_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            percentage_item = QTableWidgetItem(f"{percentage:.2f}%")
            percentage_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            percentage_item.setFlags(percentage_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            # Make parent criteria bold
            if criterion.get('parent_id') is None:
                font = name_item.font()
                font.setBold(True)
                name_item.setFont(font)
                weight_item.setFont(font)
                percentage_item.setFont(font)
            
            self.weights_table.setItem(row, 0, name_item)
            self.weights_table.setItem(row, 1, weight_item)
            self.weights_table.setItem(row, 2, percentage_item)
        
        # Display in hierarchical order
        main_criteria = [c for c in self.criteria if c.get('parent_id') is None]
        
        for main_criterion in main_criteria:
            add_criterion_row(main_criterion, 0)
            
            # Add sub-criteria
            sub_criteria = [c for c in self.criteria if c.get('parent_id') == main_criterion['id']]
            for sub_criterion in sub_criteria:
                add_criterion_row(sub_criterion, 1)
        
        # Update CR label
        if consistency_info:
            # Determine which group to show metrics for
            current_group_key = None
            
            # If user has selected a specific node, show its metrics
            if self.current_node:
                current_group_key = 'main' if self.current_node['type'] == 'root' else f"sub_{self.current_node['id']}"
            # Otherwise, default to showing 'main' metrics if available
            elif 'main' in consistency_info:
                current_group_key = 'main'
            
            if current_group_key and current_group_key in consistency_info:
                metrics = consistency_info[current_group_key]
                cr = metrics.get('cr', 0)
                ci = metrics.get('ci', 0)
                lm = metrics.get('lambda_max', 0)
                n = len(metrics.get('matrix')) if metrics.get('matrix') is not None else 0
                
                self.lambda_label.setText(f"λmax: {lm:.4f}")
                self.n_label.setText(f"n: {n}")
                self.ci_label.setText(f"CI: {ci:.4f}")
                self.cr_label.setText(f"CR: {cr:.4f}")
                
                if cr < 0.1:
                    self.cr_label.setStyleSheet("color: green; font-weight: bold;")
                    self.inconsistency_text.setPlainText("✓ Comparisons are consistent (CR < 0.1)")
                    self.inconsistency_text.setStyleSheet("background-color: #D4EDDA; border: 1px solid #28A745; padding: 5px; color: #155724;")
                else:
                    self.cr_label.setStyleSheet("color: red; font-weight: bold;")
                    self.inconsistency_text.setPlainText(f"⚠ Inconsistency detected (CR = {cr:.4f})")
                    self.inconsistency_text.setStyleSheet("background-color: #FFF3CD; border: 1px solid #FFC107; padding: 5px; color: #856404;")
                return

        self.lambda_label.setText("λmax: -")
        self.n_label.setText("n: -")
        self.ci_label.setText("CI: -")
        self.cr_label.setText("CR: Not calculated")
        self.cr_label.setStyleSheet("color: black; font-weight: bold;")
        self.inconsistency_text.setPlainText("No consistency data available.")
        self.inconsistency_text.setStyleSheet("background-color: #F8F9FA; border: 1px solid #DEE2E6; padding: 5px; color: #6C757D;")

    def auto_save_comparisons_for_expert(self, expert_id):
        """Automatically save comparisons for a specific expert without showing messages"""
        if not self.current_children:
            return
        
        project_id = self.main_window.get_project_id()
        db = self.main_window.get_db_manager()
        undo_manager = self.main_window.get_undo_manager()
        
        comparisons_to_save = []
        
        try:
            # Iterate through table rows
            n = len(self.current_children)
            row = 0
            for i in range(n):
                for j in range(i + 1, n):
                    c1_id = self.current_children[i]['id']
                    c2_id = self.current_children[j]['id']
                    
                    # Get scale value from combo
                    scale_combo = self.comparison_table.cellWidget(row, 2)
                    if scale_combo:
                        scale_val = scale_combo.currentData()
                        
                        # Get fuzzy numbers
                        l, m, u = FuzzyAHP.get_fuzzy_number(scale_val)
                        
                        comparisons_to_save.append({
                            'c1_id': c1_id,
                            'c2_id': c2_id,
                            'l': l, 'm': m, 'u': u
                        })
                    
                    row += 1
            
            if comparisons_to_save:
                command = BatchSaveComparisonsCommand(db, project_id, expert_id, comparisons_to_save)
                undo_manager.execute(command)  # Save silently, no message
                
        except Exception:
            pass  # Silent fail for auto-save
    
    def save_comparisons(self):
        """Save comparisons to database"""
        if not self.current_children:
            return
            
        if self.expert_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Warning", "Please select an expert first.")
            return
            
        expert_id = self.expert_combo.currentData()
        project_id = self.main_window.get_project_id()
        db = self.main_window.get_db_manager()
        undo_manager = self.main_window.get_undo_manager()
        
        comparisons_to_save = []
        
        try:
            # Iterate through table rows
            n = len(self.current_children)
            row = 0
            for i in range(n):
                for j in range(i + 1, n):
                    c1_id = self.current_children[i]['id']
                    c2_id = self.current_children[j]['id']
                    
                    # Get scale value from combo
                    scale_combo = self.comparison_table.cellWidget(row, 2)
                    if scale_combo:
                        scale_val = scale_combo.currentData()
                        
                        # Get fuzzy numbers
                        l, m, u = FuzzyAHP.get_fuzzy_number(scale_val)
                        
                        comparisons_to_save.append({
                            'c1_id': c1_id,
                            'c2_id': c2_id,
                            'l': l, 'm': m, 'u': u
                        })
                    
                    row += 1
            
            if comparisons_to_save:
                command = BatchSaveComparisonsCommand(db, project_id, expert_id, comparisons_to_save)
                if undo_manager.execute(command):
                    QMessageBox.information(self, "Success", "Comparisons saved successfully!")
                else:
                    QMessageBox.critical(self, "Error", "Failed to save comparisons.")
            else:
                QMessageBox.information(self, "Info", "No comparisons to save.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save comparisons: {str(e)}")


    def calculate_weights(self):
        """Calculate weights based on all comparisons with expert weighting"""
        project_id = self.main_window.get_project_id()
        db = self.main_window.get_db_manager()
        
        try:
            with db as database:
                # Get all comparisons
                comparisons = database.get_ahp_comparisons(
                    project_id,
                    scenario_id=self.main_window.current_scenario_id  # NEW
                )
                
                if not comparisons:
                    QMessageBox.warning(self, "Warning", "No comparisons found. Please add comparisons first.")
                    return
                
                # Get expert weights
                expert_weights_dict = database.get_expert_weights(project_id)
                
                # Organize comparisons by group (returns dict with expert_ids per group)
                comparisons_by_group_with_experts = self._organize_comparisons_with_experts(
                    comparisons, self.criteria
                )
                
                # Prepare comparisons_by_group format for hierarchical calc
                comparisons_by_group = {}
                expert_weights_by_group = {}
                
                for group_key, (matrices, expert_ids) in comparisons_by_group_with_experts.items():
                    comparisons_by_group[group_key] = matrices
                    # Map expert weights for this group
                    expert_weights_by_group[group_key] = [
                        expert_weights_dict.get(eid, 1.0/len(expert_ids)) 
                        for eid in expert_ids
                    ]
                
                # Calculate global weights with expert weighting
                global_weights, consistency_info = self._calculate_hierarchical_weights_weighted(
                    self.criteria, comparisons_by_group, expert_weights_by_group
                )
                
                # Save weights to database
                for criterion_id, weight in global_weights.items():
                    database.update_criterion_weight(criterion_id, weight)
                
                # Display results
                self.display_hierarchical_weights(global_weights, consistency_info)
                
                QMessageBox.information(self, "Success", "Weights calculated and saved!")
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to calculate weights: {str(e)}")
    
    def _organize_comparisons_with_experts(self, all_comparisons, criteria_hierarchy):
        """Organize comparisons by group, tracking expert IDs"""
        from algorithms.fuzzy_ahp import FuzzyAHP
        
        criteria_map = {c['id']: c for c in criteria_hierarchy}
        comparisons_by_expert_and_group = {}
        
        for comp in all_comparisons:
            expert_id = comp['expert_id']
            c1_id = comp['criterion1_id']
            c2_id = comp['criterion2_id']
            
            if c1_id in criteria_map and c2_id in criteria_map:
                c1_parent = criteria_map[c1_id].get('parent_id')
                c2_parent = criteria_map[c2_id].get('parent_id')
                
                if c1_parent == c2_parent:
                    group_key = 'main' if c1_parent is None else f'sub_{c1_parent}'
                    key = (expert_id, group_key)
                    if key not in comparisons_by_expert_and_group:
                        comparisons_by_expert_and_group[key] = []
                    comparisons_by_expert_and_group[key].append(comp)
        
        result = {}
        groups = set(group_key for (_, group_key) in comparisons_by_expert_and_group.keys())
        
        for group_key in groups:
            experts_in_group = sorted(set(
                expert_id for (expert_id, gk) in comparisons_by_expert_and_group.keys()
                if gk == group_key
            ))
            
            matrices = []
            for expert_id in experts_in_group:
                key = (expert_id, group_key)
                if key in comparisons_by_expert_and_group:
                    comps = comparisons_by_expert_and_group[key]
                    
                    if group_key == 'main':
                        n_criteria = len([c for c in criteria_hierarchy if c['parent_id'] is None])
                        criteria_ids = [c['id'] for c in criteria_hierarchy if c['parent_id'] is None]
                    else:
                        parent_id = int(group_key.split('_')[1])
                        n_criteria = len([c for c in criteria_hierarchy if c['parent_id'] == parent_id])
                        criteria_ids = [c['id'] for c in criteria_hierarchy if c['parent_id'] == parent_id]
                    
                    matrix = FuzzyAHP.create_fuzzy_matrix_from_comparisons(
                        n_criteria, comps, criteria_ids
                    )
                    matrices.append(matrix)
            
            if matrices:
                result[group_key] = (matrices, experts_in_group)
        
        return result
    
    def _calculate_hierarchical_weights_weighted(self, criteria_hierarchy, comparisons_by_group, expert_weights_by_group):
        """Calculate hierarchical weights using expert weights"""
        from algorithms.hierarchical_ahp import HierarchicalFuzzyAHP
        
        global_weights = {}
        consistency_info = {}
        
        main_criteria = [c for c in criteria_hierarchy if c['parent_id'] is None]
        
        if 'main' in comparisons_by_group and comparisons_by_group['main']:
            main_weights, metrics = HierarchicalFuzzyAHP._calculate_group_weights(
                comparisons_by_group['main'],
                len(main_criteria),
                expert_weights_by_group.get('main')
            )
            consistency_info['main'] = metrics
            
            for i, criterion in enumerate(main_criteria):
                global_weights[criterion['id']] = main_weights[i]
        else:
            equal_weight = 1.0 / len(main_criteria) if main_criteria else 0
            for criterion in main_criteria:
                global_weights[criterion['id']] = equal_weight
        
        for main_criterion in main_criteria:
            main_id = main_criterion['id']
            main_weight = global_weights.get(main_id, 0)
            
            sub_criteria = [c for c in criteria_hierarchy if c['parent_id'] == main_id]
            
            if not sub_criteria:
                continue
            
            group_key = f'sub_{main_id}'
            
            if group_key in comparisons_by_group and comparisons_by_group[group_key]:
                sub_weights, metrics = HierarchicalFuzzyAHP._calculate_group_weights(
                    comparisons_by_group[group_key],
                    len(sub_criteria),
                    expert_weights_by_group.get(group_key)
                )
                consistency_info[group_key] = metrics
                
                for i, sub_criterion in enumerate(sub_criteria):
                    global_weights[sub_criterion['id']] = sub_weights[i] * main_weight
            else:
                equal_weight = main_weight / len(sub_criteria)
                for sub_criterion in sub_criteria:
                    global_weights[sub_criterion['id']] = equal_weight
        
        # Normalize leaf criteria
        leaf_criteria_ids = [c['id'] for c in criteria_hierarchy 
                            if c['id'] not in set(c2.get('parent_id') for c2 in criteria_hierarchy if c2.get('parent_id'))]
        leaf_weights_sum = sum(global_weights.get(cid, 0) for cid in leaf_criteria_ids)
        
        if leaf_weights_sum > 0:
            for cid in leaf_criteria_ids:
                if cid in global_weights:
                    global_weights[cid] = global_weights[cid] / leaf_weights_sum
        
        return global_weights, consistency_info


