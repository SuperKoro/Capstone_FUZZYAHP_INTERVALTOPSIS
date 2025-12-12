# Hướng Dẫn Sửa Lỗi "no such column: scenario_id"

## Vấn Đề
Bạn gặp lỗi **"Failed to save rating: Database error: no such column: scenario_id"** khi cố gắng lưu TOPSIS rating.

## Nguyên Nhân
File cơ sở dữ liệu (.mcdm) của bạn chưa được cập nhật schema để hỗ trợ tính năng Scenarios mới.

## Giải Pháp

### Cách 1: Tự Động Migration (Khuyến Nghị)

Khi bạn khởi động lại ứng dụng sau các thay đổi mới, hệ thống sẽ **TỰ ĐỘNG** migrate database cho bạn.

**Làm theo các bước sau:**

1. **Đóng ứng dụng hiện tại** (nếu đang chạy)
2. **Khởi động lại ứng dụng**:
   ```bash
   python main.py
   ```
3. **Mở project của bạn** (file .mcdm)
4. Hệ thống sẽ tự động phát hiện và migrate database
5. Bạn sẽ thấy thông báo:
   ```
   [Scenarios Migration] Detected old schema version
   [Scenarios Migration] Running migration for: <file_path>
   [Scenarios Migration] ✓ Migration completed!
   ```

### Cách 2: Migration Thủ Công (Nếu cách 1 không hoạt động)

Nếu auto-migration không hoạt động, bạn có thể chạy migration thủ công:

**Bước 1:** Sao chép file .mcdm của bạn vào thư mục `supplier_selection_app`

**Bước 2:** Chạy migration script:
```bash
cd G:\anti\supplier_selection_app
python run_migration.py
```

**Bước 3:** Script sẽ tự động tìm và migrate tất cả file .mcdm trong thư mục

## Kiểm Tra Sau Migration

Sau khi migration hoàn tất:

1. ✅ Khởi động lại ứng dụng
2. ✅ Mở project của bạn
3. ✅ Vào tab "TOPSIS Rating"
4. ✅ Thử thay đổi một rating
5. ✅ **Không còn lỗi "scenario_id"!**

## Lưu Ý Quan Trọng

- ⚠️ Migration tạo bản backup tự động (tables: `*_backup`)
- ⚠️ Nên backup file .mcdm trước khi migration (để an toàn)
- ⚠️ Migration chỉ cần chạy **MỘT LẦN** cho mỗi file .mcdm
- ✅ Sau migration, tất cả dữ liệu cũ vẫn được giữ nguyên
- ✅ Migration thêm tính năng Scenarios nhưng vẫn hoạt động với project cũ

## Nếu Vẫn Gặp Lỗi

Nếu sau khi làm theo hướng dẫn trên mà vẫn gặp lỗi, vui lòng:

1. Kiểm tra terminal output để xem có thông báo lỗi migration không
2. Thử chạy migration thủ công (Cách 2)
3. Cung cấp thông tin lỗi chi tiết để được hỗ trợ thêm
