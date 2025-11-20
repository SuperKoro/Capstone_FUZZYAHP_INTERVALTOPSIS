"""
Supplier Selection Desktop Application
Main Entry Point

A standalone desktop application for supplier selection using:
- Fuzzy AHP for criteria weighting
- Interval TOPSIS for alternative ranking
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from gui.main_window import MainWindow


def main():
    """Main application entry point"""
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
