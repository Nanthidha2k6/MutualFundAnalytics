-- ========================================================
--   Mutual Fund Analytics - Day 2: Analytical SQL Queries
--   File   : sql/queries.sql
--   Author : Student Project
--   Purpose: Implement 10 required analytical SQL queries
--            against the SQLite star schema database.
-- ========================================================

-- NOTE: Because raw files for transactions (investor_transactions.csv) and 
-- performance (scheme_performance.csv) were not provided in the repository, 
-- the tables fact_transactions, fact_performance, and fact_aum are empty. 
-- Consequently, queries depending on these tables will return empty results.
-- This limitation is noted in the comments for each affected query.

-- --------------------------------------------------------
-- QUERY 1: Top 5 funds by AUM
-- --------------------------------------------------------
-- Description: Retrieves the top 5 mutual fund schemes sorted by AUM.
-- Status: RETURNS EMPTY due to missing source data in fact_aum.
-- --------------------------------------------------------
SELECT 
    f.amfi_code,
    f.scheme_name,
    f.fund_house,
    f.category,
    a.aum AS aum_in_crores
FROM fact_aum a
JOIN dim_fund f ON a.fund_key = f.fund_key
ORDER BY a.aum DESC
LIMIT 5;


-- --------------------------------------------------------
-- QUERY 2: Average NAV per month
-- --------------------------------------------------------
-- Description: Computes the average NAV for each mutual fund scheme 
--              grouped by year and month.
-- Status: OPERATIONAL (queries fact_nav and dim_date).
-- --------------------------------------------------------
SELECT 
    f.amfi_code,
    f.scheme_name,
    d.year,
    d.month,
    d.month_name,
    ROUND(AVG(n.nav), 4) AS average_nav,
    COUNT(n.nav_key) AS trading_days_count
FROM fact_nav n
JOIN dim_fund f ON n.fund_key = f.fund_key
JOIN dim_date d ON n.date_key = d.date_key
GROUP BY f.fund_key, d.year, d.month
ORDER BY f.scheme_name, d.year, d.month;


-- --------------------------------------------------------
-- QUERY 3: SIP year-over-year growth
-- --------------------------------------------------------
-- Description: Computes the total amount invested via SIP each year 
--              and calculates the Year-over-Year (YoY) growth percentage.
-- Status: RETURNS EMPTY due to missing source data in fact_transactions.
-- --------------------------------------------------------
WITH sip_by_year AS (
    SELECT 
        d.year,
        SUM(t.amount) AS total_sip_amount
    FROM fact_transactions t
    JOIN dim_date d ON t.date_key = d.date_key
    WHERE t.transaction_type = 'SIP'
    GROUP BY d.year
)
SELECT 
    s1.year,
    s1.total_sip_amount,
    s2.total_sip_amount AS prev_year_sip_amount,
    ROUND(
        CASE 
            WHEN s2.total_sip_amount IS NULL THEN NULL
            ELSE ((s1.total_sip_amount - s2.total_sip_amount) / s2.total_sip_amount) * 100
        END, 
        2
    ) AS yoy_growth_percentage
FROM sip_by_year s1
LEFT JOIN sip_by_year s2 ON s1.year = s2.year + 1
ORDER BY s1.year;


-- --------------------------------------------------------
-- QUERY 4: Transactions by state
-- --------------------------------------------------------
-- Description: Aggregates total transaction count, total investment 
--              amount, and average investment size by investor state.
-- Status: RETURNS EMPTY due to missing source data in fact_transactions.
-- --------------------------------------------------------
SELECT 
    t.investor_state,
    COUNT(t.transaction_key) AS transaction_count,
    SUM(t.amount) AS total_investment_amount,
    ROUND(AVG(t.amount), 2) AS average_transaction_amount
FROM fact_transactions t
GROUP BY t.investor_state
ORDER BY total_investment_amount DESC;


-- --------------------------------------------------------
-- QUERY 5: Funds with expense_ratio < 1%
-- --------------------------------------------------------
-- Description: Lists all schemes with an expense ratio below 1.0%.
-- Status: RETURNS EMPTY due to missing source data in fact_performance.
-- --------------------------------------------------------
SELECT 
    f.amfi_code,
    f.scheme_name,
    f.fund_house,
    p.expense_ratio
FROM fact_performance p
JOIN dim_fund f ON p.fund_key = f.fund_key
WHERE p.expense_ratio < 1.0
ORDER BY p.expense_ratio ASC;


