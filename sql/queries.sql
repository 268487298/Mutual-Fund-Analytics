-- 1. Top 5 Mutual Funds by Latest AUM
SELECT fund_house, date, aum_crore, num_schemes
FROM fact_aum
WHERE date = (SELECT MAX(date) FROM fact_aum)
ORDER BY aum_crore DESC
LIMIT 5;
 
-- 2. Average NAV by Month
SELECT
    strftime('%Y-%m', date) AS month,
    AVG(nav) AS avg_nav
FROM fact_nav
GROUP BY month
ORDER BY month;
 
-- 3. SIP Inflow with YoY Growth
WITH base AS (
    SELECT
        date(
            '2022-01-01',
            '+' || ((month - 1) / 12) || ' years',
            '+' || ((month - 1) % 12) || ' months'
        ) AS month_date,
        sip_inflow_crore,
        LAG(sip_inflow_crore, 12) OVER (ORDER BY month) AS prior_year_inflow
    FROM fact_sip_industry
)
SELECT
    strftime('%Y-%m', month_date) AS month,
    sip_inflow_crore,
    prior_year_inflow,
    CASE WHEN prior_year_inflow IS NULL THEN NULL
         ELSE ROUND((sip_inflow_crore - prior_year_inflow) * 100.0 / prior_year_inflow, 2)
    END AS yoy_growth_pct
FROM base
ORDER BY month_date;

-- 4. Transaction Summary by State
SELECT state, COUNT(*) AS transaction_count,
    SUM(amount_inr) AS total_amount_inr,
    AVG(amount_inr) AS avg_amount_inr
FROM fact_transactions
GROUP BY state ORDER BY total_amount_inr DESC;

-- 5. Funds with Expense Ratio < 1%
SELECT amfi_code, fund_house, scheme_name, category, sub_category, expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct ASC;

-- 6. Average Return and Volatility by Fund Category
SELECT
    f.category,
    AVG(p.return_1yr_pct)   AS avg_return_1yr,
    AVG(p.std_dev_ann_pct)  AS avg_volatility
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
GROUP BY f.category
ORDER BY avg_return_1yr DESC;

-- 7. Top 5 Fund Houses by Latest AUM
SELECT fund_house, SUM(aum_crore) AS total_aum_crore
FROM fact_aum
WHERE date = (SELECT MAX(date) FROM fact_aum)
GROUP BY fund_house
ORDER BY total_aum_crore DESC
LIMIT 5;

-- 8. Transaction Volume by Payment Mode and City Tier
SELECT payment_mode, city_tier,
    COUNT(*) AS transaction_count,
    SUM(amount_inr) AS total_amount_inr
FROM fact_transactions
GROUP BY payment_mode, city_tier
ORDER BY total_amount_inr DESC;

-- 9. Portfolio Exposure by Sector
SELECT sector,
    SUM(weight_pct) AS total_weight_pct,
    COUNT(DISTINCT amfi_code) AS fund_count
FROM fact_portfolio
GROUP BY sector
ORDER BY total_weight_pct DESC;

-- 10. Low-Cost Funds with Above-Average Performance
WITH avg_return AS (
    SELECT AVG(return_1yr_pct) AS avg_return_1yr
    FROM fact_performance
)
SELECT f.amfi_code, f.fund_house, f.scheme_name,
    f.expense_ratio_pct, p.return_1yr_pct
FROM dim_fund f
JOIN fact_performance p ON f.amfi_code = p.amfi_code
CROSS JOIN avg_return
WHERE f.expense_ratio_pct < 1.0
  AND p.return_1yr_pct > avg_return.avg_return_1yr
ORDER BY p.return_1yr_pct DESC;