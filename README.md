# Supplier Selection Application

A desktop application for Multi-Criteria Decision Making (MCDM) using Fuzzy AHP and Interval TOPSIS methodologies to evaluate and rank suppliers.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-Educational-green)

## 🎯 Overview

This application provides a comprehensive solution for supplier selection problems using hybrid MCDM methods:
- **Fuzzy AHP**: Calculate criteria weights based on expert pairwise comparisons
- **Interval TOPSIS**: Rank alternatives using linguistic performance ratings
- **What-If Analysis**: Evaluate decision robustness through sensitivity analysis

## ✨ Key Features

### Fuzzy AHP Module
- **17-Level Linguistic Scale**: Comprehensive scale from -9 to 9 for pairwise comparisons
- **Multi-Expert Support**: Aggregate judgments from multiple experts using fuzzy geometric mean
- **Dual Input Modes**:
  - Direct Input: Enter comparisons directly in the application
  - Excel Import: Generate templates, fill offline, and import back
- **Consistency Check**: Automatic CR calculation with color-coded feedback (CR ≤ 0.1)
- **Hierarchical Criteria**: Support for criteria and sub-criteria structures

### Interval TOPSIS Module
- **Linguistic Ratings**: Six-level scale (Very Poor to Excellent)
- **Interval Calculations**: Full interval arithmetic for robust decision-making
- **Expert Aggregation**: Combine ratings from multiple experts
- **Automated Ranking**: Calculate final supplier rankings based on closeness coefficients

### Sensitivity Analysis (NEW)
- **Weight Perturbation**: Analyze impact of criteria weight changes
- **Rank Reversal Detection**: Identify critical decision points
- **Stability Metrics**: Measure robustness of ranking results
- **Visual Charts**: Interactive matplotlib charts with zoom/pan capabilities
- **Excel Export**: Detailed sensitivity reports with conditional formatting

### Scenario Management (NEW)
- **What-If Analysis**: Create multiple scenarios to compare different evaluation outcomes
- **Deep Copy Strategy**: Independent scenarios with complete data isolation
- **Scenario Comparison**: Easily switch between different analysis scenarios
- **Base Scenario Protection**: Original data preserved and cannot be deleted

### Visualization & Export
- **Interactive Charts**: Embedded bar charts showing ranking results
- **Excel Export**: Comprehensive reports with all calculations and results
- **Color-Coded Results**: Visual highlighting of top-ranked alternatives
- **User Guide**: Built-in step-by-step visual instructions

## 📋 Requirements

- **Python**: 3.10 or higher
- **Operating System**: Windows (tested), Linux/Mac (should work)
- **Dependencies**: See `requirements.txt`

## 🚀 Installation

### Quick Start

1. **Clone the repository** (or download the source code)

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the application**:
```bash
python main.py
```

### Dependencies

The application requires the following Python packages:
- PyQt6 (GUI framework)
- NumPy (numerical computations)
- Pandas (data handling)
- Matplotlib (charting)
- openpyxl (Excel export)
- xlsxwriter (Excel formatting)

All dependencies are listed in `requirements.txt`.

## 📖 Usage

### 1. Create a New Project
- Click **New** in the toolbar or File → New Project
- Enter project name and select save location
- Project saved as `.mcdm` file (SQLite database)

### 2. Setup Criteria and Alternatives
- Navigate to **Project Setup** tab
- Add evaluation criteria (e.g., Price, Quality, Delivery Time)
  - Click **Add** to create main criteria
  - Click **Add** next to a criterion to create sub-criteria
- Specify if each criterion is **Benefit** (higher is better) or **Cost** (lower is better)
- Add supplier alternatives using **Add Alternative** button

### 3. Perform Fuzzy AHP Evaluation
- Navigate to **Fuzzy AHP Evaluation** tab
- Add expert profiles using **Add Expert**
- Select an expert from the dropdown
- Choose input mode:
  - **Direct Input**: Click on criteria nodes and enter pairwise comparisons using dropdown menus
  - **Excel Import**: Generate template, fill offline, and import completed file
- Click **Calculate All Weights**
- Review **Consistency Ratio** (CR)
  - ✅ CR ≤ 0.1 (green): Acceptable consistency
  - ❌ CR > 0.1 (red): Revise comparisons

### 4. Enter TOPSIS Ratings
- Navigate to **TOPSIS Rating** tab
- Select an expert from the dropdown
- Enter performance ratings for each alternative against each criterion
- Use linguistic ratings from dropdown menus:
  - Very Poor [0-1], Poor [1-3], Fair [3-5], Good [5-7], Very Good [7-9], Excellent [9-10]
- Click **Calculate TOPSIS Rankings**

### 5. View Results
- Navigate to **Results** tab
- View ranked alternatives with scores
- See visual bar chart representation
- Export results to Excel using **File → Export Results to Excel**

