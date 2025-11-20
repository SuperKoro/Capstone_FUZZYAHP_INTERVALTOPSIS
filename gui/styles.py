"""
Application Styles
Modern QSS stylesheet for the Supplier Selection app
"""

MODERN_STYLE = """
/* ===== Global Settings ===== */
QMainWindow {
    background-color: #f5f6fa;
}

QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 9pt;
    color: #2c3e50;
}

/* ===== Menu Bar ===== */
QMenuBar {
    background-color: #2c3e50;
    color: white;
    padding: 4px;
    border-bottom: 2px solid #3498db;
}

QMenuBar::item {
    background-color: transparent;
    padding: 6px 12px;
    margin: 2px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #34495e;
}

QMenuBar::item:pressed {
    background-color: #3498db;
}

QMenu {
    background-color: #ffffff;
    border: 1px solid #bdc3c7;
    border-radius: 6px;
    padding: 4px;
}

QMenu::item {
    padding: 6px 24px 6px 12px;
    border-radius: 4px;
    margin: 2px;
}

QMenu::item:selected {
    background-color: #3498db;
    color: white;
}

QMenu::separator {
    height: 1px;
    background-color: #ecf0f1;
    margin: 4px 8px;
}

/* ===== Tool Bar ===== */
QToolBar {
    background-color: #34495e;
    border: none;
    spacing: 4px;
    padding: 6px;
}

QToolBar QToolButton {
    background-color: transparent;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 6px 12px;
    margin: 2px;
}

QToolBar QToolButton:hover {
    background-color: #3498db;
}

QToolBar QToolButton:pressed {
    background-color: #2980b9;
}

QToolBar::separator {
    width: 1px;
    background-color: #7f8c8d;
    margin: 4px 8px;
}

/* ===== Status Bar ===== */
QStatusBar {
    background-color: #ecf0f1;
    color: #2c3e50;
    border-top: 1px solid #bdc3c7;
    padding: 4px;
}

/* ===== Tab Widget ===== */
QTabWidget::pane {
    border: 1px solid #dfe6e9;
    border-radius: 6px;
    background-color: white;
    top: -1px;
}

QTabBar::tab {
    background-color: #ecf0f1;
    color: #2c3e50;
    border: 1px solid #dfe6e9;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 10px 20px;
    margin-right: 2px;
    font-weight: 500;
}

QTabBar::tab:selected {
    background-color: white;
    color: #3498db;
    border-bottom: 2px solid #3498db;
    font-weight: 600;
}

QTabBar::tab:hover:!selected {
    background-color: #dfe6e9;
}

/* ===== Group Box ===== */
QGroupBox {
    background-color: white;
    border: 2px solid #e8eef2;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: 600;
    font-size: 10pt;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 4px 8px;
    background-color: #3498db;
    color: white;
    border-radius: 4px;
}

/* ===== Buttons ===== */
QPushButton {
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-weight: 500;
    min-width: 80px;
}

QPushButton:hover {
    background-color: #2980b9;
}

QPushButton:pressed {
    background-color: #21618c;
}

QPushButton:disabled {
    background-color: #bdc3c7;
    color: #7f8c8d;
}

/* Success Button */
QPushButton[class="success"] {
    background-color: #219150;  /* Muted Green */
}

QPushButton[class="success"]:hover {
    background-color: #1e8449;
}

/* Danger Button */
QPushButton[class="danger"] {
    background-color: #c0392b;  /* Muted Red */
}

QPushButton[class="danger"]:hover {
    background-color: #a93226;
}

/* Warning Button */
QPushButton[class="warning"] {
    background-color: #d4ac0d;  /* Muted Yellow/Orange */
    color: white;
}

QPushButton[class="warning"]:hover {
    background-color: #b7950b;
}

/* ===== Line Edit ===== */
QLineEdit {
    background-color: white;
    border: 1px solid #bdc3c7;  /* Thinner, softer border */
    border-radius: 4px;
    padding: 6px 10px;
    selection-background-color: #3498db;
    color: #2c3e50;
}

QLineEdit:focus {
    border: 1px solid #3498db;
}

QLineEdit:disabled {
    background-color: #f5f6fa;
    color: #95a5a6;
}

/* ===== Text Edit ===== */
QTextEdit, QPlainTextEdit {
    background-color: white;
    border: 1px solid #bdc3c7;
    border-radius: 4px;
    padding: 6px;
    selection-background-color: #3498db;
    color: #2c3e50;
}

QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #3498db;
}

/* ===== Combo Box ===== */
QComboBox {
    background-color: white;
    border: 1px solid #bdc3c7;
    border-radius: 4px;
    padding: 4px 10px;
    min-width: 60px;
    color: #2c3e50;
}

QComboBox:hover {
    border: 1px solid #3498db;
}

QComboBox:focus {
    border: 1px solid #3498db;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    image: url(none);
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #7f8c8d;
    width: 0px;
    height: 0px;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: white;
    border: 1px solid #bdc3c7;
    border-radius: 4px;
    selection-background-color: #3498db;
    selection-color: white;
    padding: 2px;
    outline: none;
}

/* Specific style for ComboBox inside Table to fix visibility */
QTableWidget QComboBox {
    margin: 1px;
    padding: 1px 5px;
    border: none;
    background-color: transparent;
}

QTableWidget QComboBox:hover {
    background-color: #f0f3f4;
}

/* ===== Spin Box ===== */
QSpinBox, QDoubleSpinBox {
    background-color: white;
    border: 1px solid #bdc3c7;
    border-radius: 4px;
    padding: 4px 8px;
    color: #2c3e50;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border: 2px solid #3498db;
}

QSpinBox::up-button, QDoubleSpinBox::up-button {
    border: none;
    background-color: #ecf0f1;
    border-top-right-radius: 4px;
    width: 16px;
}

QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {
    background-color: #3498db;
}

QSpinBox::down-button, QDoubleSpinBox::down-button {
    border: none;
    background-color: #ecf0f1;
    border-bottom-right-radius: 4px;
    width: 16px;
}

QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
    background-color: #3498db;
}

/* ===== Table Widget ===== */
QTableWidget {
    background-color: white;
    alternate-background-color: #f8f9fa;
    gridline-color: #dfe6e9;
    border: 2px solid #dfe6e9;
    border-radius: 6px;
    selection-background-color: #3498db;
    selection-color: white;
}

QTableWidget::item {
    padding: 6px;
}

QTableWidget::item:hover {
    background-color: #eef5ff;
}

QHeaderView::section {
    background-color: #34495e;
    color: white;
    padding: 8px;
    border: none;
    font-weight: 600;
    border-right: 1px solid #2c3e50;
}

QHeaderView::section:first {
    border-top-left-radius: 4px;
}

QHeaderView::section:last {
    border-top-right-radius: 4px;
    border-right: none;
}

QHeaderView::section:hover {
    background-color: #3498db;
}

/* ===== Scroll Bar ===== */
QScrollBar:vertical {
    background-color: #ecf0f1;
    width: 12px;
    border-radius: 6px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #bdc3c7;
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #95a5a6;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #ecf0f1;
    height: 12px;
    border-radius: 6px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background-color: #bdc3c7;
    border-radius: 6px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #95a5a6;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* ===== Labels ===== */
QLabel {
    color: #2c3e50;
    background-color: transparent;
}

QLabel[class="heading"] {
    font-size: 14pt;
    font-weight: 600;
    color: #2c3e50;
}

QLabel[class="subheading"] {
    font-size: 11pt;
    font-weight: 500;
    color: #34495e;
}

/* ===== Progress Bar ===== */
QProgressBar {
    background-color: #ecf0f1;
    border: 2px solid #dfe6e9;
    border-radius: 6px;
    text-align: center;
    height: 20px;
}

QProgressBar::chunk {
    background-color: #3498db;
    border-radius: 4px;
}

/* ===== Message Box ===== */
QMessageBox {
    background-color: white;
}

QMessageBox QPushButton {
    min-width: 80px;
    padding: 6px 16px;
}

/* ===== Tool Tip ===== */
QToolTip {
    background-color: #34495e;
    color: white;
    border: 1px solid #2c3e50;
    border-radius: 4px;
    padding: 6px 8px;
}
"""
