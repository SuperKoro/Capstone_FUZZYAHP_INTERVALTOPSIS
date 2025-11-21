# ✅ Disable Mouse Wheel Scrolling in Dropdowns

## 🎯 Vấn Đề
Người dùng có thể vô tình thay đổi giá trị trong dropdown (combobox) khi cuộn chuột trên trang, gây ra sai sót trong việc nhập liệu.

## ✅ Giải Pháp
Tạo custom `NoScrollComboBox` class để **tắt hoàn toàn** chức năng scroll wheel trên các dropdown quan trọng.

---

## 📝 Changes Made

### 1. Created `NoScrollComboBox` Class

Custom QComboBox subclass được thêm vào **3 files**:

#### **File: `gui/ahp_tab.py`**
```python
class NoScrollComboBox(QComboBox):
    """Custom QComboBox that disables mouse wheel scrolling"""
    
    def wheelEvent(self, event):
        """Ignore wheel events to prevent accidental selection changes"""
        event.ignore()
```

**Áp dụng cho:**
- ✅ **Pairwise Comparison Scale dropdown** (dòng 731)
  - Người dùng chọn importance scale (1-9)
  - **Rất quan trọng** vì có 17 options, dễ bị thay đổi nhầm

#### **File: `gui/topsis_tab.py`**
```python
class NoScrollComboBox(QComboBox):
    """Custom QComboBox that disables mouse wheel scrolling"""
    
    def wheelEvent(self, event):
        """Ignore wheel events to prevent accidental selection changes"""
        event.ignore()
```

**Áp dụng cho:**
- ✅ **Performance Rating dropdown** (dòng 157)
  - Người dùng chọn linguistic ratings: Very Poor, Poor, Fair, Good, Very Good, Excellent
  - **Quan trọng** vì ratings ảnh hưởng trực tiếp đến kết quả TOPSIS

#### **File: `gui/criteria_tree.py`**
```python
class NoScrollComboBox(QComboBox):
    """Custom QComboBox that disables mouse wheel scrolling"""
    
    def wheelEvent(self, event):
        """Ignore wheel events to prevent accidental selection changes"""
        event.ignore()
```

**Áp dụng cho:**
- ✅ **Criterion Type dropdown** (Add Criterion dialog - dòng 136)
- ✅ **Criterion Type dropdown** (Edit Criterion dialog - dòng 194)
  - Chọn Benefit/Cost cho tiêu chí
  - **Quan trọng** vì quyết định tối đa hay tối thiểu trong TOPSIS

---

## 🔍 Các Dropdown KHÔNG Bị Thay Đổi

### Expert Selection Dropdown
**File:** `gui/ahp_tab.py` (dòng 135) và `gui/topsis_tab.py` (dòng 50)

**Lý do giữ nguyên scroll wheel:**
- Ít options (thường 1-5 experts)
- Người dùng thường chủ động chọn expert
- Không phải data entry, chỉ là selection để filter view

---

## 🎨 User Experience Improvements

### Trước khi fix:
❌ Người dùng đang nhập pairwise comparison  
❌ Vô tình cuộn chuột → giá trị thay đổi từ "3: Moderately more important" → "5: Strongly more important"  
❌ Không nhận ra → Save sai data  

### Sau khi fix:
✅ Người dùng cuộn chuột → **dropdown KHÔNG thay đổi**  
✅ Phải **click vào dropdown** và chọn giá trị mới  
✅ Tránh sai sót do vô tình cuộn chuột  

---

## 🧪 Testing Guide

### Test 1: Pairwise Comparison
1. Mở project, vào **AHP Evaluation** tab
2. Chọn một criterion group để nhập comparisons
3. Hover chuột lên dropdown "Importance Scale"
4. Cuộn chuột lên/xuống
5. **Kết quả mong đợi:** Giá trị KHÔNG thay đổi

### Test 2: TOPSIS Rating
1. Vào **TOPSIS Rating** tab
2. Hover chuột lên dropdown rating (Very Poor, Poor, Fair...)
3. Cuộn chuột lên/xuống
4. **Kết quả mong đợi:** Giá trị KHÔNG thay đổi

### Test 3: Criterion Type
1. Vào **Project Setup** tab
2. Click "Add" để thêm criterion
3. Trong dialog, hover chuột lên dropdown "Type" (Benefit/Cost)
4. Cuộn chuột lên/xuống
5. **Kết quả mong đợi:** Giá trị KHÔNG thay đổi

### Test 4: Expert Selection (Should Still Work)
1. Vào **AHP Evaluation** tab
2. Hover chuột lên dropdown "Select Expert"
3. Cuộn chuột lên/xuống
4. **Kết quả mong đợi:** Vẫn có thể scroll (vì không disable)

---

## 💡 Technical Details

### How `wheelEvent` Override Works

```python
def wheelEvent(self, event):
    """Ignore wheel events to prevent accidental selection changes"""
    event.ignore()
```

- **`event.ignore()`**: Tells Qt to NOT handle this wheel event
- Event propagates to parent widget (allows page scrolling)
- Dropdown value remains unchanged
- User must **click to open dropdown** and select value manually

### Alternative Solutions (NOT Used)

#### Option 1: `setFocusPolicy(Qt.FocusPolicy.StrongFocus)`
- ❌ Chỉ prevent wheel scroll khi widget KHÔNG có focus
- ❌ Vẫn có thể scroll wheel nếu đã focus

#### Option 2: Event Filter
- ❌ Phức tạp hơn, cần install filter cho mỗi combobox
- ❌ Code không clean

#### Option 3: ✅ **Subclass QComboBox (CHOSEN)**
- ✅ Clean và reusable
- ✅ Override `wheelEvent` directly
- ✅ Easy to maintain

---

## 📁 Files Modified

1. [`gui/ahp_tab.py`](file:///G:/anti/supplier_selection_app/gui/ahp_tab.py#L23-L30) - Added NoScrollComboBox class, used in line 731
2. [`gui/topsis_tab.py`](file:///G:/anti/supplier_selection_app/gui/topsis_tab.py#L15-L22) - Added NoScrollComboBox class, used in line 157
3. [`gui/criteria_tree.py`](file:///G:/anti/supplier_selection_app/gui/criteria_tree.py#L12-L19) - Added NoScrollComboBox class, used in lines 136, 194

---

## ✅ Summary

**Đã disable mouse wheel scrolling cho ALL data-entry dropdowns:**
- ✅ Pairwise Comparison importance scale
- ✅ TOPSIS performance ratings  
- ✅ Criterion type selection (Benefit/Cost)

**Giữ nguyên scroll wheel cho:**
- Expert selection dropdowns (less critical, fewer options)

**Benefit:**
- 🎯 Prevent accidental data entry errors
- 🎯 Force intentional selection via click
- 🎯 Better user experience for precision tasks
