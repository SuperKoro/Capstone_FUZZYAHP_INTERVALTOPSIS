# 🎉 Build Scripts Đã Tạo Xong!

Tôi đã tạo **3 files** để giúp bạn build distribution dễ dàng hơn:

---

## 📂 Files Đã Tạo

### 1. **`build_dist.ps1`** (PowerShell Script - Khuyến nghị)
**Tính năng đầy đủ:**
- ✅ Auto-check dependencies
- ✅ Build executable với PyInstaller
- ✅ Tạo installer với Inno Setup (nếu có)
- ✅ Progress tracking & error handling
- ✅ Build summary với thời gian và file size

**Cách dùng:**
```powershell
# Build đầy đủ (exe + installer)
.\build_dist.ps1

# Xóa build cũ trước khi build
.\build_dist.ps1 -Clean

# Chỉ build exe, bỏ qua installer
.\build_dist.ps1 -SkipInstaller
```

---

### 2. **`build_quick.bat`** (Batch Script - Đơn giản)
**Build nhanh:**
- ✅ Build executable
- ✅ Simple & fast
- ✅ Không tạo installer

**Cách dùng:**
```cmd
build_quick.bat
```

---

### 3. **`BUILD_GUIDE.md`** (Hướng dẫn chi tiết)
**Documentation đầy đủ:**
- 📖 Yêu cầu hệ thống
- 📖 Hướng dẫn build từng bước
- 📖 Troubleshooting
- 📖 Distribution guide
- 📖 Build checklist

---

## 🚀 Quick Start

### Cách nhanh nhất:

**Windows PowerShell:**
```powershell
cd g:\anti\supplier_selection_app
.\build_dist.ps1
```

**Hoặc Command Prompt:**
```cmd
cd g:\anti\supplier_selection_app
build_quick.bat
```

Đợi **5-10 phút** → Done! ✅

---

## 📁 Output Locations

Sau khi build xong:

```
📦 Executable (Portable):
   dist/SupplierSelection/SupplierSelection.exe

📦 Installer (Windows Setup):
   installer_output/SupplierSelection_Setup_v1.0.0.exe
```

---

## ✨ Build với Bug Fixes Mới

Các bug fixes đã được áp dụng:
- ✅ **Fix crash khi đổi tên expert**
- ✅ **Fix crash khi đổi weight expert**

Build mới sẽ bao gồm tất cả các fixes này! 🎊

---

## 📝 Next Steps

1. **Build distribution:**
   ```powershell
   .\build_dist.ps1
   ```

2. **Test executable:**
   ```powershell
   .\dist\SupplierSelection\SupplierSelection.exe
   ```

3. **Tạo installer (nếu chưa có Inno Setup):**
   - Download: https://jrsoftware.org/isdl.php
   - Install Inno Setup
   - Run: `iscc SupplierSelection_Setup.iss`

4. **Distribute:**
   - Option 1: Nén `dist/SupplierSelection/` → Send ZIP
   - Option 2: Send file installer `.exe`

---

## 🆘 Need Help?

Xem file **`BUILD_GUIDE.md`** để có hướng dẫn chi tiết và troubleshooting!

---

**Happy Building! 🚀**
