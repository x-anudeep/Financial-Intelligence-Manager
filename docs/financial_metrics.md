# Financial Metrics

All ratios are calculated deterministically in the backend.

- Revenue growth: `(current_revenue - prior_revenue) / prior_revenue`
- EBITDA margin: `EBITDA / revenue`
- Gross margin: `gross_profit / revenue`
- Net margin: `net_income / revenue`
- Current ratio: `current_assets / current_liabilities`
- Quick ratio: `(current_assets - inventory) / current_liabilities`
- Debt / EBITDA: `total_debt / EBITDA`
- Interest coverage: `EBIT / interest_expense`
- Operating cash conversion: `operating_cash_flow / EBITDA`
- Working capital: `current_assets - current_liabilities`

Missing values and zero denominators return `null`.
