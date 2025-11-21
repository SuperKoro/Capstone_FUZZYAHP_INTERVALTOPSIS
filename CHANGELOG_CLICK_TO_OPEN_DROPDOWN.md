# ✅ Click Anywhere in Row to Open Dropdown

## 🎯 Feature Request
Người dùng muốn click vào **bất kỳ ô nào** trong row của Pairwise Comparison table (Criterion 1, Criterion 2, hoặc Importance Scale) thì dropdown sẽ tự động mở, không chỉ giới hạn ở ô cuối cùng.

## 📸 Before & After

### ❌ Before:
- Chỉ click vào ô "Importance Scale" (cột 3) mới mở được dropdown
- Click vào "Criterion 1" hoặc "Criterion 2" → không có gì xảy ra

### ✅ After:
- Click vào **bất kỳ ô nào** trong row → dropdown tự động mở
- UX tốt hơn, không cần phải chính xác click vào ô dropdown

---

## 🔧 Implementation

### 1. Added Click Event Handler

**File:** [`gui/ahp_tab.py`](file:///G:/anti/supplier_selection_app/gui/ahp_tab.py#L149)

```python
self.comparison_table = QTableWidget()
self.comparison_table.itemClicked.connect(self.on_comparison_cell_clicked)
comp_layout.addWidget(self.comparison_table)
```

**Explanation:**
- `itemClicked` signal được trigger khi user click vào bất kỳ cell nào
- Connect đến method `on_comparison_cell_clicked`

### 2. Created Click Handler Method

**File:** [`gui/ahp_tab.py`](file:///G:/anti/supplier_selection_app/gui/ahp_tab.py#L615-L627)

```python
def on_comparison_cell_clicked(self, item):
    """Handle click on any cell in comparison table - open dropdown for that row"""
    if item is None:
        return
    
    row = item.row()
    # Get the combobox widget in column 2 (Importance Scale)
    combo_widget = self.comparison_table.cellWidget(row, 2)
    
    if combo_widget:
        # Set focus and show dropdown
        combo_widget.setFocus()
        combo_widget.showPopup()
```

**How it works:**
1. Lấy row number từ cell được click
2. Lấy combobox widget ở cột 2 (Importance Scale column) của row đó
3. Set focus vào combobox
4. Gọi `showPopup()` để mở dropdown

---

## 🎨 User Experience Flow

### Scenario 1: Click vào "Criterion 1" (Column 0)
```
User clicks: [Giá] cell
         ↓
Get row number: 0
         ↓
Get combo from row 0, column 2
         ↓
combo.setFocus() + combo.showPopup()
         ↓
Dropdown opens! ✨
```

### Scenario 2: Click vào "Criterion 2" (Column 1)
```
User clicks: [Chất lượng] cell
         ↓
Get row number: 0
         ↓
Get combo from row 0, column 2
         ↓
Dropdown opens! ✨
```

### Scenario 3: Click vào "Importance Scale" (Column 2)
```
User clicks: [1: Equally important] cell
         ↓
Get row number: 0
         ↓
Get combo from row 0, column 2
         ↓
Dropdown opens! ✨
```

**Result:** Dù click vào column nào, dropdown đều mở!

---

## 🧪 Testing Guide

### Test Case 1: Click vào Criterion 1
1. Open project và vào AHP tab
2. Select một criterion group có comparisons
3. **Click vào ô "Criterion 1"** (cột đầu tiên) của bất kỳ row nào
4. **Expected:** Dropdown "Importance Scale" của row đó tự động mở

### Test Case 2: Click vào Criterion 2  
1. **Click vào ô "Criterion 2"** (cột giữa) của bất kỳ row nào
2. **Expected:** Dropdown "Importance Scale" của row đó tự động mở

### Test Case 3: Click vào Importance Scale (original behavior)
1. **Click vào ô "Importance Scale"** (cột cuối)
2. **Expected:** Dropdown mở như bình thường

### Test Case 4: Multiple clicks
1. Click vào row 1, column 0 → dropdown opens
2. Select một giá trị
3. Click vào row 2, column 1 → dropdown của row 2 opens
4. **Expected:** Mỗi click vào row khác nhau mở dropdown của row tương ứng

---

## 💡 Technical Details

### Why `itemClicked` instead of `cellClicked`?

- `itemClicked(QTableWidgetItem)`: Triggered when clicking on **item cells**
- `cellClicked(int row, int col)`: Triggered when clicking **any cell including widget cells**

We use `itemClicked` because:
- ✅ Works for text cells (Criterion 1, Criterion 2)
- ✅ Simple to get row from item: `item.row()`
- ⚠️ **Note:** Clicking directly on combobox widget won't trigger this (but that's fine, combobox handles it)

### `showPopup()` Method

```python
combo_widget.showPopup()
```

- Qt method to programmatically open combobox dropdown
- Equivalent to user clicking the dropdown arrow
- Combined with `setFocus()` to ensure widget is active

---

## 📊 Affected Components

### Modified:
- ✅ `gui/ahp_tab.py`:
  - Line 149: Added `itemClicked` signal connection
  - Lines 615-627: Added `on_comparison_cell_clicked` method

### Not Modified:
- TOPSIS rating table (could add similar feature later if needed)
- Expert selection dropdown
- Criteria type dropdown

---

## 🚀 Benefits

1. **Better UX**: User doesn't need to precisely click on dropdown column
2. **Faster Input**: Larger clickable area = faster workflow
3. **More Intuitive**: Clicking anywhere in row feels natural
4. **Accessibility**: Easier for users with less precise mouse control

---

## 🔮 Future Enhancements

### Possible improvements:
1. **TOPSIS Rating Table**: Apply same feature to rating table
2. **Keyboard Navigation**: 
   - Arrow keys to move between rows
   - Space/Enter to open dropdown
3. **Visual Feedback**:
   - Highlight entire row on hover
   - Show cursor change when hovering over clickable cells

---

## ✅ Summary

**Now users can click ANYWHERE in the comparison row to open the dropdown!**

- ✅ Click on "Criterion 1" → dropdown opens
- ✅ Click on "Criterion 2" → dropdown opens  
- ✅ Click on "Importance Scale" → dropdown opens
- ✅ No more need to precisely click on last column
- ✅ Faster and more intuitive data entry

**Files changed:** 
- [`gui/ahp_tab.py`](file:///G:/anti/supplier_selection_app/gui/ahp_tab.py)

**Lines added:** ~15 lines of code
