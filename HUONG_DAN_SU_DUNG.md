# Hướng Dẫn Sử Dụng - Ứng Dụng Lựa Chọn Nhà Cung Cấp

## 📋 Mục Lục
- [Giới Thiệu](#giới-thiệu)
- [Tính Năng Chính](#tính-năng-chính)
- [Yêu Cầu Hệ Thống](#yêu-cầu-hệ-thống)
- [Cài Đặt](#cài-đặt)
- [Hướng Dẫn Sử Dụng Chi Tiết](#hướng-dẫn-sử-dụng-chi-tiết)
- [Phương Pháp MCDM](#phương-pháp-mcdm)
- [Câu Hỏi Thường Gặp](#câu-hỏi-thường-gặp)
- [Khắc Phục Sự Cố](#khắc-phục-sự-cố)

---

## 🎯 Giới Thiệu

Ứng dụng **Lựa Chọn Nhà Cung Cấp** là một công cụ hỗ trợ ra quyết định đa tiêu chí (Multi-Criteria Decision Making - MCDM) được thiết kế để giúp doanh nghiệp đánh giá và xếp hạng các nhà cung cấp một cách khoa học và hiệu quả.

### Ứng dụng kết hợp hai phương pháp:
1. **Fuzzy AHP (Analytic Hierarchy Process)** - Quy trình phân tích thứ bậc mờ
   - Dùng để xác định trọng số quan trọng của các tiêu chí đánh giá
   - Hỗ trợ đánh giá từ nhiều chuyên gia

2. **Interval TOPSIS** - Kỹ thuật ưu tiên theo độ tương đồng với giải pháp lý tưởng
   - Dùng để xếp hạng các nhà cung cấp dựa trên các tiêu chí đã được gán trọng số
   - Sử dụng khoảng mờ để xử lý sự không chắc chắn trong đánh giá

### 🎓 Ứng dụng phù hợp cho:
- Các doanh nghiệp cần lựa chọn nhà cung cấp nguyên vật liệu
- Phòng ban mua hàng cần đánh giá nhiều nhà cung cấp
- Nghiên cứu học thuật về ra quyết định đa tiêu chí
- Bất kỳ tình huống nào cần đánh giá và xếp hạng các phương án theo nhiều tiêu chí

---

## ✨ Tính Năng Chính

### 🔢 Module Fuzzy AHP
- **Thang đo ngôn ngữ 17 mức độ**: Từ -9 đến +9 cho so sánh cặp đôi
- **Hai chế độ nhập liệu**:
  - Nhập trực tiếp: Nhập so sánh ngay trên ứng dụng
  - Import Excel: Tạo mẫu, điền offline, và import vào
- **Tổng hợp đánh giá**: Sử dụng trung bình hình học mờ để tổng hợp ý kiến từ nhiều chuyên gia
- **Kiểm tra tính nhất quán**: Tính toán tự động chỉ số CR với màu sắc phản hồi

### 📊 Module Interval TOPSIS
- **Thang đánh giá ngôn ngữ**: 7 mức độ từ "Very Poor" đến "Very Good"
- **Tính toán khoảng**: Sử dụng số học khoảng để xử lý độ không chắc chắn
- **Xếp hạng tự động**: Tính toán hệ số gần gũi và xếp hạng cuối cùng

### 📈 Trực Quan Hóa & Xuất Dữ Liệu
- **Biểu đồ tương tác**: Biểu đồ cột hiển thị kết quả xếp hạng
- **Xuất Excel**: Báo cáo chi tiết với tất cả tính toán và kết quả
- **Mã màu kết quả**: Đánh dấu trực quan top 3 nhà cung cấp (vàng 🥇, bạc 🥈, đồng 🥉)

### 💾 Quản Lý Dự Án
- **Lưu trữ cục bộ**: Tất cả dữ liệu được lưu trong file .mcdm (SQLite database)
- **Làm việc offline**: Không cần kết nối internet
- **Quản lý kịch bản**: Hỗ trợ nhiều kịch bản đánh giá trong một dự án
- **Phân tích độ nhạy**: Kiểm tra sự ổn định của kết quả khi thay đổi trọng số

---

## 💻 Yêu Cầu Hệ Thống

### Phần Mềm
- **Python**: Phiên bản 3.10 trở lên
- **Hệ điều hành**: Windows 10/11 (khuyến nghị)
- **RAM**: Tối thiểu 4GB
- **Dung lượng ổ cứng**: 200MB cho ứng dụng và dependencies

### Thư Viện Python Cần Thiết
```
PyQt6>=6.4.0
numpy>=1.24.0
pandas>=2.0.0
openpyxl>=3.1.0
matplotlib>=3.7.0
```

---

## 📥 Cài Đặt

### Bước 1: Chuẩn Bị Môi Trường

1. **Kiểm tra Python đã cài đặt chưa:**
   ```bash
   python --version
   ```
   Nếu chưa có, tải Python từ [python.org](https://www.python.org/downloads/)

2. **Di chuyển đến thư mục ứng dụng:**
   ```bash
   cd g:\anti\supplier_selection_app
   ```

### Bước 2: Cài Đặt Dependencies

```bash
pip install -r requirements.txt
```

### Bước 3: Chạy Ứng Dụng

```bash
python main.py
```

Ứng dụng sẽ mở ra với giao diện người dùng đồ họa (GUI).

---

## 📖 Hướng Dẫn Sử Dụng Chi Tiết

### 🆕 Bước 1: Tạo Dự Án Mới

1. Nhấn **File → New Project** (hoặc `Ctrl+N`)
2. Nhập tên dự án (ví dụ: "Đánh Giá Nhà Cung Cấp Q1-2025")
3. Chọn vị trí lưu file .mcdm
4. Nhấn **Save**

> 💡 **Mẹo**: File .mcdm là một database SQLite chứa toàn bộ dữ liệu dự án của bạn. Hãy sao lưu file này thường xuyên!

### 📝 Bước 2: Thiết Lập Tiêu Chí và Phương Án

#### 2.1. Thêm Tiêu Chí Đánh Giá
1. Chuyển đến tab **"Project Setup"** (Thiết lập dự án)
2. Nhấn **"Add Criterion"** (Thêm tiêu chí)
3. Nhập thông tin tiêu chí:
   - **Tên tiêu chí**: Ví dụ: "Giá cả", "Chất lượng", "Thời gian giao hàng"
   - **Loại tiêu chí**: 
     - **Benefit** (Lợi ích): Giá trị càng cao càng tốt (ví dụ: Chất lượng)
     - **Cost** (Chi phí): Giá trị càng thấp càng tốt (ví dụ: Giá cả, Thời gian giao)
4. Nhấn **Save** và lặp lại cho các tiêu chí khác

> ⚠️ **Lưu ý**: Cần tối thiểu 2 tiêu chí để thực hiện đánh giá

#### 2.2. Thêm Phương Án (Nhà Cung Cấp)
1. Vẫn trong tab **"Project Setup"**
2. Nhấn **"Add Alternative"** (Thêm phương án)
3. Nhập:
   - **Tên nhà cung cấp**: Ví dụ: "Công ty ABC", "Công ty XYZ"
   - **Mô tả**: Thông tin chi tiết (tùy chọn)
4. Lặp lại cho tất cả nhà cung cấp cần đánh giá

> ⚠️ **Lưu ý**: Cần tối thiểu 2 phương án để thực hiện xếp hạng

### ⚖️ Bước 3: Đánh Giá Fuzzy AHP (Tính Trọng Số)

#### 3.1. Thêm Chuyên Gia
1. Chuyển đến tab **"Fuzzy AHP Evaluation"**
2. Nhấn **"Add Expert"** (Thêm chuyên gia)
3. Nhập tên chuyên gia (ví dụ: "Nguyễn Văn A - Trưởng phòng Mua hàng")
4. Lặp lại nếu có nhiều chuyên gia đánh giá

#### 3.2. Chọn Phương Thức Nhập Liệu

##### **Phương Thức A: Nhập Trực Tiếp**
1. Chọn chuyên gia từ dropdown
2. Với mỗi cặp tiêu chí, chọn mức độ quan trọng từ -9 đến +9:
   - **Số dương (+)**: Tiêu chí bên trái quan trọng hơn
   - **Số âm (-)**: Tiêu chí bên phải quan trọng hơn
   - **1**: Hai tiêu chí có tầm quan trọng ngang nhau
3. Nhấn **"Save Comparisons"** (Lưu so sánh)

##### **Phương Thức B: Import Excel**
1. Chọn chuyên gia từ dropdown
2. Nhấn **"Generate Excel Template"** (Tạo mẫu Excel)
3. Mở file Excel được tạo ra
4. Điền giá trị so sánh (-9 đến +9) vào các ô tương ứng
5. Lưu file Excel
6. Quay lại ứng dụng, nhấn **"Import Completed Excel"**
7. Chọn file Excel đã điền

> 💡 **Mẹo**: Import Excel rất hữu ích khi có nhiều tiêu chí hoặc cần làm việc offline

#### 3.3. Tính Toán Trọng Số
1. Sau khi nhập đủ so sánh từ tất cả chuyên gia
2. Nhấn **"Calculate AHP Weights"** (Tính trọng số AHP)
3. Kiểm tra **Consistency Ratio (CR)**:
   - **CR < 0.1**: ✅ Chấp nhận được (màu xanh)
   - **CR ≥ 0.1**: ⚠️ Không nhất quán, cần xem xét lại (màu đỏ)

> 📊 **Giải thích CR**: Chỉ số CR đo lường tính nhất quán trong đánh giá của bạn. Nếu CR cao, có thể bạn đã mâu thuẫn trong so sánh (ví dụ: A quan trọng hơn B, B quan trọng hơn C, nhưng C lại quan trọng hơn A).

1. Chuyển đến tab **"TOPSIS Rating"**
2. Bạn sẽ thấy ma trận: Hàng là nhà cung cấp, cột là tiêu chí
3. Với mỗi ô, chọn mức độ đánh giá từ dropdown:
   - **Very Good** (Rất tốt): 9-10/10
   - **Good** (Tốt): 6-9/10
   - **Medium Good** (Khá): 5-6/10
   - **Fair** (Trung bình): 4-5/10
   - **Medium Poor** (Hơi kém): 3-4/10
   - **Poor** (Kém): 1-3/10
   - **Very Poor** (Rất kém): 0-1/10
4. Sau khi điền đủ, nhấn **"Calculate TOPSIS Ranking"****

> 💡 **Mẹo**: Đánh giá nên dựa trên dữ liệu thực tế (hiệu suất quá khứ, báo cáo kiểm định, đánh giá khách hàng, v.v.)

### 🏆 Bước 5: Xem Kết Quả

1. Tab **"Results"** sẽ tự động mở sau khi tính toán
2. Bảng kết quả hiển thị:
   - **Rank**: Thứ hạng (1, 2, 3, ...)
   - **Alternative**: Tên nhà cung cấp
   - **Closeness Coefficient**: Hệ số gần gũi (0-1, càng cao càng tốt)
   - **Distance to Ideal**: Khoảng cách đến giải pháp lý tưởng
   - **Distance to Anti-Ideal**: Khoảng cách đến giải pháp tệ nhất
3. Top 3 được đánh dấu màu:
   - 🥇 **Vị trí 1**: Màu vàng
   - 🥈 **Vị trí 2**: Màu xám
   - 🥉 **Vị trí 3**: Màu hồng
4. Xem biểu đồ cột để so sánh trực quan
5. Nhấn **"Export Results to Excel"** để xuất báo cáo chi tiết

---

## 📐 Phương Pháp MCDM

### Fuzzy AHP - Quy Trình Phân Tích Thứ Bậc Mờ

#### Nguyên Lý
Fuzzy AHP mở rộng phương pháp AHP truyền thống bằng cách sử dụng **số mờ tam giác (Triangular Fuzzy Numbers - TFN)** để xử lý sự không chắc chắn trong đánh giá của con người.

#### Quy Trình
1. **So sánh cặp đôi**: Chuyên gia so sánh từng cặp tiêu chí
2. **Chuyển đổi fuzzy**: Giá trị ngôn ngữ → Số mờ tam giác
3. **Tổng hợp**: Sử dụng trung bình hình học mờ để tổng hợp đánh giá từ nhiều chuyên gia
4. **Defuzzification**: Chuyển số mờ thành số rõ (crisp) bằng phương pháp Center of Area
5. **Chuẩn hóa**: Tính trọng số cuối cùng (tổng = 1)

#### Thang Đo 17 Mức
| Giá Trị | Ý Nghĩa | Khi Nào Sử Dụng |
|---------|---------|------------------|
| **9** | Tuyệt đối quan trọng hơn | A vượt trội hoàn toàn so với B |
| **7** | Rất rất quan trọng hơn | A quan trọng hơn rất nhiều so với B |
| **5** | Rất quan trọng hơn | A quan trọng hơn đáng kể so với B |
| **3** | Vừa phải quan trọng hơn | A hơi quan trọng hơn B |
| **1** | Ngang nhau | A và B có tầm quan trọng như nhau |
| **-3** | Vừa phải kém quan trọng hơn | B hơi quan trọng hơn A |
| **-5** | Rất kém quan trọng hơn | B quan trọng hơn đáng kể so với A |
| **-9** | Tuyệt đối kém quan trọng hơn | B vượt trội hoàn toàn so với A |

> 💡 **Mẹo**: Các giá trị 2, 4, 6, 8 và giá trị âm tương ứng được dùng cho các mức độ trung gian

### Interval TOPSIS - Kỹ Thuật Ưu Tiên

#### Nguyên Lý
TOPSIS xếp hạng các phương án dựa trên nguyên tắc: Phương án tốt nhất nên **gần với giải pháp lý tưởng** và **xa với giải pháp tệ nhất**.

#### Quy Trình
1. **Chuẩn hóa ma trận**: Đưa các tiêu chí về cùng thang đo
2. **Tính ma trận có trọng số**: Nhân với trọng số từ AHP
3. **Xác định giải pháp lý tưởng** (A+): Giá trị tốt nhất cho mỗi tiêu chí
4. **Xác định giải pháp tệ nhất** (A-): Giá trị tệ nhất cho mỗi tiêu chí
5. **Tính khoảng cách**: 
   - d+: Khoảng cách đến A+
   - d-: Khoảng cách đến A-
6. **Tính hệ số gần gũi**: CC = d- / (d+ + d-)
7. **Xếp hạng**: Phương án có CC cao nhất được xếp hạng 1

#### Thang Đánh Giá Linguistic
| Mức Độ | Khoảng Mờ | Ý Nghĩa |
|--------|-----------|---------|  
| **Very Good** | [9, 10] | Rất tốt, xuất sắc |
| **Good** | [6, 9] | Tốt, đạt yêu cầu |
| **Medium Good** | [5, 6] | Khá, trên mức trung bình |
| **Fair** | [4, 5] | Trung bình, chấp nhận được |
| **Medium Poor** | [3, 4] | Hơi kém, dưới trung bình |
| **Poor** | [1, 3] | Kém, dưới mức mong đợi |
| **Very Poor** | [0, 1] | Rất kém, không chấp nhận được |

---

## 🔍 Tính Năng Nâng Cao

### 📊 Phân Tích Độ Nhạy (Sensitivity Analysis)

Phân tích độ nhạy giúp bạn hiểu **mức độ ổn định** của kết quả xếp hạng khi thay đổi trọng số tiêu chí.

#### Cách Sử Dụng:
1. Chuyển đến tab **"Sensitivity Analysis"**
2. Chọn tiêu chí muốn phân tích
3. Nhấn **"Run Sensitivity Analysis"**
4. Xem biểu đồ thay đổi thứ hạng

#### Giải Thích Kết Quả:
- **Đường thẳng ổn định**: Kết quả ít bị ảnh hưởng bởi thay đổi trọng số → Kết luận chắc chắn
- **Đường giao nhau nhiều**: Kết quả nhạy cảm với trọng số → Cần xem xét kỹ hơn

### 🔄 Quản Lý Kịch Bản (Scenario Management)

Bạn có thể tạo nhiều kịch bản đánh giá khác nhau trong cùng một dự án.

#### Ví Dụ Sử Dụng:
- **Kịch bản 1**: Tập trung vào giá cả (cho sản phẩm cơ bản)
- **Kịch bản 2**: Tập trung vào chất lượng (cho sản phẩm cao cấp)
- **Kịch bản 3**: Tập trung vào thời gian giao hàng (cho đơn hàng khẩn)

#### Cách Tạo Kịch Bản Mới:
1. Nhấn **"File → New Scenario"**
2. Nhập tên kịch bản
3. Thiết lập AHP và TOPSIS riêng cho kịch bản này

---

## ❓ Câu Hỏi Thường Gặp (FAQ)

### Q1: File .mcdm là gì?
**A**: Đây là file cơ sở dữ liệu SQLite chứa toàn bộ dữ liệu dự án của bạn (tiêu chí, phương án, đánh giá, kết quả). Bạn có thể mở file này bằng bất kỳ trình đọc SQLite nào hoặc bằng ứng dụng này.

### Q2: Tôi cần bao nhiêu chuyên gia?
**A**: Tối thiểu 1 chuyên gia, nhưng khuyến nghị 2-3 chuyên gia để kết quả đáng tin cậy hơn. Nhiều chuyên gia giúp giảm thiểu sự thiên vị cá nhân.

### Q3: CR cao hơn 0.1 có nghĩa là gì?
**A**: CR (Consistency Ratio) cao cho thấy có mâu thuẫn trong đánh giá của bạn. Ví dụ: Bạn nói A quan trọng hơn B, B quan trọng hơn C, nhưng lại nói C quan trọng hơn A. Hãy xem lại các so sánh.

### Q4: Tôi có thể thay đổi tiêu chí sau khi đã đánh giá AHP không?
**A**: Có, nhưng bạn sẽ cần phải thực hiện lại đánh giá AHP và TOPSIS. Ứng dụng sẽ cảnh báo nếu dữ liệu cũ không còn phù hợp.

### Q5: Làm sao để sao lưu dữ liệu?
**A**: Chỉ cần copy file .mcdm sang vị trí an toàn (USB, cloud storage, v.v.). File này chứa tất cả dữ liệu của bạn.

### Q6: Ứng dụng có hoạt động offline không?
**A**: Có! Ứng dụng hoạt động hoàn toàn offline, không cần kết nối internet.

### Q7: Tôi có thể so sánh nhiều nhóm nhà cung cấp không?
**A**: Có, bạn có thể tạo nhiều dự án khác nhau (file .mcdm) hoặc sử dụng tính năng Scenario để tạo nhiều kịch bản trong cùng một dự án.

---

## 🛠️ Khắc Phục Sự Cố

### Sự Cố 1: Ứng Dụng Không Khởi Động

**Triệu chứng**: Nhấn `python main.py` nhưng không có gì xảy ra hoặc báo lỗi

**Giải pháp**:
```bash
# Kiểm tra phiên bản Python
python --version  # Phải >= 3.10

# Cài đặt lại dependencies
pip install --upgrade -r requirements.txt

# Thử chạy với python3
python3 main.py
```

### Sự Cố 2: CR Quá Cao (≥ 0.1)

**Triệu chứng**: Consistency Ratio hiển thị màu đỏ

**Giải pháp**:
1. Xem lại bảng so sánh cặp đôi
2. Tìm các so sánh mâu thuẫn (ví dụ: A>>B, B>>C nhưng C>>A)
3. Điều chỉnh lại các so sánh để hợp lý hơn
4. Nếu vẫn cao, có thể bạn cần chia nhỏ tiêu chí thành các nhóm con

### Sự Cố 3: Không Thể Tính TOPSIS

**Triệu chứng**: Nút "Calculate TOPSIS" bị vô hiệu hóa hoặc báo lỗi

**Nguyên nhân & Giải pháp**:
- ✅ Đã tính AHP Weights chưa? → Phải tính AHP trước
- ✅ Đã điền đủ tất cả ô rating chưa? → Kiểm tra lại ma trận
- ✅ Có tối thiểu 2 phương án và 2 tiêu chí không? → Thêm nếu thiếu

### Sự Cố 4: Import Excel Thất Bại

**Triệu chứng**: Nhấn Import nhưng báo lỗi hoặc không load được

**Giải pháp**:
1. Kiểm tra file Excel có đúng format không (dùng template được tạo ra)
2. Không thay đổi tên cột hoặc header trong Excel
3. Chỉ điền giá trị từ -9 đến 9, không có text hay ký tự đặc biệt
4. Lưu file Excel (Ctrl+S) trước khi import
5. Đảm bảo file Excel không đang mở bởi chương trình khác

### Sự Cố 5: File .mcdm Bị Lỗi

**Triệu chứng**: Không mở được file dự án, báo "database corrupted"

**Giải pháp**:
```bash
# Chạy migration tool
python migrate_database.py your_project.mcdm

# Hoặc dùng run_migration
python run_migration.py
```

### Sự Cố 6: Thiếu Module Python

**Triệu chứng**: `ModuleNotFoundError: No module named 'PyQt6'` hoặc tương tự

**Giải pháp**:
```bash
# Cài đặt module thiếu
pip install PyQt6 numpy pandas openpyxl matplotlib

# Hoặc cài tất cả từ requirements
pip install -r requirements.txt
```

---

## 📁 Cấu Trúc Thư Mục

```
supplier_selection_app/
│
├── main.py                          # Điểm khởi động ứng dụng
├── requirements.txt                 # Danh sách dependencies
│
├── database/                        # Lớp cơ sở dữ liệu SQLite
│   ├── schema.py                   # Định nghĩa schema database
│   ├── manager.py                  # Các thao tác CRUD
│   └── database_migration.py       # Migration tool
│
├── algorithms/                      # Thuật toán MCDM
│   ├── fuzzy_ahp.py               # Implementation Fuzzy AHP
│   ├── interval_topsis.py         # Implementation Interval TOPSIS
│   ├── hierarchical_ahp.py        # AHP phân cấp
│   └── sensitivity_analysis.py    # Phân tích độ nhạy
│
├── gui/                            # Giao diện người dùng PyQt6
│   ├── main_window.py             # Cửa sổ chính
│   ├── project_tab.py             # Tab thiết lập dự án
│   ├── ahp_tab.py                 # Tab đánh giá AHP
│   ├── topsis_tab.py              # Tab đánh giá TOPSIS
│   ├── results_tab.py             # Tab hiển thị kết quả
│   ├── sensitivity_tab.py         # Tab phân tích độ nhạy
│   └── styles.py                  # Stylesheet cho UI
│
├── utils/                          # Tiện ích
│   ├── excel_handler.py           # Xử lý import/export Excel
│   ├── validators.py              # Kiểm tra dữ liệu đầu vào
│   └── scenario_manager.py        # Quản lý kịch bản
│
├── commands/                       # Command handlers
│   ├── ahp_commands.py            # Commands cho AHP
│   └── topsis_commands.py         # Commands cho TOPSIS
│
└── resources/                      # Tài nguyên (icons, images)
```

---

## 💡 Mẹo Sử Dụng Hiệu Quả

### 1. Chuẩn Bị Trước
- Liệt kê rõ ràng các tiêu chí quan trọng
- Thu thập dữ liệu về hiệu suất các nhà cung cấp
- Xác định ai là chuyên gia phù hợp (người có kinh nghiệm, hiểu rõ yêu cầu)

### 2. Nhất Quán Trong Đánh Giá
- Duy trì logic nhất quán khi so sánh
- Sử dụng dữ liệu thực tế thay vì cảm tính
- Tham khảo ý kiến nhiều người

### 3. Lưu Trữ & Backup
- Sử dụng `Ctrl+S` thường xuyên
- Backup file .mcdm định kỳ
- Đặt tên file rõ ràng (kèm ngày tháng)

### 4. Kiểm Tra Kết Quả
- Chạy phân tích độ nhạy để xem mức độ ổn định
- So sánh với đánh giá định tính
- Thử nhiều kịch bản khác nhau

### 5. Tài Liệu Hóa
- Xuất kết quả ra Excel để lưu trữ
- Ghi chú lý do đánh giá trong mô tả
- Lưu lại các quyết định quan trọng

---

## 📞 Hỗ Trợ

### Tài Liệu Tham Khảo
- [QUICK_START.md](QUICK_START.md) - Hướng dẫn nhanh bằng tiếng Anh
- [README.md](README.md) - Tài liệu kỹ thuật chi tiết
- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - Hướng dẫn migration database

### Lỗi và Góp Ý
Nếu bạn gặp lỗi hoặc có góp ý cải thiện, vui lòng ghi lại:
- Mô tả chi tiết lỗi
- Các bước tái hiện lỗi
- Screenshots nếu có

---

## 📝 Ví Dụ Thực Tế

### Kịch Bản: Chọn Nhà Cung Cấp Nguyên Liệu Thép

#### Bước 1: Định Nghĩa Tiêu Chí
| Tiêu Chí | Loại | Lý Do |
|----------|------|-------|
| Giá cả | Cost | Giảm chi phí sản xuất |
| Chất lượng sản phẩm | Benefit | Đảm bảo sản phẩm cuối |
| Thời gian giao hàng | Cost | Đáp ứng tiến độ |
| Dịch vụ hậu mãi | Benefit | Giải quyết sự cố nhanh |
| Uy tín công ty | Benefit | Đảm bảo lâu dài |

#### Bước 2: Danh Sách Nhà Cung Cấp
- Công ty Thép Việt (NCC A)
- Công ty Thép Á Châu (NCC B)
- Công ty Thép Đông Nam (NCC C)
- Công ty Thép Quốc Tế (NCC D)

#### Bước 3: So Sánh AHP (Ví dụ từ chuyên gia)
- Chất lượng vs Giá cả: **+3** (Chất lượng quan trọng hơn)
- Chất lượng vs Thời gian: **+5** (Chất lượng rất quan trọng hơn
)
- Giá cả vs Thời gian: **+1** (Ngang nhau)
- ...

#### Bước 4: Kết Quả Trọng Số (Sau tính toán)
- Chất lượng: 35%
- Giá cả: 25%
- Thời gian giao: 20%
- Dịch vụ: 12%
- Uy tín: 8%

#### Bước 5: Đánh Giá TOPSIS
| NCC | Giá | Chất lượng | Thời gian | Dịch vụ | Uy tín |
|-----|-----|------------|-----------|---------|--------|
| A | Fair | Very Good | Good | Good | Very Good |
| B | Very Good | Good | Fair | Fair | Good |
| C | Good | Very Good | Good | Medium Good | Very Good |
| D | Fair | Good | Medium Good | Very Good | Fair |

#### Bước 6: Kết Quả Xếp Hạng
1. 🥇 **NCC C** - CC: 0.78 (Cân bằng tốt, vượt trội về chất lượng)
2. 🥈 **NCC A** - CC: 0.65 (Chất lượng tốt, uy tín cao)
3. 🥉 **NCC D** - CC: 0.58 (Tốt về thời gian và dịch vụ)
4. **NCC B** - CC: 0.52 (Giá tốt nhưng yếu các tiêu chí khác)

---

## 🎓 Thuật Ngữ MCDM

| Thuật Ngữ | Tiếng Việt | Giải Thích |
|-----------|------------|------------|
| **MCDM** | Ra quyết định đa tiêu chí | Phương pháp đánh giá dựa trên nhiều tiêu chí |
| **AHP** | Quy trình phân tích thứ bậc | So sánh cặp đôi để tính trọng số |
| **Fuzzy** | Mờ | Xử lý sự không chắc chắn, mơ hồ |
| **TOPSIS** | Kỹ thuật ưu tiên theo độ tương đồng | Xếp hạng dựa trên khoảng cách |
| **CR** | Tỷ lệ nhất quán | Đo độ nhất quán trong đánh giá |
| **TFN** | Số mờ tam giác | (a, b, c) đại diện giá trị mờ |
| **Criterion** | Tiêu chí | Yếu tố đánh giá |
| **Alternative** | Phương án | Lựa chọn cần xếp hạng |
| **Weight** | Trọng số | Mức độ quan trọng (0-1) |
| **Closeness Coefficient** | Hệ số gần gũi | Điểm số cuối cùng (0-1) |

---

## 🚀 Lời Kết

Ứng dụng **Lựa Chọn Nhà Cung Cấp** là công cụ mạnh mẽ giúp bạn đưa ra quyết định khoa học và có căn cứ. Bằng cách kết hợp Fuzzy AHP và Interval TOPSIS, bạn có thể:

✅ Đánh giá khách quan nhiều nhà cung cấp  
✅ Cân nhắc nhiều tiêu chí quan trọng  
✅ Xử lý sự không chắc chắn trong đánh giá  
✅ Tài liệu hóa quy trình quyết định  
✅ So sánh và phân tích nhiều kịch bản  

Chúc bạn sử dụng ứng dụng hiệu quả! 🎯

---

**Phiên bản**: 1.0  
**Cập nhật lần cuối**: Tháng 12, 2025  
**Tác giả**: MCDM Solutions Team
