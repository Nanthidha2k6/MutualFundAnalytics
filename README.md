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
| **Day 1** | Data Ingestion + Live NAV Fetch | ✅ Complete |
| **Day 2** | Data Cleaning + Processing Pipeline | 🔜 Planned |
| **Day 3** | SQL Analysis + Schema Design | 🔜 Planned |
| **Day 4** | Advanced Analytics + Notebooks | 🔜 Planned |
| **Day 5** | Report Generation + Export | 🔜 Planned |

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

**Nanthidha V N** — Data Analytics Portfolio Project
Python 3.10+ | Streamlit | Plotly | MFAPI

---

## 📜 License

This project is licensed under the **MIT License** — free to use, modify, and distribute.

---

<div align="center">

**Built with Python for learning Financial Data Analytics**

⭐ *Star this repo if it helped you learn!* ⭐

</div>
