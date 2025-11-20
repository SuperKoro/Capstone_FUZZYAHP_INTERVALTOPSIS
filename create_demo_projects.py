import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.append(os.getcwd())

from database.schema import DatabaseSchema
from database.manager import DatabaseManager

def create_demo_projects():
    """Create demo projects for testing import functionality"""
    
    # 1. Create Master Project
    master_file = "Demo_Master.mcdm"
    if os.path.exists(master_file):
        os.remove(master_file)
        
    print(f"Creating {master_file}...")
    DatabaseSchema.create_schema(master_file)
    DatabaseSchema.initialize_project(master_file, "Demo Master Project")
    
    db_master = DatabaseManager(master_file)
    with db_master as db:
        # Get Project ID
        project = db.get_project()
        pid = project['id']
        
        # Add Criteria
        c_price = db.add_criterion(pid, "Price", is_benefit=False)
        c_quality = db.add_criterion(pid, "Quality", is_benefit=True)
        c_delivery = db.add_criterion(pid, "Delivery", is_benefit=True)
        
        # Add Alternatives
        db.add_alternative(pid, "Supplier A", "Domestic supplier")
        db.add_alternative(pid, "Supplier B", "International supplier")
        
        # Add Expert 1
        e1 = db.add_expert(pid, "Project Manager")
        
        # Add Comparisons for Expert 1 (Price vs Quality: Price is moderately less important)
        # Scale -3: (1/4, 1/3, 1/2)
        db.add_ahp_comparison(pid, e1, c_price, c_quality, 1/4, 1/3, 1/2)
        
        # Price vs Delivery: Equal
        # Scale 1: (1, 1, 1)
        db.add_ahp_comparison(pid, e1, c_price, c_delivery, 1, 1, 1)
        
        # Quality vs Delivery: Quality is moderately more important
        # Scale 3: (2, 3, 4)
        db.add_ahp_comparison(pid, e1, c_quality, c_delivery, 2, 3, 4)

    # 2. Create Expert Evaluation Project
    expert_file = "Demo_Expert.mcdm"
    if os.path.exists(expert_file):
        os.remove(expert_file)
        
    print(f"Creating {expert_file}...")
    DatabaseSchema.create_schema(expert_file)
    DatabaseSchema.initialize_project(expert_file, "Demo Expert Evaluation")
    
    db_expert = DatabaseManager(expert_file)
    with db_expert as db:
        # Get Project ID
        project = db.get_project()
        pid = project['id']
        
        # Add Criteria (MUST MATCH NAMES)
        c_price = db.add_criterion(pid, "Price", is_benefit=False)
        c_quality = db.add_criterion(pid, "Quality", is_benefit=True)
        c_delivery = db.add_criterion(pid, "Delivery", is_benefit=True)
        
        # Add Expert 2
        e2 = db.add_expert(pid, "External Consultant")
        
        # Add Comparisons for Expert 2 (Different opinions)
        
        # Price vs Quality: Price is strongly more important (Cost focus)
        # Scale 5: (4, 5, 6)
        db.add_ahp_comparison(pid, e2, c_price, c_quality, 4, 5, 6)
        
        # Price vs Delivery: Price is moderately more important
        # Scale 3: (2, 3, 4)
        db.add_ahp_comparison(pid, e2, c_price, c_delivery, 2, 3, 4)
        
        # Quality vs Delivery: Equal
        # Scale 1: (1, 1, 1)
        db.add_ahp_comparison(pid, e2, c_quality, c_delivery, 1, 1, 1)

    print("Demo projects created successfully!")
    print(f"1. {master_file} (Open this one first)")
    print(f"2. {expert_file} (Import this one)")

if __name__ == "__main__":
    create_demo_projects()
