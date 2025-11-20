    
    def display_hierarchical_weights(self, global_weights):
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
            
            # Create items
            name_item = QTableWidgetItem(name)
            weight_item = QTableWidgetItem(f"{weight:.4f}")
            
            # Make parent criteria bold
            if criterion.get('parent_id') is None:
                font = name_item.font()
                font.setBold(True)
                name_item.setFont(font)
                weight_item.setFont(font)
            
            self.weights_table.setItem(row, 0, name_item)
            self.weights_table.setItem(row, 1, weight_item)
        
        # Display in hierarchical order
        main_criteria = [c for c in self.criteria if c.get('parent_id') is None]
        
        for main_criterion in main_criteria:
            add_criterion_row(main_criterion, 0)
            
            # Add sub-criteria
            sub_criteria = [c for c in self.criteria if c.get('parent_id') == main_criterion['id']]
            for sub_criterion in sub_criteria:
                add_criterion_row(sub_criterion, 1)
        
        # Update CR label
        self.cr_label.setText("Hierarchical weights calculated (CR per level)")
        self.cr_label.setStyleSheet("color: blue; font-weight: bold;")
