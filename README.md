- **17-Level Linguistic Scale**: Comprehensive scale from -9 to 9 for pairwise comparisons
- **Dual Input Modes**:
  - Direct Input: Enter comparisons directly in the application
  - Excel Import: Generate templates, fill offline, and import back
- **Fuzzy Geometric Mean**: Aggregate multiple expert judgments
- **Consistency Ratio**: Automatic CR calculation with color-coded feedback

### Interval TOPSIS Module
- **Linguistic Ratings**: Six-level scale (Very Poor to Excellent)
- **Interval Calculations**: Full interval arithmetic for robust decision-making
- **Automated Ranking**: Calculate final supplier rankings based on closeness coefficients

### Visualization & Export
- **Interactive Charts**: Embedded bar charts showing ranking results
- **Excel Export**: Comprehensive reports with all calculations and results
- **Color-Coded Results**: Visual highlighting of top-ranked alternatives

## Installation

### Requirements
- Python 3.10 or higher
- Windows operating system

### Setup
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python main.py
```

## Usage

### 1. Create a New Project
- File → New Project
- Enter project name and select save location
- Project saved as .mcdm file (SQLite database)

### 2. Setup Criteria and Alternatives
- Navigate to "Project Setup" tab
- Add evaluation criteria (e.g., Price, Quality, Delivery Time)
- Specify if each criterion is Benefit or Cost
- Add supplier alternatives

### 3. Perform Fuzzy AHP Evaluation
- Navigate to "Fuzzy AHP Evaluation" tab
- Add expert profiles
- Choose input mode:
  - **Direct Input**: Enter pairwise comparisons using dropdown menus
  - **Excel Import**: Generate template, fill offline, import completed file
- Click "Calculate AHP Weights"
- Review Consistency Ratio (should be < 0.1)

### 4. Enter TOPSIS Ratings
- Navigate to "TOPSIS Rating" tab
- Enter performance ratings for each alternative against each criterion
- Use linguistic ratings from dropdown menus
- Click "Calculate TOPSIS Ranking"

### 5. View Results
- Navigate to "Results" tab
- View ranked alternatives with scores
- See visual bar chart
- Export results to Excel for reporting

## Technical Details

### Architecture
```
supplier_selection_app/
├── main.py                 # Application entry point
├── database/               # SQLite database layer
│   ├── schema.py          # Database schema
│   └── manager.py         # CRUD operations
├── algorithms/            # MCDM algorithms
│   ├── fuzzy_ahp.py      # Fuzzy AHP implementation
│   └── interval_topsis.py # Interval TOPSIS implementation
├── gui/                   # PyQt6 user interface
│   ├── main_window.py    # Main application window
│   ├── project_tab.py    # Project configuration
│   ├── ahp_tab.py        # AHP evaluation
│   ├── topsis_tab.py     # TOPSIS rating
│   └── results_tab.py    # Results display
└── utils/                 # Utilities
    ├── excel_handler.py  # Excel import/export
    └── validators.py     # Input validation
```

### Fuzzy AHP Algorithm
- Uses Triangular Fuzzy Numbers (TFN)
- Fuzzy Geometric Mean for aggregation
- Center of Area (CoA) defuzzification
- Eigenvalue-based consistency checking

### Interval TOPSIS Algorithm
- Vector normalization for interval data
- Weighted normalized decision matrix
- Euclidean distance for interval numbers
- Closeness coefficient ranking

## Offline Operation
This application is designed to work completely offline:
- No internet connection required
- All data stored locally in SQLite database
- Excel templates generated locally
- Self-contained Python environment

## License
This application is provided as-is for educational and business use.

## Support
For issues or questions, please refer to the documentation or contact support.
