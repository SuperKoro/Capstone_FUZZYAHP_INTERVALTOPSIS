"""
Hierarchical Criteria Tree Widget
Provides a visual tree structure for managing criteria hierarchy
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
                             QPushButton, QInputDialog, QMessageBox, QLabel, QComboBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QColor, QBrush


class NoScrollComboBox(QComboBox):
    """Custom QComboBox that disables mouse wheel scrolling"""
    
    def wheelEvent(self, event):
        """Ignore wheel events to prevent accidental selection changes"""
        event.ignore()


class CriteriaTreeWidget(QWidget):
    """Tree widget for hierarchical criteria management"""
    
    # Signal emitted when criteria structure changes
    criteria_changed = pyqtSignal()
    
    def __init__(self, db_manager, project_id, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.project_id = project_id
        self.goal_item = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 0, 5, 5)
        layout.setSpacing(2)
        
        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Criterion Name", "Type", "Actions"])
        
        # PART 2: Disable internal scrollbar
        self.tree.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tree.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Configure header resizing
        header = self.tree.header()
        from PyQt6.QtWidgets import QHeaderView
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
        # PART 3: Connect signals for dynamic height update
        self.tree.itemExpanded.connect(self.update_tree_height)
        self.tree.itemCollapsed.connect(self.update_tree_height)
        
        layout.addWidget(self.tree, stretch=1)
        
        # Instructions (compact)
        instructions = QLabel(
            "• Click + on Goal to add main criteria  • Click + on criteria to add sub-criteria  • Click - to remove criteria (except Goal)"
        )
        instructions.setStyleSheet("color: gray; font-size: 10px;")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        self.setLayout(layout)
        
        # Initialize with Goal node
        self.create_goal_node()
    
    def create_goal_node(self):
        """Create the root Goal node"""
        self.tree.clear()
        
        self.goal_item = QTreeWidgetItem(self.tree)
        self.goal_item.setText(0, "Goal")
        self.goal_item.setText(1, "Root")
        self.goal_item.setData(0, Qt.ItemDataRole.UserRole, None)  # No DB ID for goal
        
        # Make Goal bold and blue
        font = self.goal_item.font(0)
        font.setBold(True)
        self.goal_item.setFont(0, font)
        self.goal_item.setForeground(0, QBrush(QColor(52, 114, 196)))
        
        # Add + button for Goal
        self.add_action_buttons(self.goal_item, show_delete=False)
        
        self.goal_item.setExpanded(True)
    
    def add_action_buttons(self, item, show_delete=True):
        """Add +/- buttons to a tree item"""
        # Calculate the level/depth of this item
        level = 0
        parent = item.parent()
        while parent is not None:
            level += 1
            parent = parent.parent()
        
        # Create button widget with indentation based on level
        button_widget = QWidget()
        button_layout = QHBoxLayout()
        
        # Add left margin based on level (20 pixels per level)
        left_margin = level * 20
        button_layout.setContentsMargins(left_margin, 2, 2, 2)
        button_layout.setSpacing(5)
        
        # Add button (+) - adaptive sizing
        from PyQt6.QtWidgets import QSizePolicy
        add_btn = QPushButton("Add")
        add_btn.setMinimumSize(45, 28)  # Minimum size instead of fixed
        add_btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        add_btn.setProperty("class", "success")
        add_btn.setStyleSheet("font-size: 9pt; font-weight: bold;")
        add_btn.setToolTip("Add Sub-criterion")
        add_btn.clicked.connect(lambda: self.add_criterion(item))
        button_layout.addWidget(add_btn)
        
        # Edit button (✎) - Only for non-root items
        if show_delete:  # Root doesn't have delete, so we use this flag to identify non-root
            edit_btn = QPushButton("✎")  # Pencil character
            edit_btn.setMinimumSize(32, 28)  # Minimum size
            edit_btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
            edit_btn.setProperty("class", "warning")
            edit_btn.setStyleSheet("font-size: 13pt; font-weight: bold;")
            edit_btn.setToolTip("Edit Criterion")
            edit_btn.clicked.connect(lambda: self.edit_criterion(item))
            button_layout.addWidget(edit_btn)
        
        # Delete button (-)
        if show_delete:
            del_btn = QPushButton("Delete")
            del_btn.setMinimumSize(55, 28)  # Minimum size
            del_btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
            del_btn.setProperty("class", "danger")
            del_btn.setStyleSheet("font-size: 9pt; font-weight: bold;")
            del_btn.setToolTip("Delete Criterion")
            del_btn.clicked.connect(lambda: self.delete_criterion(item))
            button_layout.addWidget(del_btn)
        
        button_layout.addStretch()
        button_widget.setLayout(button_layout)
        
        self.tree.setItemWidget(item, 2, button_widget)
    
    def add_criterion(self, parent_item):
        """Add a new criterion under the parent item"""
        # Ask for criterion name
        name, ok = QInputDialog.getText(
            self, "Add Criterion", 
            "Enter criterion name:"
        )
        
        if not ok or not name.strip():
            return
        
        # Ask for type (Benefit/Cost)
        from PyQt6.QtWidgets import QDialog, QFormLayout, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Criterion Type")
        layout = QFormLayout()
        
        type_combo = NoScrollComboBox()
        type_combo.addItems(["Benefit", "Cost"])
        layout.addRow("Type:", type_combo)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        is_benefit = type_combo.currentText() == "Benefit"
        
        # Get parent ID
        parent_id = parent_item.data(0, Qt.ItemDataRole.UserRole)
        
        # Add to database
        with self.db_manager as db:
            try:
                criterion_id = db.add_criterion(self.project_id, name.strip(), parent_id, is_benefit)
                
                # Add to tree
                child_item = QTreeWidgetItem(parent_item)
                child_item.setText(0, name.strip())
                child_item.setText(1, "Benefit" if is_benefit else "Cost")
                # Make Type bold
                type_font = child_item.font(1)
                type_font.setBold(True)
                child_item.setFont(1, type_font)
                child_item.setData(0, Qt.ItemDataRole.UserRole, criterion_id)
                
                # Add action buttons
                self.add_action_buttons(child_item, show_delete=True)
                
                parent_item.setExpanded(True)
                
                # Emit signal
                self.criteria_changed.emit()
                
                # Update tree height
                self.update_tree_height()
                
                QMessageBox.information(self, "Success", f"Criterion '{name}' added!")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add criterion: {str(e)}")
    
    def edit_criterion(self, item):
        """Edit a criterion"""
        criterion_name = item.text(0)
        criterion_id = item.data(0, Qt.ItemDataRole.UserRole)
        current_type = item.text(1)
        
        from PyQt6.QtWidgets import QDialog, QFormLayout, QDialogButtonBox, QLineEdit
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Criterion")
        layout = QFormLayout()
        
        name_input = QLineEdit(criterion_name)
        layout.addRow("Name:", name_input)
        
        type_combo = NoScrollComboBox()
        type_combo.addItems(["Benefit", "Cost"])
        type_combo.setCurrentText(current_type)
        layout.addRow("Type:", type_combo)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_name = name_input.text().strip()
            if not new_name:
                QMessageBox.warning(self, "Validation Error", "Name cannot be empty")
                return
                
            is_benefit = type_combo.currentText() == "Benefit"
            
            # Get current parent_id
            parent = item.parent()
            parent_id = None
            if parent and parent != self.goal_item:
                parent_id = parent.data(0, Qt.ItemDataRole.UserRole)
            
            with self.db_manager as db:
                try:
                    db.update_criterion(criterion_id, new_name, parent_id, is_benefit)
                    
                    # Update tree item
                    item.setText(0, new_name)
                    item.setText(1, "Benefit" if is_benefit else "Cost")
                    # Make Type bold
                    type_font = item.font(1)
                    type_font.setBold(True)
                    item.setFont(1, type_font)
                    
                    # Emit signal
                    self.criteria_changed.emit()
                    
                    QMessageBox.information(self, "Success", "Criterion updated!")
                    
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to update criterion: {str(e)}")

    def delete_criterion(self, item):
        """Delete a criterion"""
        criterion_name = item.text(0)
        criterion_id = item.data(0, Qt.ItemDataRole.UserRole)
        
        # Check if it has children
        if item.childCount() > 0:
            QMessageBox.warning(
                self, "Cannot Delete",
                f"Cannot delete '{criterion_name}' because it has sub-criteria.\n"
                "Please delete all sub-criteria first."
            )
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{criterion_name}'?\n"
            "All related comparisons and ratings will be removed.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            with self.db_manager as db:
                try:
                    db.delete_criterion(criterion_id)
                    
                    # Remove from tree
                    parent = item.parent()
                    if parent:
                        parent.removeChild(item)
                    else:
                        self.tree.takeTopLevelItem(self.tree.indexOfTopLevelItem(item))
                    
                    # Emit signal
                    self.criteria_changed.emit()
                    
                    # Update tree height
                    self.update_tree_height()
                    
                    QMessageBox.information(self, "Success", f"Criterion '{criterion_name}' deleted!")
                    
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to delete criterion: {str(e)}")
    
    def load_criteria(self):
        """Load criteria from database and build tree"""
        with self.db_manager as db:
            criteria = db.get_criteria(self.project_id)
        
        # Clear existing items (except goal)
        self.goal_item.takeChildren()
        
        # Build tree structure
        # First pass: create all items
        items_by_id = {}
        
        for criterion in criteria:
            item = QTreeWidgetItem()
            item.setText(0, criterion['name'])
            item.setText(1, "Benefit" if criterion['is_benefit'] else "Cost")
            # Make Type bold
            type_font = item.font(1)
            type_font.setBold(True)
            item.setFont(1, type_font)
            item.setData(0, Qt.ItemDataRole.UserRole, criterion['id'])
            
            items_by_id[criterion['id']] = {
                'item': item,
                'parent_id': criterion['parent_id']
            }
        
        # Second pass: build hierarchy
        for criterion_id, data in items_by_id.items():
            item = data['item']
            parent_id = data['parent_id']
            
            if parent_id is None:
                # Top-level criterion (child of Goal) - Make it bold
                font = item.font(0)
                font.setBold(True)
                font.setPointSize(11)
                item.setFont(0, font)
                item.setForeground(0, QBrush(QColor(41, 128, 185)))  # Blue color for main criteria
                self.goal_item.addChild(item)
            elif parent_id in items_by_id:
                # Sub-criterion
                items_by_id[parent_id]['item'].addChild(item)
            
            # Add action buttons
            self.add_action_buttons(item, show_delete=True)
            item.setExpanded(True)
        
        self.goal_item.setExpanded(True)
        
        # PART 3: Update tree height after loading
        self.update_tree_height()
    
    def update_tree_height(self):
        """PART 3: Recalculate tree height based on visible items"""
        # Calculate total height needed
        total_height = 0
        
        # Add header height
        total_height += self.tree.header().height()
        
        # Helper function to count visible item heights recursively
        def count_visible_height(item):
            # Get this item's height
            rect = self.tree.visualItemRect(item)
            height = rect.height() if rect.isValid() else 30  # Default height if not visible yet
            
            # If expanded, add children heights
            if item.isExpanded():
                for i in range(item.childCount()):
                    height += count_visible_height(item.child(i))
            
            return height
        
        # Count all top-level items and their children
        for i in range(self.tree.topLevelItemCount()):
            total_height += count_visible_height(self.tree.topLevelItem(i))
        
        # Add padding for instructions and borders
        total_height += 60
        
        # Set minimum height (not maximum - allows growth)
        self.tree.setMinimumHeight(total_height)
    
    def get_all_criteria(self):
        """Get all criteria with their hierarchy information"""
        criteria = []
        
        def traverse(item, level=0):
            if item == self.goal_item:
                # Process children of goal
                for i in range(item.childCount()):
                    traverse(item.child(i), level)
            else:
                criterion_id = item.data(0, Qt.ItemDataRole.UserRole)
                if criterion_id is not None:
                    parent = item.parent()
                    parent_id = None
                    if parent and parent != self.goal_item:
                        parent_id = parent.data(0, Qt.ItemDataRole.UserRole)
                    
                    criteria.append({
                        'id': criterion_id,
                        'name': item.text(0),
                        'parent_id': parent_id,
                        'level': level,
                        'is_benefit': item.text(1) == "Benefit"
                    })
                
                # Process children
                for i in range(item.childCount()):
                    traverse(item.child(i), level + 1)
        
        traverse(self.goal_item, 0)
        return criteria
    
    def get_leaf_criteria(self):
        """Get only leaf criteria (criteria without children)"""
        all_criteria = self.get_all_criteria()
        
        # Find which criteria have children
        parent_ids = set(c['parent_id'] for c in all_criteria if c['parent_id'] is not None)
        
        # Return only criteria that are not parents
        leaf_criteria = [c for c in all_criteria if c['id'] not in parent_ids]
        
        return leaf_criteria