### 6. Sensitivity Analysis (Optional)
- Navigate to **Sensitivity Analysis** tab
- Select a criterion to analyze
- Choose perturbation range (±10%, ±20%, ±30%, ±50%)
- Click **Run Analysis**
- View sensitivity chart and rank reversal warnings
- Export detailed analysis to Excel

### 7. Scenario Management (Optional)
- Use the **Scenario** dropdown in the toolbar to manage what-if analyses
- Click **➕** to create a new scenario (duplicates current scenario)
- Switch between scenarios using the dropdown
- Click **🗑️** to delete a scenario (Base scenario cannot be deleted)

## 🏗️ Technical Details

### Architecture
```
supplier_selection_app/
├── main.py                      # Application entry point
├── database/                    # SQLite database layer
│   ├── schema.py               # Database schema definition
│   ├── manager.py              # CRUD operations
│   └── database_migration.py  # Schema migration tool
├── algorithms/                  # MCDM algorithms
│   ├── fuzzy_ahp.py           # Fuzzy AHP implementation
│   ├── interval_topsis.py     # Interval TOPSIS implementation
│   └── sensitivity_analysis.py # Sensitivity analysis
├── gui/                         # PyQt6 user interface
│   ├── main_window.py         # Main application window
│   ├── project_tab.py         # Project configuration
│   ├── ahp_tab.py             # AHP evaluation
│   ├── topsis_tab.py          # TOPSIS rating
│   ├── results_tab.py         # Results display
│   ├── sensitivity_tab.py     # Sensitivity analysis
│   ├── user_guide_dialog.py   # User guide
│   └── welcome_dialog.py      # Welcome screen
├── utils/                       # Utilities
│   ├── scenario_manager.py    # Scenario management
│   ├── project_manager.py     # Recent projects
│   ├── excel_handler.py       # Excel import/export
│   └── undo_manager.py        # Undo/redo functionality
└── assets/                      # Images and resources
    └── guide_images/           # User guide screenshots
```

### Algorithms

#### Fuzzy AHP
- **Triangular Fuzzy Numbers (TFN)**: (l, m, u) representation
- **Fuzzy Geometric Mean**: Aggregate expert comparisons
- **Center of Area (CoA)**: Defuzzification method
- **Eigenvalue Method**: Consistency ratio calculation
- **17-Level Scale**: From Absolutely Less Important (-9) to Absolutely More Important (+9)

#### Interval TOPSIS
- **Vector Normalization**: For interval data
- **Weighted Normalized Matrix**: Incorporates AHP weights
- **Euclidean Distance**: Calculated for interval numbers
- **Closeness Coefficient**: Final ranking metric
- **Linguistic Ratings**: [0-1], [1-3], [3-5], [5-7], [7-9], [9-10]

#### Sensitivity Analysis
- **Weight Perturbation**: Vary individual criterion weights
- **Rank Stability**: Detect changes in alternative rankings
- **Stability Index**: Measure overall decision robustness
- **Critical Points**: Identify weight changes causing rank reversals

### Database Schema
- **SQLite**: Lightweight, file-based database
- **Foreign Keys**: Enforced referential integrity
- **Auto-migration**: Seamless schema updates
- **Scenarios**: Isolated data copies for what-if analysis

## 🔒 Security

✅ **Production-Ready Security**:
- Parameterized SQL queries (SQL injection safe)
- No eval/exec usage
- No external API calls
- File operations through Qt dialogs only
- Completely offline operation

## 📴 Offline Operation

This application is designed to work completely offline:
- ✅ No internet connection required
- ✅ All data stored locally in SQLite database
- ✅ Excel templates generated locally
- ✅ Self-contained Python environment
- ✅ Portable database files (.mcdm)

## 📚 Documentation

- **User Guide**: Press `F1` or click Help → User Guide (in-app visual guide)
- **Methodology**: Click Methodology menu to learn about Fuzzy AHP and Interval TOPSIS
- **Quick Start**: See `QUICK_START.md` (Tiếng Việt)
- **Detailed Guide**: See `HUONG_DAN_SU_DUNG.md` (Tiếng Việt)

## 🐛 Known Issues

None currently reported. Application is production-ready.

## 🔄 Version History

### Version 1.0.0 (Current)
- ✅ Fuzzy AHP with multi-expert support
- ✅ Interval TOPSIS ranking
- ✅ Sensitivity analysis
- ✅ Scenario management (what-if analysis)
- ✅ Excel import/export
- ✅ Visual user guide
- ✅ Production-ready code quality
- ✅ Security hardened

## 📝 License

This application is provided as-is for educational and business use.

## 👥 Support

For issues or questions:
- Check the built-in User Guide (F1)
- Review documentation files
- Contact development team

## 🙏 Acknowledgments

Built with:
- **PyQt6**: Cross-platform GUI framework
- **NumPy**: Numerical computing
- **Pandas**: Data manipulation
- **Matplotlib**: Visualization
- **SQLite**: Embedded database

---

**Ready for Production** ✅ | **Version 1.0.0** | **Last Updated**: December 2025
