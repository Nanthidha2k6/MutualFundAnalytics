# Bluestock Mutual Fund Analytics - Power BI Dashboard Setup Guide

This guide details the step-by-step process to load datasets, establish table relationships, write DAX measures, design page visuals, and export deliverables for the **Bluestock Mutual Fund Analytics Dashboard** using Microsoft Power BI Desktop.

---

## 🛠️ Step 1: Import CSV Datasets into Power BI

1. Open **Microsoft Power BI Desktop**.
2. Click **Get Data** on the Home tab ribbon, then select **Text/CSV**.
3. Browse and select the following 5 CSV files from the folder `data/processed/power_bi/`:
   - `dim_fund.csv`
   - `fact_nav.csv`
   - `fact_nifty_benchmarks.csv`
   - `fact_scorecard.csv`
   - `fact_alpha_beta.csv`
4. For each file, verify that **File Origin** is set to `65001: Unicode (UTF-8)` and **Delimiter** is set to `Comma`. Click **Load**.

---

## 🔗 Step 2: Establish Schema Relationships

1. Go to the **Model View** (left-hand sidebar icon of three connected rectangles).
2. Establish the relationships by dragging matching fields between tables. Set them as follows:

| From Table (Dimension) | From Field | To Table (Fact) | To Field | Cardinality | Cross Filter Direction |
|---|---|---|---|---|---|
| `dim_fund` | `amfi_code` | `fact_nav` | `amfi_code` | `1 to Many (1:*)` | `Single` (dim_fund filters fact_nav) |
| `dim_fund` | `amfi_code` | `fact_scorecard` | `amfi_code` | `1 to 1 (1:1)` | `Single` (dim_fund filters scorecard) |
| `dim_fund` | `amfi_code` | `fact_alpha_beta` | `amfi_code` | `1 to Many (1:*)` | `Single` (dim_fund filters alpha_beta) |

*Note: Power BI automatically links `fact_nav[date]` and `fact_nifty_benchmarks[date]` to calendar-date hierarchies for time-series aggregation.*

---

## 🧮 Step 3: Add Required DAX Measures

To create a measure:
- Right-click the `fact_nav` table in the **Data** pane on the right.
- Select **New Measure** and paste the corresponding DAX code:

### 1. Latest NAV
Returns the latest available NAV within the current filter context:
```dax
Latest NAV = 
CALCULATE(
    MAX('fact_nav'[nav]),
    LASTDATE('fact_nav'[date])
)
```

### 2. Cumulative Growth (Base = 100)
Rebases daily NAV growth starting from a normalized base value of 100:
```dax
Cumulative Growth = 
VAR FirstDateVal = CALCULATE(MIN('fact_nav'[date]), ALLSELECTED('fact_nav'[date]))
VAR FirstNAV = CALCULATE(SUM('fact_nav'[nav]), 'fact_nav'[date] = FirstDateVal)
VAR CurrentNAV = [Latest NAV]
RETURN
DIVIDE(CurrentNAV, FirstNAV, 0) * 100
```

### 3. Annualized Volatility
Measures the annualized standard deviation of daily fund returns:
```dax
Annualized Volatility = 
STDEV.S('fact_nav'[daily_return]) * SQRT(252)
```

### 4. Overall Score KPI
Displays the average ranking score:
```dax
Average Score = AVERAGE('fact_scorecard'[overall_scorecard_score])
```

### 5. Benchmark Cumulative Growth (Base = 100)
Rebases benchmark closing prices starting from a base value of 100:
```dax
Benchmark Cumulative Growth = 
VAR FirstDateVal = CALCULATE(MIN('fact_nifty_benchmarks'[date]), ALLSELECTED('fact_nifty_benchmarks'[date]))
VAR FirstClose = CALCULATE(SUM('fact_nifty_benchmarks'[close]), 'fact_nifty_benchmarks'[date] = FirstDateVal)
VAR CurrentClose = SUM('fact_nifty_benchmarks'[close])
RETURN
DIVIDE(CurrentClose, FirstClose, 0) * 100
```

---

## 🎨 Step 4: Theme, Canvas, and Layout Setup

1. Click on the **View** tab in the ribbon. Under the **Themes** dropdown, select **Browse for Themes** or import a custom JSON theme with the following **Bluestock Theme Palette**:
   - **Background**: `#F0F4F8` (Soft blue-grey)
   - **Headers & Sidebars**: `#0F1B35` (Dark Navy)
   - **Visual Cards**: `#FFFFFF` (White) with 12px rounded corners and a soft drop shadow.
   - **Accents**:
     - Navy Primary: `#1A2F5E`
     - Return Green: `#00875A`
     - Risk Red: `#DE350B`
     - High Performance Blue: `#0052CC`
2. Set Canvas size to **16:9** (1280 x 720 px).
3. Import the **Bluestock Logo** placeholder image in the header of each page.

---

## 📊 Step 5: Build All Dashboard Pages

