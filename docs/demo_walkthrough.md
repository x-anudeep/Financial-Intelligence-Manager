# Simple Demo Walkthrough

1. Start the app with `BACKEND_PORT=8010 FRONTEND_PORT=5173 ./scripts/launch_local.sh`.
2. Open `http://localhost:5173`.
3. In the Real Data Agent, type a US public company name or ticker, for example `Apple`, `JPM`, or `Bank of America`.
4. The app fetches public SEC filing data, creates a CSV, stores the financial metrics, and refreshes the dashboard.
5. Open the company page.
6. Explain the top cards and charts:
   - normal companies show revenue, EBITDA, debt, cash, margin, and ratios.
   - banks show deposits, loans, net interest income, ROA, ROE, and efficiency ratio.
7. Show the anomaly timeline. Each anomaly has evidence and suggested review steps.
8. Upload a supporting PDF/TXT document if available.
9. Click `Find Context` on an anomaly to search documents for possible explanation.
10. Ask the copilot a simple question, for example `What are the biggest risks?`

## One-Minute Explanation

This project helps an analyst quickly review company financial data. Instead of manually reading many rows in a spreadsheet, the app fetches or uploads financial data, calculates key ratios, highlights unusual movements, and lets the user search supporting documents for context.

The important point is that the calculations and anomaly detection are rule-based and deterministic. The optional LLM only explains already-calculated findings in simple language.
