# Prototype 2 - Supplier Selection System
## Multi-Criteria Decision Making Application

---

## 📋 Table of Contents

- [Overview](#overview)
- [Folder Structure](#folder-structure)
- [Quick Start](#quick-start)
- [Installation Guide](#installation-guide)
- [Technical Details](#technical-details)
- [Features](#features)
- [System Requirements](#system-requirements)

---

## 🎯 Overview

**Project**: Supplier Selection Decision Support System  
**Methods**: Fuzzy AHP + Interval TOPSIS  
**Technology**: Python + PyQt6 + SQLite  
**Version**: 1.0 (Updated with 7-level TOPSIS scale & transposed UI)

This prototype provides a complete Multi-Criteria Decision Making (MCDM) solution for supplier evaluation and selection using:
- **Fuzzy AHP**: Calculate criterion weights from expert pairwise comparisons
- **Interval TOPSIS**: Rank suppliers using 7-level linguistic ratings
- **Sensitivity Analysis**: Test decision robustness

---

## 📁 Folder Structure

```
Prototype 2/
│
├── 📂 Source Code/                    # Complete project source
│   ├── main.py                        # Application entry point
│   ├── requirements.txt               # Python dependencies
│   │
│   ├── 📂 gui/                        # User interface (PyQt6)
│   ├── 📂 algorithms/                 # MCDM algorithms
│   ├── 📂 database/                   # SQLite data layer
│   ├── 📂 utils/                      # Utilities & helpers
│   ├── 📂 commands/                   # Undo/Redo functionality
│   ├── 📂 tests/                      # Unit tests
│   ├── 📂 assets/                     # Icons & images
│   │
│   └── 📄 Documentation files (.md)
│
└── 📂 dist/                           # Distribution (Ready to use)
    └── SupplierSelection/
        ├── SupplierSelection.exe      # ← Run this!
        └── _internal/                 # Dependencies (required)
```

---

## 🚀 Quick Start

### Option 1: Run Executable (Recommended)

**No installation required!**

1. Navigate to: `dist/SupplierSelection/`
2. Double-click: `SupplierSelection.exe`
3. Application will launch immediately

**⚠️ Important**: Keep `_internal/` folder with the .exe file

---

### Option 2: Run from Source Code

**Prerequisites**: Python 3.11+

```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

---

## 🔧 Technical Details

### Architecture

**4-Layer Architecture**:
- **Presentation Layer**: PyQt6 GUI
- **Business Logic**: Fuzzy AHP, Interval TOPSIS, Sensitivity Analysis
- **Data Persistence**: SQLite Database
- **Utility Layer**: Excel I/O, Validation

### Technologies

| Category | Technology |
|----------|-----------|
| Language | Python 3.13 |
| GUI | PyQt6 |
| Database | SQLite 3 |
| Numerical | NumPy, Pandas |
| Visualization | Matplotlib |
| Distribution | PyInstaller |

### MCDM Methods

#### Fuzzy AHP
- Calculate criterion weights
- Chang's extent analysis
- Consistency check (CR ≤ 0.1)

#### Interval TOPSIS (7-Level Scale)
- Very Poor [0, 1]
- Poor [1, 3]
- **Medium Poor [3, 4]** ← NEW
- Fair [4, 5]
- **Medium Good [5, 6]** ← NEW
- Good [6, 9]
- Very Good [9, 10]

#### Sensitivity Analysis
- Weight perturbation (±20%)
- Rank reversal detection
- Stability metrics

---

## ✨ Features

✅ **Project Management**
- Create/Open/Save projects (.mcdm format)
- Hierarchical criteria structure
- Multi-expert evaluation

✅ **Fuzzy AHP Evaluation**
- Pairwise comparisons
- Automatic weight calculation
- Consistency validation

✅ **Interval TOPSIS Rating**
- **7-level linguistic scale** (updated)
- **Transposed table** (criteria in rows)
- Expert aggregation

✅ **Results & Analysis**
- Supplier rankings
- Visual charts
- Sensitivity analysis

✅ **Data Management**
- Excel import/export
- Scenario management
- Auto-save

---

## 💻 System Requirements

### Minimum
- Windows 10/11 (64-bit)
- 4 GB RAM
- 200 MB storage

### Recommended
- Windows 11
- 8 GB+ RAM
- 1920x1080 display

---

## 📖 Documentation

- **HUONG_DAN_SU_DUNG.md** - Vietnamese user guide
- **ARCHITECTURE_DIAGRAMS.md** - System architecture
- **QUICK_START.md** - Step-by-step tutorial
- **In-app Help** - Help menu → User Guide

---

## 🎓 Usage Workflow

```
1. Create Project
2. Add Criteria & Alternatives
3. Add Experts
4. AHP Comparisons → Calculate Weights
5. TOPSIS Ratings (7 levels)
6. Calculate Rankings
7. View Results
8. Sensitivity Analysis
9. Export Excel
```

---

## 🔄 Recent Updates (Version 1.0)

✨ **New Features**:
- 7-level TOPSIS scale (added Medium Poor & Medium Good)
- Transposed TOPSIS table (criteria in rows)
- Fixed sensitivity analysis defaults

❌ **Removed**: "Excellent" rating level

---

## 🛠️ Building from Source

```bash
# Run build script
build_quick.bat

# Output: dist/SupplierSelection/
```

---

## 📦 Submission Contents

✅ Complete Source Code (~8,000 LOC)  
✅ Executable Application  
✅ Technical Documentation  
✅ User Manuals (EN + VN)  
✅ Architecture Diagrams  

---

## 🎯 For Reviewers

### Evaluation Checklist

- [ ] Application launches
- [ ] Create project works
- [ ] AHP calculation functional
- [ ] TOPSIS with 7 levels
- [ ] Rankings display correctly
- [ ] Export to Excel works
- [ ] Code well-documented
- [ ] Architecture diagrams provided

---

**Version**: 1.0  
**Date**: January 2026  
**Status**: ✅ Production Ready  

**Thank you for reviewing! 🚀**