### Page 1: Industry Overview
> [!NOTE]
> **Data Limitation Note**: Industry AUM history, SIP inflows, and AMC-level industry aggregates are **unavailable** in the source files. 
> **Design Strategy**: Create this page using the **6 available schemes** to summarize current asset sizes and allocations.

*   **Visual 1: KPI Cards (AUM & Risk)**:
    - **Card A**: Fields = `SUM('fact_scorecard'[aum_cr])`, rename label to "Tracked Assets under Management (AUM) in Cr".
    - **Card B**: Fields = `DISTINCTCOUNT('dim_fund'[amfi_code])`, label to "Active Schemes".
    - **Card C**: Fields = `[Average Score]`, label to "Average Portfolio Score".
*   **Visual 2: AUM by AMC (Donut Chart)**:
    - Legend: `dim_fund[fund_house]`
    - Values: `SUM('fact_scorecard'[aum_cr])`
    - Formatting: Enable category labels and detail percentages.
*   **Visual 3: Schemes List Table**:
    - Columns: `dim_fund[fund_house]`, `dim_fund[scheme_name]`, `dim_fund[category]`, `fact_scorecard[aum_cr]`.

### Page 2: Fund Performance (Core Page)
*   **Visual 1: Return vs. Risk Scatter Plot**:
    - Legend / Details: `dim_fund[scheme_name]`
    - X-Axis: `[Annualized Volatility]` (DAX Measure, format as %)
    - Y-Axis: `AVERAGE('fact_scorecard'[cagr_3y])` (3-Year CAGR, format as %)
    - Size: `SUM('fact_scorecard'[aum_cr])` (AUM in Cr)
    - Color Saturation: `[Average Score]` (Cmap: Coolwarm)
*   **Visual 2: Fund Scorecard Table**:
    - Columns: `dim_fund[amfi_code]`, `dim_fund[scheme_name]`, `fact_scorecard[overall_scorecard_score]`, `fact_scorecard[cagr_3y]`, `fact_scorecard[sharpe_ratio]`, `fact_scorecard[max_drawdown]`, `fact_scorecard[expense_ratio_percent]`.
    - Sorting: Sort Descending by `overall_scorecard_score`.
*   **Visual 3: NAV vs. Benchmark Performance (Line Chart)**:
    - Shared Axis (X-Axis): `fact_nav[date]` (hierarchical or continuous)
    - Y-Axis Values: `[Cumulative Growth]` and `[Benchmark Cumulative Growth]`
    - Legend: `dim_fund[scheme_name]` and `fact_nifty_benchmarks[benchmark_name]`
*   **Visual 4: Slicers (Sidebar)**:
    - Slicer A: `dim_fund[fund_house]` (Checkbox List)
    - Slicer B: `dim_fund[category]` (Dropdown)

### Page 3: Investor Analytics (Omitted/Placeholder)
> [!WARNING]
> **Data Omission Notice**: Investor transaction details by state, age-group SIP distributions, and city tiers are **unavailable**.
> **Design Strategy**: Create a single text panel displaying a **"Data Omission Notice: Demographics and transactions details are unavailable"** to maintain absolute data integrity.

### Page 4: SIP & Market Trends (Omitted/Placeholder)
> [!WARNING]
> **Data Omission Notice**: Monthly SIP inflows, category inflow heatmaps, and category net flows are **unavailable**.
> **Design Strategy**: Create a single text panel displaying a **"Data Omission Notice: Category-wise monthly inflows and SIP time-series are unavailable"**.

---

## 💾 Step 6: Interactivity & Navigation

1. **Drill-Through Action**:
   - Create a separate detail page named **"NAV Detail"**.
   - Drag `dim_fund[amfi_code]` into the **Drill-through fields** panel.
   - Design a table on this page showing `fact_nav[date]`, `fact_nav[nav]`, and `fact_nav[daily_return]` so the user can right-click any fund on Page 2 and select "Drillthrough -> NAV Detail".
2. **Tooltips**:
   - Enable tooltip hover boxes on the Scatter Plot and Line Chart, displaying name, score, and volatility.
3. **Cross-Filtering**:
   - Ensure clicking a slice in the "AUM by AMC" donut chart cross-filters the scorecard table.
4. **Navigation Buttons**:
   - Insert Page Navigation buttons under the **Insert -> Buttons -> Page Navigator** ribbon item. Place them in the sidebar.

---

## 📤 Step 7: Exporting Deliverables

1. **Export `.pbix` File**:
   - Save the file as `bluestock_mf_dashboard.pbix` in the project root directory.
2. **Export `Dashboard.pdf`**:
   - In Power BI Desktop, click **File -> Export -> Export to PDF**.
   - Save the file as `reports/Dashboard.pdf`.
3. **Export PNG Page Images**:
   - Open each page in Power BI Desktop.
   - Click **File -> Save As** and choose **PNG** (or take high-resolution screenshots of each page).
   - Save the images as:
     - `reports/page1_industry_overview.png`
     - `reports/page2_fund_performance.png`
     - `reports/page3_investor_analytics.png`
     - `reports/page4_sip_market_trends.png`
