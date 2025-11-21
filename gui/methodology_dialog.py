"""
Methodology Dialog Module
Displays information about Fuzzy AHP and Interval TOPSIS methodologies
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTabWidget, QTextBrowser, 
                             QPushButton, QHBoxLayout, QWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class MethodologyDialog(QDialog):
    """Dialog showing methodology information for Fuzzy AHP and Interval TOPSIS"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Methodology - Fuzzy AHP & Interval TOPSIS")
        self.setGeometry(100, 100, 900, 700)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Create tab widget
        tabs = QTabWidget()
        
        # Fuzzy AHP tab
        fuzzy_ahp_widget = self.create_fuzzy_ahp_tab()
        tabs.addTab(fuzzy_ahp_widget, "Fuzzy AHP")
        
        # Interval TOPSIS tab
        interval_topsis_widget = self.create_interval_topsis_tab()
        tabs.addTab(interval_topsis_widget, "Interval TOPSIS")
        
        layout.addWidget(tabs)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_button = QPushButton("Đóng")
        close_button.clicked.connect(self.accept)
        close_button.setMinimumWidth(100)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def create_fuzzy_ahp_tab(self) -> QWidget:
        """Create Fuzzy AHP methodology tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        
        # Set font
        font = QFont("Segoe UI", 10)
        browser.setFont(font)
        
        # HTML content
        html_content = """
        <html>
        <head>
            <style>
                body { font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; padding: 15px; }
                h2 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px; }
                h3 { color: #34495e; margin-top: 20px; }
                .formula { background-color: #ecf0f1; padding: 10px; margin: 10px 0; border-left: 4px solid #3498db; font-family: 'Courier New', monospace; }
                .example { background-color: #e8f5e9; padding: 10px; margin: 10px 0; border-left: 4px solid #4caf50; }
                ul { margin-left: 20px; }
                li { margin: 8px 0; }
                .scale-table { border-collapse: collapse; width: 100%; margin: 15px 0; }
                .scale-table th, .scale-table td { border: 1px solid #bdc3c7; padding: 8px; text-align: left; }
                .scale-table th { background-color: #3498db; color: white; }
                .scale-table tr:nth-child(even) { background-color: #f8f9fa; }
            </style>
        </head>
        <body>
            <h2>Phương pháp Fuzzy AHP (Analytical Hierarchy Process)</h2>
            
            <h3>1. Tổng quan</h3>
            <p>Fuzzy AHP là phương pháp phân tích thứ bậc mờ, kết hợp AHP truyền thống với lý thuyết tập mờ để xử lý sự không chắc chắn trong đánh giá của chuyên gia.</p>
            
            <h3>2. Thang đo Fuzzy (Triangular Fuzzy Numbers)</h3>
            <table class="scale-table">
                <tr>
                    <th>Mức độ quan trọng</th>
                    <th>Giá trị ngôn ngữ</th>
                    <th>Số mờ tam giác (l, m, u)</th>
                </tr>
                <tr><td>1</td><td>Equally important (Ngang nhau)</td><td>(1, 1, 1)</td></tr>
                <tr><td>2</td><td>Weak advantage</td><td>(1, 2, 3)</td></tr>
                <tr><td>3</td><td>Moderate importance (Hơn một chút)</td><td>(2, 3, 4)</td></tr>
                <tr><td>4</td><td>Moderate plus</td><td>(3, 4, 5)</td></tr>
                <tr><td>5</td><td>Strong importance (Quan trọng hơn)</td><td>(4, 5, 6)</td></tr>
                <tr><td>6</td><td>Strong plus</td><td>(5, 6, 7)</td></tr>
                <tr><td>7</td><td>Very strong (Quan trọng hơn nhiều)</td><td>(6, 7, 8)</td></tr>
                <tr><td>8</td><td>Very, very strong</td><td>(7, 8, 9)</td></tr>
                <tr><td>9</td><td>Extreme importance (Cực kỳ quan trọng)</td><td>(8, 9, 9)</td></tr>
            </table>
            
            <h3>3. Các bước tính toán</h3>
            
            <h4>Bước 1: Xây dựng ma trận so sánh cặp mờ</h4>
            <p>Mỗi phần tử trong ma trận là một số mờ tam giác ã = (l, m, u) thể hiện mức độ so sánh giữa tiêu chí i và j.</p>
            
            <h4>Bước 2: Tính tổng hàng và tổng cột (Fuzzy Geometric Mean)</h4>
            <div class="formula">
                r̃ᵢ = (∏ⱼ ãᵢⱼ)^(1/n)<br>
                <br>
                Với số mờ tam giác:<br>
                r̃ᵢ = (lᵢ, mᵢ, uᵢ)<br>
                lᵢ = (∏ⱼ lᵢⱼ)^(1/n)<br>
                mᵢ = (∏ⱼ mᵢⱼ)^(1/n)<br>
                uᵢ = (∏ⱼ uᵢⱼ)^(1/n)
            </div>
            
            <h4>Bước 3: Tính trọng số mờ của các tiêu chí</h4>
            <div class="formula">
                w̃ᵢ = r̃ᵢ ⊗ (r̃₁ ⊕ r̃₂ ⊕ ... ⊕ r̃ₙ)⁻¹<br>
                <br>
                Trong đó:<br>
                - ⊕ là phép cộng số mờ: (l₁, m₁, u₁) ⊕ (l₂, m₂, u₂) = (l₁+l₂, m₁+m₂, u₁+u₂)<br>
                - ⊗ là phép nhân số mờ<br>
                - ⁻¹ là phép nghịch đảo: (l, m, u)⁻¹ = (1/u, 1/m, 1/l)
            </div>
            
            <h4>Bước 4: Defuzzification (Khử mờ)</h4>
            <p>Chuyển trọng số mờ thành số thực bằng phương pháp Center of Area (CoA):</p>
            <div class="formula">
                wᵢ = (lᵢ + 4mᵢ + uᵢ) / 6
            </div>
            
            <h4>Bước 5: Chuẩn hóa trọng số</h4>
            <div class="formula">
                Wᵢ = wᵢ / Σⱼ wⱼ<br>
                <br>
                Đảm bảo: Σᵢ Wᵢ = 1
            </div>
            
            <h3>4. Kiểm tra tính nhất quán (Consistency)</h3>
            <p>Để đảm bảo đánh giá có tính nhất quán, phần mềm tính toán:</p>
            <ul>
                <li><b>λmax</b>: Giá trị riêng lớn nhất của ma trận</li>
                <li><b>CI</b> (Consistency Index): CI = (λmax - n) / (n - 1)</li>
                <li><b>CR</b> (Consistency Ratio): CR = CI / RI</li>
            </ul>
            <div class="example">
                <b>Ngưỡng chấp nhận:</b> CR < 0.1 (10%)<br>
                Nếu CR ≥ 0.1, cần xem xét lại các đánh giá so sánh cặp.
            </div>
            
            <h3>5. Tích hợp đánh giá của nhiều chuyên gia</h3>
            <p>Khi có nhiều chuyên gia, phần mềm tổng hợp bằng trung bình hình học:</p>
            <div class="formula">
                ãᵢⱼ = ((∏ₖ lᵢⱼₖ)^(1/K), (∏ₖ mᵢⱼₖ)^(1/K), (∏ₖ uᵢⱼₖ)^(1/K))
            </div>
            <p>Trong đó K là số lượng chuyên gia.</p>
            
        </body>
        </html>
        """
        
        browser.setHtml(html_content)
        layout.addWidget(browser)
        widget.setLayout(layout)
        
        return widget
    
    def create_interval_topsis_tab(self) -> QWidget:
        """Create Interval TOPSIS methodology tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        
        # Set font
        font = QFont("Segoe UI", 10)
        browser.setFont(font)
        
        # HTML content
        html_content = """
        <html>
        <head>
            <style>
                body { font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; padding: 15px; }
                h2 { color: #2c3e50; border-bottom: 2px solid #e74c3c; padding-bottom: 5px; }
                h3 { color: #34495e; margin-top: 20px; }
                .formula { background-color: #ecf0f1; padding: 10px; margin: 10px 0; border-left: 4px solid #e74c3c; font-family: 'Courier New', monospace; }
                .example { background-color: #fff3e0; padding: 10px; margin: 10px 0; border-left: 4px solid #ff9800; }
                ul { margin-left: 20px; }
                li { margin: 8px 0; }
                .scale-table { border-collapse: collapse; width: 100%; margin: 15px 0; }
                .scale-table th, .scale-table td { border: 1px solid #bdc3c7; padding: 8px; text-align: left; }
                .scale-table th { background-color: #e74c3c; color: white; }
                .scale-table tr:nth-child(even) { background-color: #f8f9fa; }
            </style>
        </head>
        <body>
            <h2>Phương pháp Interval TOPSIS</h2>
            
            <h3>1. Tổng quan</h3>
            <p>Interval TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution) là phương pháp xếp hạng các phương án dựa trên khoảng cách đến điểm lý tưởng dương (PIS) và điểm lý tưởng âm (NIS).</p>
            <p>Phương pháp này sử dụng <b>khoảng số (interval numbers)</b> để xử lý tính không chắc chắn trong đánh giá.</p>
            
            <h3>2. Thang đo ngôn ngữ</h3>
            <table class="scale-table">
                <tr>
                    <th>Mức đánh giá</th>
                    <th>Khoảng số [Lower, Upper]</th>
                </tr>
                <tr><td>Very Poor (Rất kém)</td><td>[0, 1]</td></tr>
                <tr><td>Poor (Kém)</td><td>[1, 3]</td></tr>
                <tr><td>Fair (Trung bình)</td><td>[3, 5]</td></tr>
                <tr><td>Good (Tốt)</td><td>[5, 7]</td></tr>
                <tr><td>Very Good (Rất tốt)</td><td>[7, 9]</td></tr>
                <tr><td>Excellent (Xuất sắc)</td><td>[9, 10]</td></tr>
            </table>
            
            <h3>3. Các bước tính toán</h3>
            
            <h4>Bước 1: Xây dựng ma trận quyết định khoảng</h4>
            <p>Ma trận D với mỗi phần tử là khoảng số [xᵢⱼ⁻, xᵢⱼ⁺]:</p>
            <div class="formula">
                D = [[x₁₁⁻, x₁₁⁺] ... [x₁ₙ⁻, x₁ₙ⁺]]<br>
                &nbsp;&nbsp;&nbsp;&nbsp;[  ...     ...    ... ]<br>
                &nbsp;&nbsp;&nbsp;&nbsp;[[xₘ₁⁻, xₘ₁⁺] ... [xₘₙ⁻, xₘₙ⁺]]
            </div>
            
            <h4>Bước 2: Tích hợp đánh giá của nhiều chuyên gia</h4>
            <p>Sử dụng trung bình cộng đơn giản:</p>
            <div class="formula">
                x̄ᵢⱼ⁻ = (Σₖ xᵢⱼₖ⁻) / K<br>
                x̄ᵢⱼ⁺ = (Σₖ xᵢⱼₖ⁺) / K
            </div>
            <p>Trong đó K là số lượng chuyên gia.</p>
            
            <h4>Bước 3: Chuẩn hóa ma trận quyết định</h4>
            <p><b>Đối với tiêu chí lợi ích (Benefit):</b></p>
            <div class="formula">
                rᵢⱼ⁻ = xᵢⱼ⁻ / max(xᵢⱼ⁺)<br>
                rᵢⱼ⁺ = xᵢⱼ⁺ / max(xᵢⱼ⁺)
            </div>
            
            <p><b>Đối với tiêu chí chi phí (Cost):</b></p>
            <div class="formula">
                rᵢⱼ⁻ = min(xᵢⱼ⁻) / xᵢⱼ⁺<br>
                rᵢⱼ⁺ = min(xᵢⱼ⁻) / xᵢⱼ⁻
            </div>
            
            <h4>Bước 4: Tính ma trận quyết định có trọng số</h4>
            <p>Nhân ma trận chuẩn hóa với trọng số từ Fuzzy AHP:</p>
            <div class="formula">
                vᵢⱼ⁻ = wⱼ × rᵢⱼ⁻<br>
                vᵢⱼ⁺ = wⱼ × rᵢⱼ⁺
            </div>
            
            <h4>Bước 5: Xác định điểm lý tưởng dương (PIS) và âm (NIS)</h4>
            <div class="formula">
                <b>PIS (A⁺):</b><br>
                A⁺ = {[v₁⁺⁻, v₁⁺⁺], ..., [vₙ⁺⁻, vₙ⁺⁺]}<br>
                Trong đó: [vⱼ⁺⁻, vⱼ⁺⁺] = [max(vᵢⱼ⁻), max(vᵢⱼ⁺)]<br>
                <br>
                <b>NIS (A⁻):</b><br>
                A⁻ = {[v₁⁻⁻, v₁⁻⁺], ..., [vₙ⁻⁻, vₙ⁻⁺]}<br>
                Trong đó: [vⱼ⁻⁻, vⱼ⁻⁺] = [min(vᵢⱼ⁻), min(vᵢⱼ⁺)]
            </div>
            
            <h4>Bước 6: Tính khoảng cách đến PIS và NIS</h4>
            <p>Sử dụng khoảng cách Euclidean cho khoảng số:</p>
            <div class="formula">
                d(A, B) = √[(a⁻ - b⁻)² + (a⁺ - b⁺)²] / √2<br>
                <br>
                <b>Khoảng cách đến PIS:</b><br>
                Dᵢ⁺ = √[Σⱼ d²([vᵢⱼ⁻, vᵢⱼ⁺], [vⱼ⁺⁻, vⱼ⁺⁺])]<br>
                <br>
                <b>Khoảng cách đến NIS:</b><br>
                Dᵢ⁻ = √[Σⱼ d²([vᵢⱼ⁻, vᵢⱼ⁺], [vⱼ⁻⁻, vⱼ⁻⁺])]
            </div>
            
            <h4>Bước 7: Tính điểm tương đối gần (Closeness Coefficient)</h4>
            <div class="formula">
                CCᵢ = Dᵢ⁻ / (Dᵢ⁺ + Dᵢ⁻)
            </div>
            <div class="example">
                <b>Khoảng giá trị:</b> 0 ≤ CCᵢ ≤ 1<br>
                - CCᵢ gần 1: Phương án i gần với điểm lý tưởng dương (tốt)<br>
                - CCᵢ gần 0: Phương án i gần với điểm lý tưởng âm (không tốt)
            </div>
            
            <h4>Bước 8: Xếp hạng các phương án</h4>
            <p>Sắp xếp các phương án theo giá trị CC giảm dần. Phương án có CC cao nhất là tốt nhất.</p>
            
            <h3>4. Tích hợp với Fuzzy AHP</h3>
            <p>Trong phần mềm này:</p>
            <ul>
                <li><b>Fuzzy AHP</b> được sử dụng để tính trọng số của các tiêu chí (wⱼ)</li>
                <li><b>Interval TOPSIS</b> sử dụng trọng số này để xếp hạng các nhà cung cấp</li>
            </ul>
            <div class="example">
                <b>Quy trình tổng quát:</b><br>
                1. Sử dụng Fuzzy AHP để xác định trọng số tiêu chí<br>
                2. Sử dụng Interval TOPSIS để đánh giá và xếp hạng nhà cung cấp<br>
                3. Kết quả cuối cùng là danh sách xếp hạng dựa trên CC
            </div>
            
        </body>
        </html>
        """
        
        browser.setHtml(html_content)
        layout.addWidget(browser)
        widget.setLayout(layout)
        
        return widget
