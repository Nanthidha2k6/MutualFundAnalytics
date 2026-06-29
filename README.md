<div align="center">

# 📊 Mutual Fund Analytics Platform

### A Professional-Grade Python Analytics Suite for Indian Mutual Funds

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive%20Charts-3D4FC9?style=flat-square&logo=plotly&logoColor=white)](https://plotly.com/)
[![MFAPI](https://img.shields.io/badge/MFAPI-Live%20NAV%20Data-green?style=flat-square)](https://mfapi.in/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

**Live NAV Ingestion • Data Quality Validation • Interactive Analytics Dashboard • Risk & Performance Insights**

---

</div>

## 🌟 What Is This Project?

**Mutual Fund Analytics** is a full-stack data analytics project built entirely in Python. It automates the end-to-end pipeline from raw NAV data ingestion to a professional Bloomberg-style fintech dashboard — all for free, using open APIs.

| Layer | What It Does |
|-------|-------------|
| 🔄 **Data Ingestion** | Fetches live NAV history from MFAPI for 6 large-cap funds |
| 🧹 **Data Validation** | Detects nulls, duplicates, schema issues & AMFI code mismatches |
| 📊 **Dashboard** | Streamlit app with 4 interactive pages, Plotly charts & KPI cards |
| 💡 **Insights Engine** | Auto-computes CAGR, Sharpe ratio, drawdown, volatility & more |

---

## 🚀 Quick Start (3 Commands)

```powershell
# 1. Go to the project folder
cd "MutualFundAnalytics"

# 2. Install all dependencies
pip install -r requirements.txt

# 3. Fetch live data + launch dashboard
python live_nav_fetch.py
streamlit run dashboard/streamlit_app.py
```

Open **`http://localhost:8501`** in your browser. That's it. ✅

---

## 📁 Project Structure

```
MutualFundAnalytics/
│
├── 📂 data/
│   ├── raw/                        ← Live NAV CSVs fetched from MFAPI
│   │   ├── live_nav_combined.csv   ← All 6 funds merged (19,882 rows)
│   │   ├── nav_118632_nippon_large_cap.csv
│   │   ├── nav_119092_axis_bluechip.csv
│   │   ├── nav_119551_sbi_bluechip.csv
│   │   ├── nav_120503_icici_bluechip.csv
│   │   ├── nav_120841_kotak_bluechip.csv
│   │   └── nav_125497_hdfc_top_100_direct.csv
│   └── processed/                  ← Cleaned data for downstream use
│
├── 📂 dashboard/                   ← Streamlit multi-page app
│   ├── streamlit_app.py            ← Main entry point (run this)
│   └── pages/
│       ├── fund_analysis.py        ← Single fund deep-dive
│       ├── nav_comparison.py       ← Multi-fund comparison
│       └── performance_insights.py ← Smart insights engine
│
├── 📂 frontend/                    ← Reusable UI components
│   ├── app.py                      ← Launcher shortcut
│   ├── components/
│   │   ├── charts.py               ← 5 Plotly chart builders
│   │   ├── metrics_cards.py        ← KPI cards, insight cards, badges
│   │   └── filters.py              ← Fund selectors, date filters
│   └── styles/
│       └── theme.css               ← Premium fintech CSS theme
│
├── 📂 notebooks/                   ← Jupyter EDA notebooks
├── 📂 sql/                         ← SQL queries and schema scripts
├── 📂 reports/                     ← Exported analytics reports
│
├── data_ingestion.py               ← CSV loader + quality validator
├── live_nav_fetch.py               ← MFAPI live data fetcher
├── requirements.txt                ← All Python dependencies
└── README.md                       ← You are here
```

---

## 📊 Dashboard Pages

### 🏠 Overview Page
The default landing page. At-a-glance summary of the entire portfolio.

- **6 KPI Cards** — Total Funds, Avg NAV, Highest NAV, Lowest NAV, Best Return, Total Records
- **Normalised Comparison Chart** — All funds rebased to 100 for fair comparison
- **Returns Summary Table** — Start NAV → Latest NAV → Return % for every fund
- **Global Period Filter** — Toggle 1M / 3M / 6M / 1Y / 3Y / All from the sidebar

---

### 🔍 Fund Analysis Page
Deep-dive into any single mutual fund.

| Feature | Details |
|---------|---------|
| Fund Selector | Dropdown with all 6 available funds |
| NAV Trend Chart | Spline curve with gradient fill, hover tooltips |
| Rolling Return Chart | Configurable N-day rolling return (7–365 days) |
| Period Returns | 1M / 3M / 6M / 1Y / Total return stat row |
| Risk Metrics | Annualised volatility, Sharpe ratio, Max drawdown |
| Auto-Insights | Risk profile, capital preservation score, performance grade |

---

### ⚖️ NAV Comparison Page
Side-by-side comparison of multiple funds.

| Feature | Details |
|---------|---------|
| Multi-Select | Pick any combination of funds to compare |
| Normalised Overlay Chart | Base=100 comparison for apples-to-apples view |
| Returns Bar Chart | Horizontal bar chart, green=positive / red=negative |
| Risk vs Return Scatter | Bubble chart — ideal funds are top-left (high return, low risk) |
| Detailed Returns Table | 1M / 3M / 6M / 1Y / Total returns side by side |

---

### 💡 Performance Insights Page
Auto-generated analytics and fund scorecard.

| Feature | Details |
|---------|---------|
| Champion Cards | Best Return, Lowest Return, Most Stable, Best Sharpe |
| Smart Insight Cards | 8 auto-labelled insights with colour-coded severity |
| Full Scorecard Table | CAGR, Volatility, Sharpe, Max Drawdown, Consistency % |
| Risk-Return Map | All funds plotted for portfolio-level risk analysis |
| Metric Guide | Built-in explainer for every metric |

---

## ⚙️ Detailed Setup

### Prerequisites

- Python **3.10 or higher**
- Internet connection (for live NAV fetch)
- ~500 MB disk space

### Step 1 — Clone the Repository

```bash
git clone https://github.com/your-username/MutualFundAnalytics.git
cd MutualFundAnalytics
```

### Step 2 — Create a Virtual Environment *(recommended)*

```powershell
# Windows
python -m venv venv
venv\Scripts\activate
```

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔄 Running the Scripts

### Fetch Live NAV Data

```bash
python live_nav_fetch.py
```

Connects to [MFAPI.in](https://mfapi.in/) and fetches NAV history for 6 funds.

**Output files created in `data/raw/`:**

| File | Fund | Records |
|------|------|---------|
| `nav_118632_nippon_large_cap.csv` | Nippon India Large Cap | 3,312 |
| `nav_119092_axis_bluechip.csv` | HDFC Money Market | 3,579 |
| `nav_119551_sbi_bluechip.csv` | Aditya Birla Sun Life PSU Debt | 3,250 |
| `nav_120503_icici_bluechip.csv` | Axis ELSS Tax Saver | 3,321 |
| `nav_120841_kotak_bluechip.csv` | quant Mid Cap | 3,315 |
| `nav_125497_hdfc_top_100_direct.csv` | SBI Small Cap | 3,105 |
| `live_nav_combined.csv` | **All 6 funds merged** | **19,882** |

---

### Validate Data Quality

```bash
python data_ingestion.py
```

Runs 6-section analysis across all CSVs in `data/raw/`:

| Section | What It Checks |
|---------|---------------|
| **A** | Auto-detects and loads all CSV files |
| **B** | Shape, dtypes, `.head()` for every file |
| **C** | Missing values, duplicates, naming issues, empty rows |
| **D** | Fund master — unique houses, categories, risk grades |
| **E** | AMFI scheme code cross-validation |
| **F** | Overall data quality summary report |

---

### Launch the Dashboard

```bash
streamlit run dashboard/streamlit_app.py
```

Opens at **`http://localhost:8501`**

---

## 🗄️ Day 2: SQLite Star Schema & SQL Analytics

Day 2 introduces a complete **data cleaning pipeline**, a **SQLite star schema design**, and a **SQL analytical query engine**.

### Architecture & Components

```
data/raw/                     → Raw data source (unmodified)
  ├── fund_master.csv
  └── live_nav_combined.csv
scripts/clean_data.py         → Standardizes, deduplicates, and forward-fills holidays/weekends
data/processed/               → Holds 10 cleaned CSV files (e.g. nav_history_cleaned.csv)
sql/schema.sql                → Star schema DDL for dimensions and facts
sql/create_schema.py          → Initializes bluestock_mf.db using SQLAlchemy
sql/load_cleaned_data.py      → Seeds dimension and fact tables, mapping natural keys
sql/queries.sql               → 10 analytical SQL queries against the star schema
data_dictionary.md            → Detailed schema and column documentation
day2_pipeline.py              → End-to-end orchestrator pipeline
bluestock_mf.db               → Final SQLite star schema database in project root
```

### Database Star Schema Design

The SQLite database `bluestock_mf.db` is built around a multi-dimensional star schema to optimize analytical queries:
- **Dimensions**:
  - `dim_fund`: Fund details and categories.
  - `dim_date`: Calendar date attributes (`date_key`, `full_date`, `day`, `month`, `month_name`, `quarter`, `year`, `week_of_year`).
- **Facts**:
  - `fact_nav`: Daily NAV records (linked to `dim_fund` and `dim_date`).
  - `fact_transactions` *(Created but empty)*: Investor transactions (SIP, Lumpsum, Redemption).
  - `fact_performance` *(Created but empty)*: Scheme return metrics and expense ratios.
  - `fact_aum` *(Created but empty)*: Fund Assets Under Management (AUM).

> [!NOTE]
> To maintain strict data integrity, the transaction, return, and AUM fact tables are left empty because their corresponding raw source files (`investor_transactions.csv` and `scheme_performance.csv`) are not part of the raw repository. These limitations are documented in `data_dictionary.md` and `sql/queries.sql`.

### How to Run the Day 2 Workflow

Run the end-to-end pipeline orchestrator using a single command:

```bash
python day2_pipeline.py
```

This command will:
1. Process and clean all raw CSVs, writing the outputs to `data/processed/`.
2. Initialize the SQLite database schema.
3. Seed `dim_fund`, `dim_date`, and `fact_nav`.
4. Execute the 10 analytical SQL queries and print formatted tables of the output in the console.

---

## 📦 Dependencies

| Library | Version | Purpose |
|---------|---------|---------|
| `pandas` | ≥ 2.0.0 | Data loading and manipulation |
| `numpy` | ≥ 1.24.0 | Numerical operations |
| `streamlit` | latest | Interactive web dashboard |
| `plotly` | ≥ 5.15.0 | Interactive charts and graphs |
| `requests` | ≥ 2.31.0 | HTTP API calls to MFAPI |
| `matplotlib` | ≥ 3.7.0 | Static plotting |
| `seaborn` | ≥ 0.12.0 | Statistical visualizations |
| `sqlalchemy` | ≥ 2.0.0 | Database ORM |
| `scipy` | ≥ 1.11.0 | Statistical analysis |
| `jupyter` | ≥ 1.0.0 | Notebook environment |

---

## 📐 Analytics Metrics Explained

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| **Total Return** | `(Last NAV / First NAV - 1) × 100` | Total gain/loss over the period |
| **CAGR** | `(Last/First)^(1/years) - 1` | Annualised compounded growth rate |
| **Volatility** | `std(daily_returns) × √252` | Annualised risk (lower = stabler) |
| **Sharpe Ratio** | `(Return - Rf) / Volatility` | Return per unit of risk (>1 = good) |
| **Max Drawdown** | `min((NAV - Rolling Max) / Rolling Max)` | Worst peak-to-trough fall |
| **Consistency** | `% months with positive return` | How reliably the fund grows |

> Risk-free rate assumed: **6.5% per annum** (approx. Indian T-bill rate)

---

## 🎨 UI Design System

The dashboard uses a custom premium CSS theme inspired by Bloomberg Terminal and Zerodha Console:

```
Background:  #f0f4f8  (soft blue-grey)
Sidebar:     #0f1b35 → #1a2f5e  (dark navy gradient)
Cards:       #ffffff with box-shadow + border-radius: 14px
Accent:      Blue / Green / Purple / Orange / Red / Teal
Typography:  Inter (Google Fonts) — weights 300–800
Charts:      Spline curves, gradient fills, unified hover tooltips
```

---

## 🗂️ Optional: Add Your Own CSV Datasets

Drop any CSV files into `data/raw/` and re-run `data_ingestion.py`.  
The script **auto-detects all CSVs** — no code changes needed.

For full AMFI validation, add:

| File | Required Columns |
|------|-----------------|
| `fund_master.csv` | `scheme_code`, `fund_house`, `category`, `risk` |
| `nav_history.csv` | `scheme_code`, `date`, `nav` |

---

## 📤 GitHub Submission Checklist

- [ ] `pip install -r requirements.txt` runs without errors
- [ ] `python live_nav_fetch.py` fetches all 6 schemes successfully
- [ ] `python data_ingestion.py` shows clean quality summary
- [ ] `streamlit run dashboard/streamlit_app.py` opens the dashboard
- [ ] `data/raw/live_nav_combined.csv` exists with 19,000+ rows
- [ ] All 4 dashboard pages load without errors
- [ ] Code is commented and beginner-friendly
- [ ] `requirements.txt` is present and complete

---

## 🗺️ Project Roadmap

| Day | Module | Status |
|-----|--------|--------|
| **Day 1** | Data Ingestion & Quality Validation | ✅ Complete |
| **Day 2** | Data Cleaning & Database Seed Pipeline | ✅ Complete |
| **Day 3** | Performance Analytics & Scorecard | ✅ Complete |
| **Day 4** | Exploratory Data Analysis (EDA) | ✅ Complete |
| **Day 5** | Portfolio Reporting & Export | 📅 In Progress |

---

## 🏆 Day 3: Performance Analytics & Scorecard

Day 3 adds professional-grade mutual fund performance and risk analysis, linear regression against benchmark indices, and a dynamic ranking scorecard.

### Key Implementation Features
1. **Benchmark Indices Ingestion**: Fetches real daily historical index prices and returns for **Nifty 50 (`^NSEI`)** and **Nifty 100 (`^CNX100`)** from the public Yahoo Finance Chart API.
2. **Verified Metadata**: Uses a verified metadata file (`data/raw/fund_metadata.csv`) containing public Assets Under Management (AUM) and Expense Ratios retrieved from **ValueResearchOnline** (as of June 2026), preventing data fabrication.
3. **Resilient Scorecard (0-100)**: Implements Min-Max ranking scaling with a robust weight-rescaling mechanism. If any fund-level metric (like expense ratio) is marked as `"Unavailable"`, active weights are automatically rescaled to sum to 100%.
4. **Calculated Risk & Performance Metrics**:
   - **CAGR**: 1-Year, 3-Year, and 5-Year CAGR computed using the closest date logic.
   - **Sharpe & Sortino Ratios**: Annualized using a 6.5% risk-free rate, with downside deviation calculated using negative daily return variance.
   - **Alpha, Beta, and Tracking Error**: Annualized metrics computed via linear regression against date-aligned daily index returns.
   - **Max Drawdowns**: Worst peak-to-trough drop details including Peak, Trough, and Recovery dates.
5. **Interactive Scorecard Page**: Integrated as a separate page in the Streamlit dashboard sidebar containing KPI leaderboard cards, structured data tables, Plotly bar charts, and growth comparisons.

### New Day 3 Components & Outputs
- **[NEW] [Performance_Analytics.ipynb](file:///c:/Users/hp/Desktop/AI AGENT2/MutualFundAnalytics/notebooks/Performance_Analytics.ipynb)**: Detailed step-by-step analytics notebook.
- **[NEW] [fund_metadata.csv](file:///c:/Users/hp/Desktop/AI AGENT2/MutualFundAnalytics/data/raw/fund_metadata.csv)**: Verified fund level AUM, expense ratios, and sources.
- **[NEW] [fund_scorecard.csv](file:///c:/Users/hp/Desktop/AI AGENT2/MutualFundAnalytics/data/processed/fund_scorecard.csv)**: Final scorecard metrics.
- **[NEW] [alpha_beta.csv](file:///c:/Users/hp/Desktop/AI AGENT2/MutualFundAnalytics/data/processed/alpha_beta.csv)**: Regression results.
- **[NEW] [benchmark_comparison.png](file:///c:/Users/hp/Desktop/AI AGENT2/MutualFundAnalytics/reports/benchmark_comparison.png)**: Cumulative returns plot.
- **[NEW] SQLite Tables**: Loaded tables `fund_scorecard`, `alpha_beta`, and `nifty_benchmarks` in `mutual_funds.db`.

---

## 🔍 Day 4: Exploratory Data Analysis (EDA)

Day 4 adds an advanced, institutional-grade Exploratory Data Analysis (EDA) suite based strictly on verified historical data.

### ⚠️ Day 4 Data Limitations & Missing Metrics
To maintain strict data integrity, the following datasets are explicitly documented as **Unavailable** and omitted from the code to avoid data fabrication:
- Historical AUM Time-Series (2022–2025)
- Monthly SIP Inflow Time-Series (2022–2025)
- Category-wise monthly inflow data
- Investor Demographics (Age Group, Gender)
- Geographic Distribution (State-Wise, T30 vs B30 Cities)
- Folio Count History
- Sector Allocation / Portfolio Holdings (`portfolio_holdings.csv`)

### Visualization & Insights Suite
We expanded the risk and performance analysis using the existing historical NAVs and Nifty benchmark returns to generate **15 advanced financial charts** (8 interactive Plotly charts, 7 Seaborn/Matplotlib charts) exported as publication-quality PNGs in the `reports/` directory:

1. **Daily NAV Trends (2022–2026)**: Overlay of NAV curves with shaded zones highlighting the **2023 Bull Run** and **2024 Market Corrections**.
2. **Normalized Cumulative Growth (2013–2026)**: Rebased growth from a base of 100 showing long-term compounding.
3. **Correlation Heatmap**: Daily returns correlation matrix between all 6 schemes.
4. **KDE Returns Distribution**: Analysis of daily return density, skewness, and kurtosis.
5. **Annualized 90-Day Rolling Volatility**: Running return variance tracking market risk shifts.
6. **Rolling 90-Day Beta**: Sensitivities against Nifty 50 showing portfolio risk dynamics.
7. **Running Drawdown Curves**: Run of declines from peak (%) showing crash depths and lengths.
8. **Risk-Return Profile**: Annualized Volatility vs. 3-Year CAGR scatter plot showing the efficient frontier.
9. **Monthly Seasonality Heatmap**: Average monthly returns (Months vs. Years) showing calendar anomalies.
10. **Outperformance Spread**: Cumulative return spread of Nippon Large Cap vs. Nifty 50.
11. **Drawdown Depth Boxplots**: Distribution of daily drawdown depths showing spread of corrections.
12. **Rolling 90-Day Correlation**: Dynamic relationship between equity schemes and Nifty 50.
13. **Return Autocorrelation (ACF)**: Analysis of serial correlation for lags 1 to 20 days.
14. **Bivariate Returns Scatter Matrix (Pairplot)**: Joint return distributions between equity schemes.
15. **Tail Risk Comparison**: Bar comparison of 95% and 99% daily Value-at-Risk (VaR) & Conditional VaR (CVaR).

The Jupyter Notebook **[EDA_Analysis.ipynb](file:///c:/Users/hp/Desktop/AI AGENT2/MutualFundAnalytics/notebooks/EDA_Analysis.ipynb)** contains all 15 cells and includes **15 well-written Markdown insight sections** (one for each visualization) explaining the market findings.

---

## 📊 Power BI Dashboard Developer Guide

A complete developer blueprint is provided in **[power_bi_setup.md](file:///c:/Users/hp/Desktop/AI%20AGENT2/MutualFundAnalytics/power_bi_setup.md)** to recreate the **Bluestock Mutual Fund Analytics Dashboard** in Power BI Desktop.

### 🗃️ 1. Power BI-Ready Datasets
The datasets are pre-packaged and available as clean CSV files inside **`data/processed/power_bi/`**:
- **`dim_fund.csv`**: Fund Master table containing AMC metadata and risk profiles.
- **`fact_nav.csv`**: Time-series table containing daily NAV records and daily return percentages.
- **`fact_nifty_benchmarks.csv`**: Time-series table containing daily close prices and daily returns for Nifty 50 and Nifty 100.
- **`fact_scorecard.csv`**: Performance indicator summary containing CAGR (1Y/3Y/5Y), Sharpe, Sortino, drawdowns, and overall scorecard scores.
- **`fact_alpha_beta.csv`**: Risk analytics summary containing Alpha, Beta, and Tracking Errors.

### 🔗 2. Star Schema & Relationships
Configure the relationships inside Power BI's Model View:
- **`dim_fund[amfi_code]` (1) <---> `fact_nav[amfi_code]` (*)** (Active, Single direction)
- **`dim_fund[amfi_code]` (1) <---> `fact_scorecard[amfi_code]` (1)** (Active, Single direction)
- **`dim_fund[amfi_code]` (1) <---> `fact_alpha_beta[amfi_code]` (*)** (Active, Single direction)

### 🧮 3. Required DAX Measures
Create the following DAX measures in Power BI:
- **Latest NAV**:
  ```dax
  Latest NAV = CALCULATE(MAX('fact_nav'[nav]), LASTDATE('fact_nav'[date]))
  ```
- **Cumulative Growth (Base = 100)**:
  ```dax
  Cumulative Growth = 
  VAR FirstDateVal = CALCULATE(MIN('fact_nav'[date]), ALLSELECTED('fact_nav'[date]))
  VAR FirstNAV = CALCULATE(SUM('fact_nav'[nav]), 'fact_nav'[date] = FirstDateVal)
  VAR CurrentNAV = [Latest NAV]
  RETURN
  DIVIDE(CurrentNAV, FirstNAV, 0) * 100
  ```
- **Annualized Volatility**:
  ```dax
  Annualized Volatility = STDEV.S('fact_nav'[daily_return]) * SQRT(252)
  ```
- **Average Score KPI**:
  ```dax
  Average Score = AVERAGE('fact_scorecard'[overall_scorecard_score])
  ```
- **Benchmark Cumulative Growth (Base = 100)**:
  ```dax
  Benchmark Cumulative Growth = 
  VAR FirstDateVal = CALCULATE(MIN('fact_nifty_benchmarks'[date]), ALLSELECTED('fact_nifty_benchmarks'[date]))
  VAR FirstClose = CALCULATE(SUM('fact_nifty_benchmarks'[close]), 'fact_nifty_benchmarks'[date] = FirstDateVal)
  VAR CurrentClose = SUM('fact_nifty_benchmarks'[close])
  RETURN
  DIVIDE(CurrentClose, FirstClose, 0) * 100
  ```

### 📋 4. Page Layout & Visual Mappings
- **Page 1: Industry Overview**:
  - **KPI Cards**: Tracked AUM (`SUM(fact_scorecard[aum_cr])`), active scheme counts (`DISTINCTCOUNT(dim_fund[amfi_code])`), and portfolio scorecard averages.
  - **AUM by AMC Donut Chart**: Legend = `dim_fund[fund_house]`, Values = `SUM(fact_scorecard[aum_cr])`.
- **Page 2: Fund Performance**:
  - **Risk-Return Scatter Bubble Plot**: X-Axis = `[Annualized Volatility]`, Y-Axis = `AVERAGE(fact_scorecard[cagr_3y])`, Size = `SUM(fact_scorecard[aum_cr])`, Details = `dim_fund[scheme_name]`. (Reference image: **[dashboard_scorecard_view.png](file:///c:/Users/hp/Desktop/AI%20AGENT2/MutualFundAnalytics/reports/dashboard_scorecard_view.png)**).
  - **Fund Scorecard Grid Table**: AMFI code, Scheme Name, Overall Score, 3Y CAGR, Sharpe, Max Drawdown, Expense Ratio.
  - **NAV vs Index Performance Line Chart**: Shared X-Axis = `fact_nav[date]`, Y-Axis = `[Cumulative Growth]` & `[Benchmark Cumulative Growth]`.
  - **Slicers**: Filters for Fund House (AMCs) and Fund Category.
- **Pages 3 & 4 (Data Omissions)**:
  - Display clean "Data Omission Notice" text cards for **Investor Analytics** and **SIP & Market Trends** pages to explain the missing source data limitations.

### ⚠️ 5. Known Data Limitations (No Fabrication)
Due to strict requirements against synthetic data generation, the following visuals cannot be completed because their raw sources are missing from the project repository:
- Industry-wide AUM history (2022–2025)
- Monthly AMC SIP inflows
- Investor demographic splits (age distribution, average SIP by age, gender splits)
- Geographic sales (SIP amount by state, T30 vs B30 cities)
- Folio count history

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---------|-----|
| `No such file or directory: data_ingestion.py` | Run from inside `MutualFundAnalytics/` folder |
| `UnicodeEncodeError` in terminal | The script auto-fixes this via `sys.stdout.reconfigure` |
| Dates show `NaT` | Already fixed — script tries multiple date formats |
| Scheme timeout | Script retries 2× with 20s timeout automatically |
| Streamlit not found | Run `pip install streamlit` |
| Dashboard shows no data | Run `python live_nav_fetch.py` first |

---

## 👤 Author

**Nanthidha V N (Nanthidha2k6)** — Data Analytics Portfolio Project
Python 3.10+ | Streamlit | Plotly | MFAPI | SQLite

---

## 📜 License

This project is licensed under the **MIT License** — free to use, modify, and distribute.

---

<div align="center">

**Built with Python for learning Financial Data Analytics**

⭐ *Star this repo if it helped you learn!* ⭐

</div>
