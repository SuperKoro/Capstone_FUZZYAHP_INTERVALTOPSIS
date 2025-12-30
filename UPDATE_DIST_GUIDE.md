# 🔄 Cách Update Distribution Đơn Giản

Bạn có **2 options** để update distribution:

---

## 📦 **Option 1: ZIP Nhanh (Không có bug fixes mới)** ⚡

Nếu bạn chỉ cần **đóng gói dist cũ** để distribute:

```cmd
# Tạo ZIP từ dist có sẵn (30 giây)
powershell -Command "Compress-Archive -Path 'dist\SupplierSelection\*' -DestinationPath 'dist\SupplierSelection.zip' -Force"
```

**✅ Ưu điểm:** Nhanh (30 giây)  
**❌ Nhược điểm:** KHÔNG có bug fixes mới (ahp_tab.py, topsis_tab.py)

---

## 🔨 **Option 2: Rebuild Đầy Đủ (Có bug fixes)** ⭐ Khuyến nghị

Để có **bug fixes mới**, cần rebuild:

### **Cách 1: Dùng script (Tự động)**
```cmd
rebuild_simple.bat
```

Chờ **3-5 phút** → Done!

### **Cách 2: Manual (Nếu script lỗi)**
```cmd
# Bước 1: Clean
rmdir /s /q build
rmdir /s /q dist\SupplierSelection

# Bước 2: Build
python -m PyInstaller main.py --onedir --windowed --name SupplierSelection --icon assets/icon.ico.ico --add-data "assets;assets" --add-data "resources;resources" --noconfirm

# Bước 3: ZIP
powershell -Command "Compress-Archive -Path 'dist\SupplierSelection\*' -DestinationPath 'dist\SupplierSelection_v1.0.1.zip' -Force"
```

**✅ Ưu điểm:** Có tất cả bug fixes mới  
**⏱️ Thời gian:** 3-5 phút

---

## 🐛 **Bug Fixes Included:**

Build mới sẽ có:
1. ✅ **Fix crash khi đổi tên expert** (`ahp_tab.py`)
2. ✅ **Fix crash khi đổi weight expert** (`ahp_tab.py`)  
3. ✅ **Fix warning giả TOPSIS** (`topsis_tab.py`)

---

## 📁 **Output Location:**

Sau khi build xong:

```
dist/
├── SupplierSelection/          # Folder chứa executable
│   └── SupplierSelection.exe
└── SupplierSelection_v1.0.1.zip  # ZIP để distribute
```

---

## 💡 **Khuyến nghị:**

**Dùng Option 2** (rebuild) để users nhận được bug fixes!

Build lần đầu mất 3-5 phút, không quá lâu.

---

## 🆘 **Nếu build bị lỗi:**

1. Check Python version: `python --version`
2. Reinstall PyInstaller: `pip uninstall pyinstaller && pip install pyinstaller`
3. Xóa `build/` và `dist/`, thử lại
4. Xem logs trong terminal để debug

---

**Chúc update thành công! 🎉**
