# Anomaly Methodology

The rule engine is primary because analysts need explainable findings.

Implemented detectors include:

- Revenue decline
- EBITDA margin compression
- Receivables growing materially faster than revenue
- Inventory growing materially faster than sales
- Debt growing faster than EBITDA
- Significant cash deterioration
- Negative or weak operating cash flow conversion
- Weakening interest coverage
- Unusual expense spike
- Abnormal year-over-year movement using z-score where enough history exists
- Working-capital deterioration
- EBITDA growth materially lagging revenue growth

Every anomaly stores:

- Current and prior values
- Calculated change
- Rule triggered
- Severity
- Evidence text
- Suggested analyst review steps
- Method and supporting statistics where applicable

The system identifies exceptions requiring analyst review. It does not detect fraud, make investment recommendations, or determine financing eligibility.
