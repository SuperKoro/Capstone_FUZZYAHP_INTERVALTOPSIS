"""
User Guide Dialog Module
Displays step-by-step visual instructions for using the application
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QScrollArea, QWidget, QFrame, QTabWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
import os


class UserGuideDialog(QDialog):
    """Dialog showing visual user guide for the application"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hướng dẫn sử dụng - User Guide")
        self.setGeometry(100, 100, 1100, 800)
        
        # Get the assets directory path relative to project root
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.artifacts_dir = os.path.join(current_dir, "assets", "guide_images")
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        main_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Hướng dẫn sử dụng phần mềm")
        title_font = QFont("Segoe UI", 16, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; padding: 15px;")
        main_layout.addWidget(title_label)
        
        # Create Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
                background: white;
                border-radius: 4px;
            }
            QTabBar::tab {
                background: #f5f6fa;
                border: 1px solid #dcdcdc;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                color: #2c3e50;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom-color: white;
                font-weight: bold;
                color: #2980b9;
            }
            QTabBar::tab:hover {
                background: #ecf0f1;
            }
        """)
        
        # Add tabs
        self.add_intro_tab()
        self.add_project_setup_tab()
        self.add_fuzzy_ahp_tab()
        self.add_topsis_tab()
        self.add_results_tab()
        
        main_layout.addWidget(self.tabs)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_button = QPushButton("Đóng")
        close_button.clicked.connect(self.accept)
        close_button.setMinimumWidth(100)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 20px;
                font-size: 11pt;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        button_layout.addWidget(close_button)
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
        
    def create_tab_content(self, title, steps):
        """Create a scrollable tab content widget
        
        Args:
            title: Title of the section
            steps: List of tuples (step_title, description, image_basename)
        """
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: white; }")
        
        content_widget = QWidget()
        content_widget.setStyleSheet("background: white;")
        content_layout = QVBoxLayout()
        content_layout.setSpacing(30)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Section Title
        section_label = QLabel(title)
        section_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        section_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        content_layout.addWidget(section_label)
        
        for i, (step_title, step_desc, img_name) in enumerate(steps, 1):
            self.add_step_to_layout(content_layout, i, step_title, step_desc, img_name)
            
        content_layout.addStretch()
        content_widget.setLayout(content_layout)
        scroll.setWidget(content_widget)
        return scroll

    def add_step_to_layout(self, layout, step_number, title, description, image_basename):
        """Add a step widget to the layout"""
        step_frame = QFrame()
        step_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        step_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        step_layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        
        # Number
        number_label = QLabel(str(step_number))
        number_label.setFixedSize(30, 30)
        number_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        number_label.setStyleSheet("""
            QLabel {
                background-color: #3498db;
                color: white;
                border-radius: 15px;
                font-weight: bold;
            }
        """)
        header_layout.addWidget(number_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        step_layout.addLayout(header_layout)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #34495e; margin: 10px 0;")
        step_layout.addWidget(desc_label)
        
        # Image
        if image_basename:
            image_label = QLabel()
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            image_path = self.find_image_file(image_basename)
            
            if image_path and os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaledToWidth(800, Qt.TransformationMode.SmoothTransformation)
                    image_label.setPixmap(scaled_pixmap)
                    image_label.setStyleSheet("border: 1px solid #ddd; border-radius: 4px;")
                else:
                    image_label.setText("[Hình ảnh lỗi]")
            else:
                image_label.setText(f"[Đang cập nhật hình ảnh: {image_basename}]")
                image_label.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 20px;")
            
            step_layout.addWidget(image_label)
            
        step_frame.setLayout(step_layout)
        layout.addWidget(step_frame)

    def add_intro_tab(self):
        """Add Introduction tab"""
        content = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Chào mừng đến với Phần mềm Lựa chọn Nhà cung cấp")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        desc = QLabel(
            "Phần mềm này hỗ trợ ra quyết định đa tiêu chí (MCDM) để lựa chọn nhà cung cấp tốt nhất "
            "dựa trên phương pháp kết hợp Fuzzy AHP và TOPSIS.\n\n"
            "Quy trình thực hiện gồm 4 bước chính:"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("font-size: 11pt; color: #34495e;")
        layout.addWidget(desc)
        
        # Process flow
        flow_layout = QHBoxLayout()
        steps = ["1. Thiết lập Dự án", "2. Đánh giá Fuzzy AHP", "3. Xếp hạng TOPSIS", "4. Xuất Kết quả"]
        for step in steps:
            lbl = QLabel(step)
            lbl.setStyleSheet("""
                background-color: #e8f6f3;
                color: #16a085;
                padding: 15px;
                border-radius: 8px;
                font-weight: bold;
                border: 1px solid #a2d9ce;
            """)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            flow_layout.addWidget(lbl)
        layout.addLayout(flow_layout)
        
        # Tips section
        self.add_tips_section(layout)
        
        layout.addStretch()
        content.setLayout(layout)
        self.tabs.addTab(content, "Giới thiệu")

    def add_project_setup_tab(self):
        """Add Project Setup tab"""
        steps = [
            ("Bước 1: Tạo dự án mới", 
             "Từ màn hình chính, nhấn nút 'New' để tạo project mới.\n"
             "Nhập tên project và chọn vị trí lưu file (tệp .mcdm).", 
             "guide_project_setup"),
            ("Bước 2: Thêm tiêu chí đánh giá", 
             "Trong tab 'Project Setup':\n"
             "• Nhấn nút 'Add' ở phần Criteria để thêm tiêu chí chính\n"
             "• Nhấn nút 'Add' bên cạnh tiêu chí để thêm tiêu chí con (sub-criteria)\n"
             "• Chọn loại: Cost (giá trị thấp tốt hơn) hoặc Benefit (giá trị cao tốt hơn)", 
             "guide_criteria_setup"),
            ("Bước 3: Thêm nhà cung cấp", 
             "Ở phần 'Alternatives (Suppliers) Management':\n"
             "• Nhấn nút 'Add Alternative' để thêm từng nhà cung cấp cần đánh giá\n"
             "• Nhập tên và mô tả cho mỗi nhà cung cấp", 
             "guide_project_info")
        ]
        tab = self.create_tab_content("Thiết lập Dự án", steps)
        self.tabs.addTab(tab, "1. Thiết lập")

    def add_fuzzy_ahp_tab(self):
        """Add Fuzzy AHP tab"""
        steps = [
            ("Bước 1: Thêm chuyên gia đánh giá", 
             "Trong tab 'Fuzzy AHP Evaluation':\n"
             "• Nhấn nút 'Add Expert' để thêm chuyên gia\n"
             "• Nhập tên chuyên gia", 
             "guide_ahp_expert"),
            ("Bước 2: So sánh tiêu chí", 
             "Thực hiện so sánh từng cặp tiêu chí:\n"
             "• Chọn chuyên gia từ dropdown\n"
             "• Nhấp vào 'Goal' trong cây Criteria để so sánh các tiêu chí chính\n"
             "• Nhấp vào từng tiêu chí để so sánh các tiêu chí con của nó\n"
             "• Chọn mức độ quan trọng từ dropdown (từ -9 đến +9)", 
             "guide_fuzzy_ahp_input"),
            ("Bước 3: Tính toán trọng số", 
             "Sau khi hoàn thành tất cả so sánh:\n"
             "• Nhấn nút 'Calculate All Weights' để tính toán\n"
             "• Kiểm tra chỉ số CR (Consistency Ratio):\n"
             "  - CR ≤ 0.1 (xanh): Đánh giá nhất quán, tốt ✓\n"
             "  - CR > 0.1 (đỏ): Cần xem xét lại các so sánh", 
             None),
            ("Bước 4: Xem kết quả trọng số", 
             "Chuyển sang tab 'Results' để xem:\n"
             "• Trọng số (Weight) của từng tiêu chí\n"
             "• Biểu đồ trực quan phân bổ trọng số", 
             "guide_fuzzy_ahp_results")
        ]
        tab = self.create_tab_content("Đánh giá Fuzzy AHP", steps)
        self.tabs.addTab(tab, "2. Fuzzy AHP")

    def add_topsis_tab(self):
        """Add TOPSIS tab"""
        steps = [
            ("Bước 1: Chọn chuyên gia", 
             "Trong tab 'TOPSIS Rating':\n"
             "• Chọn chuyên gia từ dropdown 'Expert'", 
             None),
            ("Bước 2: Đánh giá nhà cung cấp", 
             "Đánh giá từng nhà cung cấp theo từng tiêu chí:\n"
             "• Chọn khoảng giá trị từ dropdown (Ví dụ: [3-5] = Fair to Good)\n"
             "• Làm tương tự cho tất cả các ô trong bảng\n"
             "• Lặp lại cho tất cả chuyên gia", 
             "guide_topsis_rating"),
            ("Bước 3: Tính toán xếp hạng", 
             "Sau khi hoàn thành đánh giá:\n"
             "• Nhấn nút 'Calculate TOPSIS Rankings'\n"
             "• Hệ thống sẽ tự động tính toán điểm số cho từng nhà cung cấp", 
             None),
            ("Bước 4: Xem kết quả xếp hạng", 
             "Chuyển sang tab 'Results' để xem:\n"
             "• Bảng xếp hạng cuối cùng (Rank 1 = tốt nhất)\n"
             "• Điểm Closeness Coefficient của từng nhà cung cấp\n"
             "• Nhà cung cấp có điểm cao nhất là lựa chọn tốt nhất", 
             None)
        ]
        tab = self.create_tab_content("Xếp hạng TOPSIS", steps)
        self.tabs.addTab(tab, "3. TOPSIS")

    def add_results_tab(self):
        """Add Results tab"""
        steps = [
            ("Xem kết quả tổng hợp", 
             "Tab 'Results' hiển thị:\n"
             "• Trọng số tiêu chí (từ Fuzzy AHP)\n"
             "• Xếp hạng nhà cung cấp (từ TOPSIS)\n"
             "• Biểu đồ trực quan dễ hiểu", 
             "guide_final_results"),
            ("Xuất báo cáo Excel", 
             "Để lưu trữ hoặc chia sẻ kết quả:\n"
             "• Vào menu 'File' → 'Export Results to Excel'\n"
             "• Chọn vị trí lưu file\n"
             "• File Excel sẽ chứa đầy đủ dữ liệu và kết quả phân tích", 
             None),
            ("Lưu dự án", 
             "Nhớ lưu dự án thường xuyên:\n"
             "• Nhấn Ctrl+S (hoặc File → Save Project)\n"
             "• Dự án được lưu trong file .mcdm\n"
             "• Có thể mở lại bất cứ lúc nào từ menu 'Open'", 
             None)
        ]
        tab = self.create_tab_content("Kết quả & Xuất báo cáo", steps)
        self.tabs.addTab(tab, "4. Kết quả")

    def find_image_file(self, basename):
        """Find image file with given basename (which may have timestamp)"""
        try:
            files = os.listdir(self.artifacts_dir)
            # Sort to get the latest one if multiple exist
            files.sort(reverse=True)
            for filename in files:
                if filename.startswith(basename) and filename.endswith('.png'):
                    return os.path.join(self.artifacts_dir, filename)
        except Exception:
            pass
        return None
    
    def add_tips_section(self, layout):
        """Add tips and tricks section"""
        tips_frame = QFrame()
        tips_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        tips_frame.setStyleSheet("""
            QFrame {
                background-color: #e8f5e9;
                border: 1px solid #a5d6a7;
                border-radius: 8px;
                padding: 20px;
                margin-top: 20px;
            }
        """)
        
        tips_layout = QVBoxLayout()
        
        # Title
        tips_title = QLabel("💡 Mẹo và Lưu ý")
        tips_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        tips_title.setStyleSheet("color: #2e7d32;")
        tips_layout.addWidget(tips_title)
        
        # Tips content
        tips_text = """
<ul style="line-height: 1.6; color: #1b5e20; margin-top: 0;">
    <li><b>Lưu thường xuyên:</b> Nhấn Ctrl+S để lưu dự án.</li>
    <li><b>Chỉ số CR:</b> Trong Fuzzy AHP, nếu CR > 0.1 (màu đỏ), hãy điều chỉnh lại các so sánh.</li>
    <li><b>Nhiều chuyên gia:</b> Nên nhập dữ liệu từ nhiều chuyên gia để có kết quả khách quan.</li>
    <li><b>Xuất Excel:</b> Luôn xuất kết quả ra Excel để lưu trữ và báo cáo chi tiết.</li>
</ul>
        """
        
        tips_content = QLabel(tips_text)
        tips_content.setWordWrap(True)
        tips_content.setTextFormat(Qt.TextFormat.RichText)
        tips_layout.addWidget(tips_content)
        
        tips_frame.setLayout(tips_layout)
        layout.addWidget(tips_frame)
