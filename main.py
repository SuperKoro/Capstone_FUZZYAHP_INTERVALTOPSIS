"""
Supplier Selection Desktop Application
Main Entry Point

A standalone desktop application for supplier selection using:
- Fuzzy AHP for criteria weighting
- Interval TOPSIS for alternative ranking
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from gui.main_window import MainWindow


def check_migration_status():
    """Check if any .mcdm files need migration and display warning if needed"""
    try:
        from database.database_migration import check_migration_needed
        
        # Find all .mcdm files in current directory
        mcdm_files = [f for f in os.listdir('.') if f.endswith('.mcdm')]
        needs_migration = []
        
        for mcdm_file in mcdm_files:
            if os.path.exists(mcdm_file):
                try:
                    if check_migration_needed(mcdm_file):
                        needs_migration.append(mcdm_file)
                except Exception:
                    # Ignore errors during check
                    pass
        
        if needs_migration:
            print("\n" + "="*60)
            print("⚠️  DATABASE MIGRATION REQUIRED")
            print("="*60)
            print("The following database files need to be migrated:")
            for f in needs_migration:
                print(f"  - {f}")
            print("\nTo fix this, run: python run_migration.py")
            print("="*60 + "\n")
    except Exception:
        # Silently ignore if migration check fails
        pass


def main():
    """Main application entry point"""
    # Check migration status before starting app
    check_migration_status()
    
    # Enable High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Supplier Selection - Fuzzy AHP & TOPSIS")
    app.setOrganizationName("MCDM Solutions")
    
    # Set application style
    app.setStyle("Fusion")
    
    # Apply modern stylesheet
    from gui.styles import MODERN_STYLE
    app.setStyleSheet(MODERN_STYLE)
    
    # Set application icon
    import os
    from PyQt6.QtGui import QIcon
    icon_path = os.path.join(os.path.dirname(__file__), "resources", "logo.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
