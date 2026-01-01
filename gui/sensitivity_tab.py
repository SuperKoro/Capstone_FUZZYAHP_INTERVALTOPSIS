"""
Sensitivity Analysis Tab Module
Implements What-If analysis for weight perturbation
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QGroupBox, QComboBox, QLabel, QPushButton, 
                             QTextEdit, QMessageBox, QApplication)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np

from algorithms.sensitivity_analysis import SensitivityAnalysis
from algorithms.interval_topsis import IntervalTOPSIS


class SensitivityAnalysisTab(QWidget):
    """
    Sensitivity Analysis Tab for What-If Weight Perturbation
    
    Features:
    - Weight perturbation analysis with visualization
    - Rank reversal detection
    - Stability metrics
    - Excel export
    """
    
    # Global color map for consistent supplier colors across app
    SUPPLIER_COLORS = [
        '#1f77b4',  # Blue
        '#ff7f0e',  # Orange
        '#2ca02c',  # Green
        '#d62728',  # Red
        '#9467bd',  # Purple
        '#8c564b',  # Brown
        '#e377c2',  # Pink
        '#7f7f7f',  # Gray
        '#bcbd22',  # Olive
        '#17becf',  # Cyan
    ]
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.current_results = None
        self.criteria = []  # ALL criteria (parents + leaves)
        self.leaf_criteria = []  # Leaf criteria only (for TOPSIS matrix)
        self.criteria_tree = {}  # Hierarchy tree with local weights
        self.alternatives = []
        self.experts = []
        self.data_loaded = False  # Track if data has been loaded
        self.init_ui()
    
    def showEvent(self, event):
        """Called when tab becomes visible - auto-load data if needed"""
        super().showEvent(event)
        if not self.data_loaded and self.main_window.get_db_manager():
            self.load_data()
            self.data_loaded = True
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Control panel
        layout.addWidget(self.create_control_panel())
        
        # Chart with toolbar
        layout.addWidget(self.create_chart_panel())
        
        # Summary
        layout.addWidget(self.create_summary_panel())
        
        self.setLayout(layout)
    
    def create_control_panel(self):
        """Create analysis parameter controls"""
        group = QGroupBox("Analysis Parameters")
        grid = QGridLayout()
        
        # Criterion selector
        grid.addWidget(QLabel("Select Criterion:"), 0, 0)
        self.criterion_combo = QComboBox()
        self.criterion_combo.setMinimumWidth(200)
        grid.addWidget(self.criterion_combo, 0, 1)
        
        # Range selector
        grid.addWidget(QLabel("Perturbation Range:"), 0, 2)
        self.range_combo = QComboBox()
        self.range_combo.addItems(["±10%", "±20%", "±30%", "±50%"])
        self.range_combo.setCurrentText("±20%")
        grid.addWidget(self.range_combo, 0, 3)
        
        # Top N filter
        grid.addWidget(QLabel("Show Top:"), 1, 0)
        self.topn_combo = QComboBox()
        self.topn_combo.addItems(["All", "Top 3", "Top 5", "Top 10"])
        grid.addWidget(self.topn_combo, 1, 1)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.run_button = QPushButton("Run Analysis")
        self.run_button.clicked.connect(self.run_analysis)
        self.run_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        button_layout.addWidget(self.run_button)
        
        self.export_button = QPushButton("Export to Excel")
        self.export_button.clicked.connect(self.export_results)
        self.export_button.setEnabled(False)
        button_layout.addWidget(self.export_button)
        
        # Add reload data button for debugging
        self.reload_button = QPushButton("🔄 Reload Data")
        self.reload_button.setToolTip("Reload criteria and alternatives from database")
        self.reload_button.clicked.connect(self.manual_reload_data)
        button_layout.addWidget(self.reload_button)
        
        button_layout.addStretch()
        
        grid.addLayout(button_layout, 2, 0, 1, 4)
        
        group.setLayout(grid)
        return group
    
    def create_chart_panel(self):
        """Create matplotlib chart with navigation toolbar"""
        group = QGroupBox("Sensitivity Chart")
        layout = QVBoxLayout()
        
        # Matplotlib figure and canvas
        self.figure = Figure(figsize=(10, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.axes = self.figure.add_subplot(111)
        
        # Navigation toolbar for zoom/pan
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        
        # Initial empty chart
        self.axes.text(0.5, 0.5, 'Select criterion and click "Run Analysis"',
                      ha='center', va='center', fontsize=12, color='gray')
        self.axes.set_xlim(-25, 25)
        self.axes.set_ylim(0, 1)
        self.axes.grid(True, linestyle='--', alpha=0.3)
        self.canvas.draw()
        
        group.setLayout(layout)
        return group
    
    def create_summary_panel(self):
        """Create analysis summary display"""
        group = QGroupBox("Analysis Summary")
        layout = QVBoxLayout()
        
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMaximumHeight(150)
        self.summary_text.setHtml(
            "<p style='color: gray; font-style: italic;'>"
            "Run analysis to see sensitivity metrics and rank reversal warnings."
            "</p>"
        )
        
        layout.addWidget(self.summary_text)
        group.setLayout(layout)
        return group
    
    def manual_reload_data(self):
        """Manually reload data - triggered by Reload button"""
        self.data_loaded = False  # Reset flag
        self.load_data()
        self.data_loaded = True
        QMessageBox.information(
            self,
            "Data Reloaded",
            f"Loaded {len(self.criteria)} criteria and {len(self.alternatives)} alternatives"
        )
    
    def load_data(self):
        """Load criteria and alternatives for current scenario"""
        db = self.main_window.get_db_manager()
        if not db:
            return
        
        with db as database:
            # Load ALL criteria (both parents and leaves) for sensitivity dropdown
            all_criteria = database.get_criteria(self.main_window.get_project_id())
            
            if all_criteria:
                criteria_ids = {c['id'] for c in all_criteria}
                parent_ids = {c['parent_id'] for c in all_criteria if c.get('parent_id')}
                leaf_ids = criteria_ids - parent_ids
                
                # Store ALL criteria for dropdown selection
                self.criteria = all_criteria
                
                # Store LEAF criteria separately for TOPSIS matrix
                self.leaf_criteria = [c for c in all_criteria if c['id'] in leaf_ids]
                
                # Build hierarchy tree and calculate local weights
                self.criteria_tree = self._build_criteria_tree(all_criteria, parent_ids)
            else:
                self.criteria = []
                self.leaf_criteria = []
                self.criteria_tree = {}
            
            self.alternatives = database.get_alternatives(self.main_window.get_project_id())
            self.experts = database.get_experts(self.main_window.get_project_id())
        
        # Update UI - preserve current selection if possible
        current_criterion_id = self.criterion_combo.currentData()  # Save current selection
        
        self.criterion_combo.clear()
        for c in self.criteria:
            # Add visual distinction for parent vs leaf
            if self._is_parent(c['id']):
                display_name = f"📁 {c['name']} (Parent)"
            else:
                display_name = f"📄 {c['name']}"
            self.criterion_combo.addItem(display_name, c['id'])
        
        # Restore previous selection if criterion still exists
        if current_criterion_id:
            index = self.criterion_combo.findData(current_criterion_id)
            if index >= 0:
                self.criterion_combo.setCurrentIndex(index)
        
        # Reset state
        self.current_results = None
        self.export_button.setEnabled(False)
    
    def _build_criteria_tree(self, all_criteria, parent_ids):
        """
        Build hierarchy tree with local weights for sensitivity analysis
        
        Returns:
            Dict mapping criterion_id to {
                'criterion': criterion_dict,
                'is_parent': bool,
                'children': [child_dicts],
                'local_weight': float (for children only)
            }
        """
        tree = {}
        
        for criterion in all_criteria:
            cid = criterion['id']
            tree[cid] = {
                'criterion': criterion,
                'is_parent': cid in parent_ids,
                'children': [],
                'local_weight': None
            }
        
        # Build parent-child relationships and calculate local weights
        for criterion in all_criteria:
            criterion_id = criterion['id']  # Use explicit variable name
            parent_id = criterion.get('parent_id')
            if parent_id and parent_id in tree:
                # This is a child
                tree[parent_id]['children'].append(criterion)
                
                # Calculate local weight (child_global / parent_global)
                parent_weight = tree[parent_id]['criterion'].get('weight', 0) or 0
                child_weight = criterion.get('weight', 0) or 0
                
                if parent_weight > 0:
                    local_weight = child_weight / parent_weight
                else:
                    local_weight = 0
                
                tree[criterion_id]['local_weight'] = local_weight  # FIX: use criterion_id, not cid
        
        return tree
    
    def _is_parent(self, criterion_id):
        """Check if a criterion has children (is a parent)"""
        return self.criteria_tree.get(criterion_id, {}).get('is_parent', False)
    
    def _get_children(self, criterion_id):
        """Get all child criteria for a parent"""
        return self.criteria_tree.get(criterion_id, {}).get('children', [])
    
    def _recalculate_global_weights(self, perturbed_criterion_id, new_weight, all_weights_dict):
        """
        Recalculate global weights after perturbing a criterion
        
        Args:
            perturbed_criterion_id: ID of the perturbed criterion
            new_weight: New weight value
            all_weights_dict: Current weights {criterion_id: weight}
            
        Returns:
            np.array of weights for LEAF criteria only (for TOPSIS)
        """
        # Update the perturbed criterion
        updated_weights = all_weights_dict.copy()
        updated_weights[perturbed_criterion_id] = new_weight
        
        # If it's a parent, propagate to children
        if self._is_parent(perturbed_criterion_id):
            children = self._get_children(perturbed_criterion_id)
            for child in children:
                child_id = child['id']
                local_weight = self.criteria_tree[child_id]['local_weight'] or 0
                # Global weight = parent_weight × local_weight
                updated_weights[child_id] = new_weight * local_weight
                
                # If child is also a parent, recursively propagate
                if self._is_parent(child_id):
                    self._propagate_to_descendants(child_id, updated_weights[child_id], updated_weights)
        
        # Extract leaf weights only in the correct order
        leaf_weights = []
        for leaf in self.leaf_criteria:
            leaf_weights.append(updated_weights.get(leaf['id'], 0))
        
        return np.array(leaf_weights)
    
    def _propagate_to_descendants(self, parent_id, parent_weight, updated_weights):
        """Recursively propagate weight changes to all descendants"""
        children = self._get_children(parent_id)
        for child in children:
            child_id = child['id']
            local_weight = self.criteria_tree[child_id]['local_weight'] or 0
            updated_weights[child_id] = parent_weight * local_weight
            
            # Recurse if this child is also a parent
            if self._is_parent(child_id):
                self._propagate_to_descendants(child_id, updated_weights[child_id], updated_weights)
    
    def _run_parent_perturbation(self, criterion_id, criterion_name, base_weights_dict,
                                 decision_matrix, is_benefit, perturbation_range, n_steps, top_n):
        """
        Run sensitivity analysis for PARENT criterion with weight propagation
        
        Args:
            criterion_id: ID of parent criterion to perturb
            criterion_name: Name of criterion for results
            base_weights_dict: Dict of {criterion_id: weight} for all criteria
            decision_matrix: TOPSIS decision matrix (alternatives × leaf_criteria × 2)
            is_benefit: Boolean array for leaf criteria
            perturbation_range: ±% range
            n_steps: Number of perturbation steps
            top_n: Top N alternatives to show (None = all)
            
        Returns:
            Results dict compatible with SensitivityAnalysis format
        """
        # Generate perturbation percentages
        perturbations = np.linspace(-perturbation_range * 100, perturbation_range * 100, n_steps)
        
        # Get base parent weight
        base_parent_weight = base_weights_dict[criterion_id]
        
        # Storage for results
        n_alternatives = len(self.alternatives)
        CC_matrix = np.zeros((n_alternatives, n_steps))
        rankings_list = []
        weights_at_steps = []
        
        # Identify all parent criteria for normalization
        parent_criteria = [c for c in self.criteria if self._is_parent(c['id'])]
        parent_ids = [p['id'] for p in parent_criteria]
        parent_base_weights = np.array([base_weights_dict[pid] for pid in parent_ids])
        
        # DEBUG: Print parent structure
        
        # Find index of our target parent in the parent list
        target_parent_idx = parent_ids.index(criterion_id)
        
        # Run TOPSIS at each perturbation step
        for step_idx, pert_pct in enumerate(perturbations):
            # Calculate delta for the target parent
            delta = base_parent_weight * (pert_pct / 100.0)
            
            # Normalize ALL parent weights (this redistributes weight among parents)
            normalized_parent_weights = SensitivityAnalysis.normalize_weights_after_perturbation(
                parent_base_weights, target_parent_idx, delta
            )
            
            # DEBUG: Print first step details
            if step_idx == 0:
                pass  # Debug logging removed
            
            # Create updated weights dict with normalized parent weights
            updated_weights_dict = base_weights_dict.copy()
            for i, pid in enumerate(parent_ids):
                updated_weights_dict[pid] = normalized_parent_weights[i]
            
            # Now propagate parent weights to their children
            for i, pid in enumerate(parent_ids):
                parent_new_weight = normalized_parent_weights[i]
                children = self._get_children(pid)
                
                for child in children:
                    child_id = child['id']
                    local_weight = self.criteria_tree[child_id]['local_weight'] or 0
                    # Child global weight = parent_weight × local_weight
                    updated_weights_dict[child_id] = parent_new_weight * local_weight
                    
                    # Recursively propagate if child is also a parent
                    if self._is_parent(child_id):
                        self._propagate_to_descendants(child_id, updated_weights_dict[child_id], updated_weights_dict)
            
            # Extract leaf weights in correct order
            leaf_weights = np.array([updated_weights_dict.get(lc['id'], 0) for lc in self.leaf_criteria])
            
            # DEBUG: Print first step leaf weights
            if step_idx == 0:
                pass  # Debug logging removed
            
            # Leaf weights should already sum to 1.0 after parent normalization + propagation
            # Only normalize if there's significant deviation (floating point errors)
            weight_sum = leaf_weights.sum()
            if abs(weight_sum - 1.0) > 0.01:  # More than 1% deviation = error
                if weight_sum > 0:
                    leaf_weights = leaf_weights / weight_sum
            
            weights_at_steps.append(normalized_parent_weights[target_parent_idx])
            
            # Run TOPSIS with updated leaf weights
            CC, _ = IntervalTOPSIS.rank_alternatives(
                decision_matrix,
                leaf_weights,
                is_benefit
            )
            
            CC_matrix[:, step_idx] = CC
            
            # Get ranking (sorted indices, best first)
            ranking = np.argsort(-CC).tolist()
            rankings_list.append(ranking)
        
        # Detect rank reversals
        base_idx = n_steps // 2  # Middle point (0% perturbation)
        base_ranking = rankings_list[base_idx]
        
        rank_reversal_points = []
        for i, ranking in enumerate(rankings_list):
            if ranking != base_ranking and i != base_idx:
                changes = SensitivityAnalysis._detect_ranking_changes(
                    base_ranking, ranking, [a['name'] for a in self.alternatives]
                )
                if changes:
                    rank_reversal_points.append({
                        'perturbation_pct': perturbations[i],
                        'changes': changes
                    })
        
        # Determine critical perturbation (first reversal)
        critical_pert = rank_reversal_points[0]['perturbation_pct'] if rank_reversal_points else None
        
        # Filter by top N if requested
        analyzed_alts = list(range(n_alternatives))
        if top_n and top_n < n_alternatives:
            # Get top N from base ranking
            analyzed_alts = base_ranking[:top_n]
        
        # Build results dict (compatible with SensitivityAnalysis format)
        results = {
            criterion_name: {
                'perturbations': perturbations,
                'closeness_coefficients': CC_matrix,
                'rankings': rankings_list,
                'weights_at_perturbations': weights_at_steps,
                'rank_reversal_points': rank_reversal_points,
                'critical_perturbation': critical_pert,
                'analyzed_alternatives': analyzed_alts
            },
            'stability_index': 1.0 - (len(rank_reversal_points) / n_steps)  # Simple stability metric
        }
        
        return results

    def build_decision_matrix(self):
        """Build decision matrix from TOPSIS ratings"""
        db = self.main_window.get_db_manager()
        if not db:
            return None
        
        try:
            n_alternatives = len(self.alternatives)
            n_criteria = len(self.leaf_criteria)  # Use LEAF criteria only for matrix
            
            # Aggregate expert ratings (same as TOPSIS tab)
            expert_matrices = []
            
            with db as database:
                for expert in self.experts:
                    ratings = database.get_topsis_ratings(
                        self.main_window.get_project_id(),
                        expert['id'],
                        scenario_id=self.main_window.current_scenario_id
                    )
                    
                    matrix = np.zeros((n_alternatives, n_criteria, 2))
                    
                    # Fill matrix from ratings
                    rating_map = {
                        (r['alternative_id'], r['criterion_id']): 
                        (r['rating_lower'], r['rating_upper']) 
                        for r in ratings
                    }
                    
                    for i, alt in enumerate(self.alternatives):
                        for j, crit in enumerate(self.leaf_criteria):  # Iterate LEAF criteria only
                            if (alt['id'], crit['id']) in rating_map:
                                matrix[i, j] = rating_map[(alt['id'], crit['id'])]
                            else:
                                # Default to Fair [4, 5] if missing
                                matrix[i, j] = [4, 5]
                    
                    expert_matrices.append(matrix)
            
            if not expert_matrices:
                QMessageBox.warning(
                    self, "No Ratings", 
                    "Please enter TOPSIS ratings first in the TOPSIS Rating tab!"
                )
                return None
            
            # Aggregate using arithmetic mean
            return IntervalTOPSIS.aggregate_expert_ratings(expert_matrices)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to build matrix: {e}")
            return None
    
    def run_analysis(self):
        """Execute sensitivity analysis"""
        # IMPORTANT: Always refresh data before analysis to ensure we have latest alternatives/criteria
        self.load_data()
        
        if not self.criteria or not self.alternatives:
            QMessageBox.warning(
                self, "No Data", 
                "Please load project data first! Ensure you have:\n"
                "- Calculated AHP weights\n"
                "- Entered TOPSIS ratings"
            )
            return
        
        # Get parameters
        criterion_idx = self.criterion_combo.currentIndex()
        if criterion_idx < 0:
            QMessageBox.warning(self, "No Criterion", "Please select a criterion!")
            return
        
        # Check if weights are calculated
        if all(c.get('weight', 0) == 0 for c in self.criteria):
            QMessageBox.warning(
                self, "No Weights",
                "Please calculate AHP weights first in the AHP Evaluation tab!"
            )
            return
        
        range_text = self.range_combo.currentText()
        perturbation_range = float(range_text.strip('±%')) / 100.0
        
        # Hard-coded: 51 steps for smooth curves
        n_steps = 51
        
        topn_text = self.topn_combo.currentText()
        top_n = None if topn_text == "All" else int(topn_text.split()[1])
        
        # Build decision matrix
        decision_matrix = self.build_decision_matrix()
        if decision_matrix is None:
            return
        
        # Get selected criterion
        selected_criterion = self.criteria[criterion_idx]
        criterion_id = selected_criterion['id']
        criterion_name = selected_criterion['name']
        
        # Determine if it's a parent or leaf criterion
        is_parent_criterion = self._is_parent(criterion_id)
        
        if is_parent_criterion:
            # PARENT PERTURBATION: Need to propagate to children
            # Get base weights for all criteria as dict
            base_weights_dict = {c['id']: c['weight'] for c in self.criteria}
            
            # Count parent criteria
            parent_criteria_list = [c for c in self.criteria if self._is_parent(c['id'])]
            n_parents = len(parent_criteria_list)
            
            # Check if parent has zero weight
            parent_weight = selected_criterion.get('weight', 0) or 0
            if parent_weight == 0:
                QMessageBox.warning(
                    self, "Zero Weight",
                    f"Cannot analyze '{criterion_name}' - it has zero weight!\n\n"
                    f"This parent criterion and its children have not been assigned "
                    f"importance in the AHP evaluation.\n\n"
                    f"Please:\n"
                    f"1. Go to 'Fuzzy AHP Evaluation' tab\n"
                    f"2. Complete pairwise comparisons for all criteria groups\n"
                    f"3. Click 'Calculate Weights'\n\n"
                    f"Then return here to run sensitivity analysis."
                )
                return
            
            # Check if this is the ONLY parent (edge case)
            if n_parents == 1:
                QMessageBox.warning(
                    self, "Single Parent Limitation",
                    f"'{criterion_name}' is the ONLY parent criterion in your hierarchy.\n\n"
                    f"⚠️ Parent perturbation requires multiple parents to redistribute weights.\n\n"
                    f"Recommendation:\n"
                    f"• Analyze child criteria instead (they show meaningful sensitivity)\n"
                    f"• Or add more parent criteria groups to your hierarchy\n\n"
                    f"With only one parent at 100% weight, perturbation has no effect."
                )
                return
            
            # For parent perturbation, we perturb the parent and propagate to children
            # Then use only leaf weights for TOPSIS
            leaf_base_weights = np.array([c['weight'] for c in self.leaf_criteria])
            is_benefit = np.array([c['is_benefit'] for c in self.leaf_criteria])
            
            # Validation: Ensure leaf criteria count matches decision matrix columns
            assert len(is_benefit) == decision_matrix.shape[1], \
                f"Mismatch: {len(is_benefit)} leaf criteria but {decision_matrix.shape[1]} matrix columns!"
        else:
            # LEAF PERTURBATION: Direct weight change
            leaf_base_weights = np.array([c['weight'] for c in self.leaf_criteria])
            is_benefit = np.array([c['is_benefit'] for c in self.leaf_criteria])
        
        # NEW: Warning for low-weight criteria (likely to show flat curves)
        criterion_weight = selected_criterion.get('weight', 0) or 0
        if criterion_weight == 0:
            QMessageBox.warning(
                self, "Zero Weight",
                f"Cannot analyze '{criterion_name}' - it has zero weight!\\n\\n"
                f"Please complete AHP evaluation first."
            )
            return
        elif criterion_weight < 0.05:  # Less than 5%
            reply = QMessageBox.warning(
                self, "⚠️ Low Weight Criterion Detected",
                f"<b>'{criterion_name}'</b> has a very low weight: <b>{criterion_weight*100:.2f}%</b><br><br>"
                
                f"<b style='color: #e67e22;'>⚠️ Why This Matters:</b><br>"
                f"Sensitivity analysis may show minimal variation (flat curves) because:<br>"
                f"• This criterion has little impact on overall rankings<br>"
                f"• A ±20% perturbation creates only ±<b>{criterion_weight*0.2*100:.3f}%</b> absolute change<br><br>"
                
                f"<b style='color: #27ae60;'>✓ This is EXPECTED behavior</b><br>"
                f"It shows your decision is <u>robust</u> to changes in this less important criterion!<br><br>"
                
                f"<b style='color: #3498db;'>💡 Recommendations:</b><br>"
                f"• Try a wider perturbation range (±50%) for more visible effects<br>"
                f"• Analyze more important criteria (weight {'>'} 5%) instead<br>"
                f"• Review AHP weights if this criterion should be more important<br><br>"
                
                f"<b>Continue with analysis anyway?</b>",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
            
        # Show loading cursor
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.run_button.setEnabled(False)
        self.run_button.setText("Analyzing...")
        
        try:
            if is_parent_criterion:
                # Parent perturbation - use custom method
                results = self._run_parent_perturbation(
                    criterion_id=criterion_id,
                    criterion_name=criterion_name,
                    base_weights_dict=base_weights_dict,
                    decision_matrix=decision_matrix,
                    is_benefit=is_benefit,
                    perturbation_range=perturbation_range,
                    n_steps=n_steps,
                    top_n=top_n
                )
            else:
                # Leaf perturbation - use standard analysis
                # Find index of this leaf in leaf_criteria (with defensive error handling)
                try:
                    leaf_idx = next(i for i, lc in enumerate(self.leaf_criteria) if lc['id'] == criterion_id)
                except StopIteration:
                    QMessageBox.critical(
                        self, "Data Error",
                        f"Criterion '{criterion_name}' not found in leaf criteria!\n\n"
                        f"This may indicate a data inconsistency. Please reload the project."
                    )
                    return
                
                results = SensitivityAnalysis.weight_perturbation_analysis(
                    decision_matrix=decision_matrix,
                    base_weights=leaf_base_weights,
                    is_benefit=is_benefit,
                    criterion_names=[c['name'] for c in self.leaf_criteria],
                    alternative_names=[a['name'] for a in self.alternatives],
                    perturbation_range=perturbation_range,
                    n_steps=n_steps,
                    top_n_alternatives=top_n
                )
            
            self.current_results = results
            
            # Update visualization
            # criterion_name already set above
            self.update_chart(results, criterion_name)
            self.update_summary(results, criterion_name)
            
            self.export_button.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Analysis Error", f"Error during analysis:\n{str(e)}")
            import traceback
            traceback.print_exc()
        
        finally:
            QApplication.restoreOverrideCursor()
            self.run_button.setEnabled(True)
            self.run_button.setText("Run Analysis")
    
    def get_supplier_color(self, alt_idx):
        """Get consistent color for supplier across all charts"""
        return self.SUPPLIER_COLORS[alt_idx % len(self.SUPPLIER_COLORS)]
    
    def update_chart(self, results, criterion_name):
        """Update matplotlib chart with sensitivity data"""
        self.axes.clear()
        
        crit_data = results[criterion_name]
        perturbations = crit_data['perturbations']
        CC_matrix = crit_data['closeness_coefficients']
        analyzed_alts = crit_data.get('analyzed_alternatives', range(len(self.alternatives)))
        
        # Get criterion weight for display
        criterion_weight = next((c['weight'] for c in self.criteria if c['name'] == criterion_name), 0)
        
        # Plot lines for each alternative with consistent colors
        for alt_idx in analyzed_alts:
            alt_name = self.alternatives[alt_idx]['name']
            CC_values = CC_matrix[alt_idx, :]
            color = self.get_supplier_color(alt_idx)
            
            self.axes.plot(perturbations, CC_values, 
                          label=alt_name, 
                          marker='o', 
                          markersize=3,
                          color=color,
                          linewidth=2)
        
        # Highlight rank reversals with vertical lines
        if crit_data['rank_reversal_points']:
            for reversal in crit_data['rank_reversal_points']:
                pct = reversal['perturbation_pct']
                self.axes.axvline(x=pct, color='red', linestyle='--', 
                                alpha=0.6, linewidth=1.5, label='_nolegend_')
            
            # Add annotation for first critical point
            first_reversal = crit_data['rank_reversal_points'][0]['perturbation_pct']
            self.axes.annotate(
                f'Critical Point: {first_reversal:.1f}%',
                xy=(first_reversal, 0.5),
                xytext=(first_reversal + 5, 0.5),
                fontsize=9,
                color='red',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
                arrowprops=dict(arrowstyle='->', color='red', lw=1.5)
            )
        
        # Styling
        self.axes.set_title(
            f"Sensitivity Analysis: {criterion_name}\n"
            f"(Current Weight: {criterion_weight*100:.2f}%)",
            fontsize=13,
            fontweight='bold',
            pad=15
        )
        self.axes.set_xlabel("Weight Change (%)", fontsize=11, fontweight='bold')
        self.axes.set_ylabel("Closeness Coefficient", fontsize=11, fontweight='bold')
        self.axes.grid(True, linestyle='--', alpha=0.4)
        self.axes.legend(loc='best', fontsize=9, framealpha=0.9)
        
        # Baseline at 0%
        self.axes.axvline(x=0, color='black', linewidth=2, linestyle='-', alpha=0.7)
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def update_summary(self, results, criterion_name):
        """Display analysis summary with HTML formatting"""
        crit_data = results[criterion_name]
        
        summary = []
        summary.append(f"<h3 style='color: #2c3e50;'>Analysis for: {criterion_name}</h3>")
        
        # Rank reversals
        if crit_data['rank_reversal_points']:
            summary.append("<p style='color: #e74c3c; font-weight: bold; font-size: 14px;'>⚠ Rank Reversal Detected!</p>")
            summary.append(f"<p><b>Critical Perturbation:</b> <span style='color: #e74c3c; font-size: 14px;'>{crit_data['critical_perturbation']:.1f}%</span></p>")
            
            summary.append("<p><b>Changes:</b></p><ul>")
            for reversal in crit_data['rank_reversal_points'][:3]:  # First 3
                summary.append(f"<li>At <b>{reversal['perturbation_pct']:.1f}%</b>:")
                summary.append("<ul>")
                for change in reversal['changes'][:5]:  # Top 5 changes
                    summary.append(f"<li>{change}</li>")
                summary.append("</ul></li>")
            summary.append("</ul>")
        else:
            summary.append("<p style='color: #27ae60; font-weight: bold; font-size: 14px;'>✓ No Rank Reversals</p>")
            summary.append("<p>The ranking is <b>stable</b> across all perturbations tested.</p>")
        
        # Stability index
        stability = results.get('stability_index', 0)
        if stability > 0.8:
            status = "High (Robust)"
            color = "#27ae60"
        elif stability > 0.5:
            status = "Moderate"
            color = "#f39c12"
        else:
            status = "Low (Sensitive)"
            color = "#e74c3c"
        
        summary.append(
            f"<p><b>Stability Index:</b> "
            f"<span style='color:{color}; font-size: 14px; font-weight: bold;'>{stability:.2f}</span> "
            f"({status})</p>"
        )
        
        self.summary_text.setHtml("".join(summary))
    
    def export_results(self):
        """Export analysis results to Excel with Summary + Detailed Data sheets"""
        if not self.current_results:
            QMessageBox.warning(self, "No Results", "Please run analysis first!")
            return
        
        try:
            import pandas as pd
        except ImportError:
            QMessageBox.critical(
                self, "Missing Library",
                "pandas library is required for Excel export.\n\n"
                "Please install: pip install pandas openpyxl xlsxwriter"
            )
            return
        
        from PyQt6.QtWidgets import QFileDialog
        
        # Get criterion currently analyzed
        criterion_idx = self.criterion_combo.currentIndex()
        if criterion_idx < 0:
            return
        
        criterion_name = self.criteria[criterion_idx]['name']
        
        # Get file path
        default_filename = f"Sensitivity_{criterion_name.replace(' ', '_')}.xlsx"
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Export Sensitivity Analysis", 
            default_filename, 
            "Excel Files (*.xlsx)"
        )
        
        if not file_path:
            return
        
        try:
            crit_data = self.current_results[criterion_name]
            perturbations = crit_data['perturbations']
            CC_matrix = crit_data['closeness_coefficients']
            rankings_list = crit_data['rankings']
            
            # Get base ranking (at 0% perturbation)
            base_idx = len(perturbations) // 2  # Middle point is 0%
            base_ranking = rankings_list[base_idx]
            
            # ============================================================
            # Sheet 1: Summary
            # ============================================================
            base_weight = self.criteria[criterion_idx]['weight']
            
            summary_data = {
                'Metric': [
                    'Target Criterion',
                    'Base Weight',
                    'Perturbation Range',
                    'Number of Steps',
                    'Stability Index',
                    'Rank Reversals Detected',
                    'Critical Perturbation',
                    'Base Ranking (0%)'
                ],
                'Value': [
                    criterion_name,
                    f"{base_weight:.4f} ({base_weight*100:.2f}%)",
                    f"{min(perturbations):.1f}% to {max(perturbations):.1f}%",
                    len(perturbations),
                    f"{self.current_results.get('stability_index', 0):.4f}",
                    len(crit_data['rank_reversal_points']),
                    f"{crit_data.get('critical_perturbation', 'None')}%" if crit_data.get('critical_perturbation') else 'None',
                    ', '.join([self.alternatives[i]['name'] for i in base_ranking])
                ]
            }
            df_summary = pd.DataFrame(summary_data)
            
            # ============================================================
            # Sheet 2: Detailed_Data
            # ============================================================
            data = {
                'Perturbation (%)': perturbations,
            }
            
            # Add Weight column
            data[f'Weight ({criterion_name})'] = crit_data['weights_at_perturbations']
            
            # Add Score columns for each alternative
            for alt_idx, alt in enumerate(self.alternatives):
                data[f'Score ({alt["name"]})'] = CC_matrix[alt_idx, :]
            
            # Add Rank columns for each alternative
            for alt_idx, alt in enumerate(self.alternatives):
                ranks = []
                for ranking in rankings_list:
                    rank = ranking.index(alt_idx) + 1  # 1-indexed
                    ranks.append(rank)
                data[f'Rank ({alt["name"]})'] = ranks
            
            df_details = pd.DataFrame(data)
            
            # ============================================================
            # Write to Excel with formatting
            # ============================================================
            with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                # Write sheets
                df_summary.to_excel(writer, sheet_name='Summary', index=False)
                df_details.to_excel(writer, sheet_name='Detailed_Data', index=False)
                
                # Get workbook and worksheets for formatting
                workbook = writer.book
                summary_sheet = writer.sheets['Summary']
                detail_sheet = writer.sheets['Detailed_Data']
                
                # --------------------------------------------------------
                # Format Summary Sheet
                # --------------------------------------------------------
                header_fmt = workbook.add_format({
                    'bold': True,
                    'bg_color': '#4CAF50',
                    'font_color': 'white',
                    'border': 1
                })
                
                metric_fmt = workbook.add_format({
                    'bold': True,
                    'border': 1
                })
                
                value_fmt = workbook.add_format({
                    'border': 1
                })
                
                # Apply formatting to Summary
                for col_num, value in enumerate(df_summary.columns.values):
                    summary_sheet.write(0, col_num, value, header_fmt)
                
                summary_sheet.set_column('A:A', 25, metric_fmt)
                summary_sheet.set_column('B:B', 40, value_fmt)
                
                # --------------------------------------------------------
                # Format Detailed_Data Sheet
                # --------------------------------------------------------
                # Header format
                for col_num, value in enumerate(df_details.columns.values):
                    detail_sheet.write(0, col_num, value, header_fmt)
                
                # Column formats
                number_fmt = workbook.add_format({'num_format': '0.0000', 'border': 1})
                pct_fmt = workbook.add_format({'num_format': '0.0', 'border': 1})
                rank_fmt = workbook.add_format({'border': 1, 'align': 'center'})
                
                # Set column widths and formats
                detail_sheet.set_column('A:A', 18, pct_fmt)  # Perturbation
                detail_sheet.set_column('B:B', 20, number_fmt)  # Weight
                
                # Score columns
                score_col_start = 2
                score_col_end = score_col_start + len(self.alternatives) - 1
                for col in range(score_col_start, score_col_end + 1):
                    detail_sheet.set_column(col, col, 18, number_fmt)
                
                # Rank columns
                rank_col_start = score_col_end + 1
                rank_col_end = rank_col_start + len(self.alternatives) - 1
                
                # --------------------------------------------------------
                # Conditional Formatting: Highlight Rank Reversals
                # --------------------------------------------------------
                base_row = base_idx + 2  # +2 for header row and 1-indexed
                
                for col in range(rank_col_start, rank_col_end + 1):
                    # Get base ranking value for this alternative
                    alt_idx = col - rank_col_start
                    base_rank = base_ranking.index(alt_idx) + 1
                    
                    # Format for rank changes (red background)
                    rank_change_fmt = workbook.add_format({
                        'bg_color': '#ffcccc',
                        'border': 1,
                        'align': 'center',
                        'bold': True
                    })
                    
                    # Apply conditional formatting to highlight changes from base
                    detail_sheet.conditional_format(
                        1, col, len(perturbations), col,  # Range: row 1 to last data row
                        {
                            'type': 'formula',
                            'criteria': f'=${chr(65+col)}2<>${chr(65+col)}${base_row}',
                            'format': rank_change_fmt
                        }
                    )
                    
                    # Set column width for rank columns
                    detail_sheet.set_column(col, col, 15, rank_fmt)
                
                # --------------------------------------------------------
                # Add 0% baseline marker
                # --------------------------------------------------------
                baseline_fmt = workbook.add_format({
                    'bg_color': '#ffff99',
                    'border': 2,
                    'border_color': 'black'
                })
                
                # Highlight the 0% row
                for col in range(len(df_details.columns)):
                    detail_sheet.write(base_row - 1, col, 
                                     df_details.iloc[base_idx, col], 
                                     baseline_fmt)
            
            QMessageBox.information(
                self, 
                "Export Successful", 
                f"Sensitivity analysis results exported to:\n{file_path}\n\n"
                f"Sheets:\n"
                f"• Summary: Overview and metrics\n"
                f"• Detailed_Data: Scores and rankings\n\n"
                f"Rank changes are highlighted in red.\n"
                f"0% baseline is highlighted in yellow."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Export Error", 
                f"Failed to export results:\n{str(e)}\n\n"
                f"Please ensure you have pandas and xlsxwriter installed."
            )
            import traceback
            traceback.print_exc()
