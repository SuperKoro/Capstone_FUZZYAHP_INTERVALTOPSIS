# Build Distribution Guide

Hướng dẫn build và tạo installer cho **Supplier Selection Application**.

---

## 📋 Yêu Cầu

### Bắt buộc:
- ✅ **Python 3.8+** đã cài đặt
- ✅ **PyInstaller** (`pip install pyinstaller`)
- ✅ Tất cả dependencies trong `requirements.txt`

### Tùy chọn (cho installer):
- 📦 **Inno Setup 6** - Download tại: https://jrsoftware.org/isdl.php

---

## 🚀 Cách Build

### **Phương án 1: Build Script Tự Động (Khuyến nghị)**

#### PowerShell Script (Đầy đủ tính năng):
```powershell
.\build_dist.ps1
```

**Tùy chọn:**
- `.\build_dist.ps1 -Clean` - Xóa build cũ trước khi build
- `.\build_dist.ps1 -SkipInstaller` - Chỉ build executable, bỏ qua installer

#### Batch Script (Đơn giản hơn):
```cmd
build_quick.bat
```

### **Phương án 2: Build Thủ Công**

#### Bước 1: Build Executable
```powershell
python -m PyInstaller --onedir --windowed --name SupplierSelection `
    --icon assets/icon.ico.ico main.py `
    --hidden-import PyQt6 `
    --hidden-import sqlite3 `
    --hidden-import numpy `
    --add-data "assets;assets" `
    --add-data "resources;resources" `
    --clean --noconfirm
```

**Kết quả:** `dist/SupplierSelection/SupplierSelection.exe`

#### Bước 2: Tạo Installer (Nếu có Inno Setup)
```powershell
iscc SupplierSelection_Setup.iss
```

**Kết quả:** `installer_output/SupplierSelection_Setup_v1.0.0.exe`

---

## 📁 Cấu Trúc Output

Sau khi build thành công:

```
supplier_selection_app/
├── build/                    # Temporary build files (có thể xóa)
├── dist/
│   └── SupplierSelection/    # ← Executable và dependencies
│       ├── SupplierSelection.exe
│       ├── _internal/        # Python runtime & libraries
│       ├── assets/           # Icons, images
│       └── resources/        # Additional resources
└── installer_output/
    └── SupplierSelection_Setup_v1.0.0.exe  # ← Windows Installer
```

---

## ⚡ Quick Commands

| Mục đích | Command |
|----------|---------|
| **Build nhanh** | `.\build_quick.bat` |
| **Build đầy đủ** | `.\build_dist.ps1` |
| **Build + Clean** | `.\build_dist.ps1 -Clean` |
| **Chỉ exe, không installer** | `.\build_dist.ps1 -SkipInstaller` |
| **Test executable** | `.\dist\SupplierSelection\SupplierSelection.exe` |

---

## 🐛 Troubleshooting

### Lỗi: "PyInstaller not found"
```powershell
pip install pyinstaller
```

### Lỗi: Missing modules
Kiểm tra `requirements.txt` và cài đặt:
```powershell
pip install -r requirements.txt
```

### Build quá lâu?
- Build lần đầu mất **5-10 phút** (normal)
- Build lần sau nhanh hơn vì PyInstaller cache

### Executable không chạy?
1. Kiểm tra antivirus (có thể block)
2. Test trên máy sạch (chưa cài Python)
3. Check Windows Defender logs

---

## 📦 Distribution

### Phân phối Executable (Portable):
- Nén folder `dist/SupplierSelection/` thành ZIP
- User giải nén và chạy `SupplierSelection.exe`
- Không cần cài đặt Python

### Phân phối Installer (Recommended):
- File: `installer_output/SupplierSelection_Setup_v1.0.0.exe`
- User chạy installer → tự động cài vào Program Files
- Tạo shortcuts và file associations (.mcdm files)
- Có uninstaller

---

## 🔧 Customize Build

### Thay đổi icon:
Sửa trong `build_dist.ps1` hoặc `SupplierSelection_Setup.iss`:
```
--icon your_icon.ico
```

### Thêm hidden imports:
```
--hidden-import your_module
```

### Thay đổi version:
Sửa trong `SupplierSelection_Setup.iss`:
```iss
#define MyAppVersion "1.0.1"
```

---

## 📝 Build Checklist

Trước khi build và distribute:

- [ ] Test tất cả chức năng của app
- [ ] Xóa tất cả debug `print()` statements
- [ ] Update version number trong `SupplierSelection_Setup.iss`
- [ ] Update CHANGELOG
- [ ] Run build với `-Clean` flag
- [ ] Test executable trên máy sạch (chưa cài Python)
- [ ] Test installer (install + uninstall)
- [ ] Scan antivirus (VirusTotal)
- [ ] Tạo release notes

---

## 📌 Notes

- **Build size**: ~80-100 MB (bao gồm Python runtime)
- **Build time**: 5-10 phút lần đầu, 2-3 phút lần sau
- **Installer size**: ~90-110 MB (compressed)
- **Supported OS**: Windows 7/8/10/11 (64-bit)

---

## 🆘 Support

Nếu gặp vấn đề khi build:
1. Check error logs trong terminal
2. Xóa `build/` và `dist/` folders, build lại
3. Cài lại PyInstaller: `pip uninstall pyinstaller && pip install pyinstaller`
4. Check PyInstaller docs: https://pyinstaller.org/

---

**Happy Building! 🎉**
