# GUI Testing Guide

## Tổng Quan

GUI testing trong PyQt6 bao gồm 3 loại chính:
1. **Unit Tests** - Test từng widget riêng lẻ
2. **Integration Tests** - Test tương tác giữa UI và Database
3. **End-to-End Tests** - Test toàn bộ user workflow

## Cài Đặt

```bash
pip install pytest pytest-qt pytest-cov
```

## Chạy Tests

```bash
# Chạy tất cả tests
pytest tests/

# Chạy GUI tests cụ thể
pytest tests/test_gui_ahp_tab.py -v

# Chạy với coverage
pytest tests/ --cov=gui --cov-report=html

# Chạy test cụ thể
pytest tests/test_gui_ahp_tab.py::test_ahp_tab_loads_successfully
```

## Cấu Trúc Tests

### 1. Unit Tests (`test_gui_*.py`)

Test các widget riêng lẻ:

```python
def test_button_enabled_state(ahp_tab):
    """Test button is disabled initially"""
    assert ahp_tab.calculate_button.isEnabled() == False
```

### 2. Integration Tests (`test_gui_database_integration.py`)

Test dữ liệu giữa UI ↔ Database:

```python
def test_save_comparison_to_database(ahp_tab):
    """Test comparison saves to DB"""
    # Add comparison via UI
    # Query database
    # Verify data matches
```

### 3. Interaction Tests

Test user interactions với `qtbot`:

```python
def test_click_add_expert(ahp_tab, qtbot):
    """Test clicking Add Expert button"""
    with qtbot.waitSignal(ahp_tab.expert_added):
        QTest.mouseClick(ahp_tab.add_expert_button, Qt.LeftButton)
```

## Fixtures Quan Trọng

### `qapp` - QApplication
```python
@pytest.fixture(scope='session')
def qapp():
    """Create QApplication for all tests"""
    app = QApplication.instance() or QApplication(sys.argv)
    yield app
```

### `temp_db` - Temporary Database
```python
@pytest.fixture
def temp_db():
    """Create temp database with test data"""
    # Create .mcdm file
    # Initialize with test data
    yield db_path
    # Cleanup
```

### `qtbot` - Qt Test Bot
```python
def test_with_qtbot(widget, qtbot):
    """Use qtbot for interactions"""
    qtbot.addWidget(widget)
    qtbot.mouseClick(button, Qt.LeftButton)
    qtbot.waitSignal(signal)
```

## Patterns Thường Gặp

### 1. Test Widget State
```python
def test_widget_state():
    assert widget.isVisible() == True
    assert widget.isEnabled() == False
    assert widget.text() == "Expected Text"
```

### 2. Test User Click
```python
def test_button_click(qtbot):
    QTest.mouseClick(button, Qt.MouseButton.LeftButton)
    qtbot.wait(100)  # Wait for processing
    assert result_label.text() == "Success"
```

### 3. Test Table Data
```python
def test_table_data():
    assert table.rowCount() == expected_rows
    assert table.item(0, 0).text() == "Expected Value"
```

### 4. Test Signal Emission
```python
def test_signal(qtbot):
    with qtbot.waitSignal(widget.dataChanged, timeout=1000):
        widget.trigger_change()
```

### 5. Test Data Binding
```python
def test_load_data(ahp_tab, temp_db):
    ahp_tab.load_data()
    
    # Verify UI matches database
    db_manager = ahp_tab.main_window.get_db_manager()
    with db_manager as db:
        experts = db.get_experts(project_id)
        assert table.rowCount() == len(experts)
```

## Mock & Stub

### Mock QMessageBox
```python
def test_error_message(monkeypatch):
    """Test error dialog shows"""
    messages = []
    
    def mock_critical(parent, title, text):
        messages.append(text)
    
    monkeypatch.setattr(QMessageBox, 'critical', mock_critical)
    
    # Trigger error
    widget.do_something_invalid()
    
    assert len(messages) > 0
    assert "Error" in messages[0]
```

### Mock QFileDialog
```python
def test_file_selection(monkeypatch):
    """Mock file dialog"""
    def mock_dialog(*args, **kwargs):
        return "/fake/path.xlsx", ""
    
    monkeypatch.setattr(QFileDialog, 'getOpenFileName', mock_dialog)
    
    # Test code that opens file
```

## Test Coverage Goals

**Target Coverage:** 80%+

### Priority Areas:

1. **High Priority** (Must Test):
   - [ ] Data loading/saving
   - [ ] User input validation
   - [ ] Calculation triggers
   - [ ] Error handling

2. **Medium Priority** (Should Test):
   - [ ] Widget state changes
   - [ ] Signal/slot connections
   - [ ] Undo/redo operations
   - [ ] Table interactions

3. **Low Priority** (Nice to Test):
   - [ ] Visual styling
   - [ ] Tooltips
   - [ ] Window geometry

## Common Issues

### Issue 1: Tests Hang
```python
# Problem: Waiting forever for signal
with qtbot.waitSignal(signal):  # Times out
    ...

# Solution: Add timeout
with qtbot.waitSignal(signal, timeout=1000):
    ...
```

### Issue 2: QApplication Already Exists
```python
# Use session-scoped fixture
@pytest.fixture(scope='session')
def qapp():
    return QApplication.instance() or QApplication(sys.argv)
```

### Issue 3: Database Conflicts
```python
# Always use temporary databases
# Clean up after each test
@pytest.fixture
def temp_db():
    db = create_temp_db()
    yield db
    os.unlink(db)  # Important!
```

## Best Practices

1. **Independent Tests** - Mỗi test không phụ thuộc vào test khác
2. **Clean State** - Reset state sau mỗi test
3. **Fast Tests** - Tránh sleep(), dùng waitSignal()
4. **Descriptive Names** - Test name nói rõ test gì
5. **One Assertion Focus** - Mỗi test focus vào 1 behavior

## Example: Full Test Flow

```python
def test_complete_ahp_workflow(qapp, temp_db, qtbot):
    """Test complete AHP workflow from start to finish"""
    
    # 1. Setup
    window = MainWindow()
    window.load_project(temp_db[0])
    ahp_tab = window.ahp_tab
    
    # 2. Add expert
    # (Would interact with UI here)
    
    # 3. Enter comparisons
    # (Would interact with comparison table)
    
    # 4. Calculate weights
    QTest.mouseClick(ahp_tab.calculate_button, Qt.LeftButton)
    qtbot.wait(500)
    
    # 5. Verify results
    assert ahp_tab.cr_label.text() != ""
    assert "CR" in ahp_tab.cr_label.text()
    
    # 6. Verify database
    db_manager = window.get_db_manager()
    with db_manager as db:
        criteria = db.get_criteria(temp_db[1])
        weights = [c['weight'] for c in criteria]
        assert sum(weights) > 0  # Weights calculated
    
    # Cleanup
    window.close()
```

## Next Steps

1. Implement tests từ `test_gui_ahp_tab.py`
2. Điền đầy đủ các test functions (hiện đang có `pass`)
3. Chạy tests và fix failures
4. Đo coverage và improve
5. Add tests cho các tabs khác (TOPSIS, Project, Results)
6. Setup CI/CD để run tests tự động

## Resources

- [pytest-qt Documentation](https://pytest-qt.readthedocs.io/)
- [PyQt6 Testing Guide](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [Python Testing Best Practices](https://docs.pytest.org/en/latest/goodpractices.html)
