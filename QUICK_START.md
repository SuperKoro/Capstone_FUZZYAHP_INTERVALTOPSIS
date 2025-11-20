# Quick Start Guide - Supplier Selection Application

## Installation

1. **Navigate to the application folder:**
   ```bash
   cd g:\anti\supplier_selection_app
   ```

2. **Install dependencies (if not already done):**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

## First-Time Usage

### Step 1: Create a New Project
1. Click **File → New Project** (or Ctrl+N)
2. Enter your project name (e.g., "Supplier Evaluation 2025")
3. Choose where to save the .mcdm file
4. Click Save

### Step 2: Setup Criteria and Alternatives
1. Go to **"Project Setup"** tab
2. **Add Criteria:**
   - Click "Add Criterion"
   - Enter name (e.g., "Price", "Quality", "Delivery Time")
   - Select type: Benefit (higher is better) or Cost (lower is better)
   - Repeat for all criteria (minimum 2)

3. **Add Alternatives:**
   - Click "Add Alternative"
   - Enter supplier name and description
   - Repeat for all suppliers (minimum 2)

### Step 3: Fuzzy AHP Evaluation
1. Go to **"Fuzzy AHP Evaluation"** tab
2. **Add Experts:**
   - Click "Add Expert"
   - Enter expert name
   - Repeat if you have multiple experts

3. **Enter Comparisons (Choose one method):**

   **Method A - Direct Input:**
   - Select expert from dropdown
   - For each criterion pair, select importance scale (-9 to 9)
   - Click "Save Comparisons"

   **Method B - Excel Import:**
   - Select expert from dropdown
   - Click "Generate Excel Template"
   - Open the Excel file
   - Fill in scale values (-9 to 9) for each comparison
   - Save the Excel file
   - Click "Import Completed Excel"
   - Select your filled Excel file

4. **Calculate Weights:**
   - Click "Calculate AHP Weights"
   - Check the Consistency Ratio (should be < 0.1)
   - If CR is too high, review your comparisons

### Step 4: TOPSIS Rating
1. Go to **"TOPSIS Rating"** tab
2. For each cell in the matrix:
   - Select a rating from dropdown (Very Poor to Excellent)
   - This represents how well each supplier performs on each criterion
3. Click "Calculate TOPSIS Ranking"

### Step 5: View Results
1. Go to **"Results"** tab (automatically opens after calculation)
2. View the ranking table:
   - Top 3 are highlighted (green, gray, yellow)
   - See closeness coefficients and distances
3. View the bar chart visualization
4. Click "Export Results to Excel" to save a report

## Tips

### Scale Values Guide
- **9**: Absolutely more important
- **7**: Strongly very more important
- **5**: Strongly more important
- **3**: Moderately more important
- **1**: Equally important
- **-3**: Moderately less important
- **-5**: Strongly less important
- **-9**: Absolutely less important

### Performance Ratings
- **Excellent**: Outstanding performance (9-10)
- **Very Good**: Above average (7-9)
- **Good**: Satisfactory (5-7)
- **Fair**: Acceptable (3-5)
- **Poor**: Below average (1-3)
- **Very Poor**: Unacceptable (0-1)

### Best Practices
1. **Consistency**: Try to be consistent in your comparisons
2. **Multiple Experts**: Use 2-3 experts for more robust results
3. **Save Often**: Use Ctrl+S to save your project
4. **Backup**: Copy .mcdm files to backup location

## Troubleshooting

**Problem**: CR is too high (≥ 0.1)
- **Solution**: Review your pairwise comparisons for inconsistencies

**Problem**: Cannot calculate TOPSIS
- **Solution**: Make sure you calculated AHP weights first

**Problem**: Application won't start
- **Solution**: Check that all dependencies are installed: `pip install -r requirements.txt`

## File Locations

- **Project Files**: .mcdm files (SQLite databases)
- **Excel Templates**: Generated when you click "Generate Excel Template"
- **Excel Reports**: Generated when you click "Export Results to Excel"

## Support

For more information, see README.md in the application folder.