-- --------------------------------------------------------
-- QUERY 6: Top 5 funds by 1-year return
-- --------------------------------------------------------
-- Description: Lists the top 5 mutual fund schemes based on 1-year return.
-- Status: RETURNS EMPTY due to missing source data in fact_performance.
-- --------------------------------------------------------
SELECT 
    f.amfi_code,
    f.scheme_name,
    f.category,
    p.return_1y AS return_1y_percentage
FROM fact_performance p
JOIN dim_fund f ON p.fund_key = f.fund_key
ORDER BY p.return_1y DESC
LIMIT 5;


-- --------------------------------------------------------
-- QUERY 7: Average expense ratio by category
-- --------------------------------------------------------
-- Description: Calculates the average expense ratio across different 
--              fund categories (e.g. Equity, Debt).
-- Status: RETURNS EMPTY due to missing source data in fact_performance.
-- --------------------------------------------------------
SELECT 
    f.category,
    ROUND(AVG(p.expense_ratio), 4) AS average_expense_ratio,
    COUNT(p.performance_key) AS fund_count
FROM fact_performance p
JOIN dim_fund f ON p.fund_key = f.fund_key
GROUP BY f.category
ORDER BY average_expense_ratio ASC;


-- --------------------------------------------------------
-- QUERY 8: Total redemptions by month
-- --------------------------------------------------------
-- Description: Computes the total redemption amount and transaction 
--              counts grouped by year and month.
-- Status: RETURNS EMPTY due to missing source data in fact_transactions.
-- --------------------------------------------------------
SELECT 
    d.year,
    d.month,
    d.month_name,
    SUM(t.amount) AS total_redemption_amount,
    COUNT(t.transaction_key) AS redemption_count
FROM fact_transactions t
JOIN dim_date d ON t.date_key = d.date_key
WHERE t.transaction_type = 'Redemption'
GROUP BY d.year, d.month
ORDER BY d.year, d.month;


-- --------------------------------------------------------
-- QUERY 9: Fund house with highest average AUM
-- --------------------------------------------------------
-- Description: Identifies the fund house with the highest average 
--              Assets Under Management (AUM) across all its schemes.
-- Status: RETURNS EMPTY due to missing source data in fact_aum.
-- --------------------------------------------------------
SELECT 
    f.fund_house,
    ROUND(AVG(a.aum), 2) AS average_aum_in_crores,
    COUNT(a.aum_key) AS fund_count
FROM fact_aum a
JOIN dim_fund f ON a.fund_key = f.fund_key
GROUP BY f.fund_house
ORDER BY average_aum_in_crores DESC
LIMIT 1;


-- --------------------------------------------------------
-- QUERY 10: Highest NAV growth over time / best performing funds
-- --------------------------------------------------------
-- Description: Measures NAV growth from the earliest available date to the
--              latest date for each scheme, demonstrating long-term return.
-- Status: OPERATIONAL (queries fact_nav and dim_date).
-- --------------------------------------------------------
WITH start_end_dates AS (
    -- Get earliest and latest date keys for each fund
    SELECT 
        fund_key,
        MIN(date_key) AS start_date_key,
        MAX(date_key) AS end_date_key
    FROM fact_nav
    GROUP BY fund_key
),
nav_growth AS (
    -- Fetch NAV and dates for start and end points and calculate growth %
    SELECT 
        se.fund_key,
        f.amfi_code,
        f.scheme_name,
        n_start.nav AS start_nav,
        d_start.full_date AS start_date,
        n_end.nav AS end_nav,
        d_end.full_date AS end_date,
        ROUND(((n_end.nav - n_start.nav) / n_start.nav) * 100, 2) AS nav_growth_percentage
    FROM start_end_dates se
    JOIN dim_fund f ON se.fund_key = f.fund_key
    JOIN fact_nav n_start ON se.fund_key = n_start.fund_key AND se.start_date_key = n_start.date_key
    JOIN dim_date d_start ON n_start.date_key = d_start.date_key
    JOIN fact_nav n_end ON se.fund_key = n_end.fund_key AND se.end_date_key = n_end.date_key
    JOIN dim_date d_end ON n_end.date_key = d_end.date_key
)
SELECT 
    amfi_code,
    scheme_name,
    start_date,
    start_nav,
    end_date,
    end_nav,
    nav_growth_percentage
FROM nav_growth
ORDER BY nav_growth_percentage DESC;
