# Financial Intelligence Platform: Simple Project Brief

## What This Project Does

This project is a simple financial review dashboard.

It can:

- fetch real public-company financial data from SEC EDGAR.
- create a CSV from that data.
- display company financials in charts and KPI cards.
- calculate useful ratios.
- flag unusual movements as anomalies.
- let users upload supporting documents.
- search those documents for context behind an anomaly.

## What Problem It Solves

Financial analysts often receive company data in spreadsheets and documents. Reviewing everything manually takes time and important warning signs can be missed.

This project helps by:

- reducing manual spreadsheet review.
- showing key numbers in one dashboard.
- identifying unusual financial changes.
- giving evidence for each anomaly.
- connecting financial issues with supporting documents.

## Where AI Is Used

The project does not depend on AI for calculations.

The main financial work is deterministic:

- ratios are calculated in Python.
- anomaly rules are fixed and explainable.
- document search uses local TF-IDF retrieval.

An LLM is optional. If `GEMINI_API_KEY` is set, the app can use Gemini with the model from `GEMINI_MODEL`. If `OPENAI_API_KEY` is set, it can use OpenAI's Responses API with the model from `OPENAI_MODEL`.

The LLM only summarizes and explains:

- already-calculated financial metrics.
- already-detected anomalies.
- retrieved document context.

If no API key is configured, the app still works and returns structured rule-based answers.

## Why It Is Relevant

For a bank or finance team, this is useful as an analyst support tool. It does not replace analysts, make investment decisions, or detect fraud by itself. It helps analysts quickly find what needs review.

## Demo Flow

1. Type a company name such as `Apple`, `JPM`, or `Bank of America`.
2. The app fetches real SEC data and creates a CSV.
3. The dashboard updates with company metrics.
4. Open a company page.
5. Show charts, ratios, and anomalies.
6. Upload a support document.
7. Use `Find Context` or the copilot to connect anomalies with document text.

## Simple Pitch

This is a financial analyst helper. It turns company financial data into a dashboard, highlights unusual changes, and helps find document context behind those changes.
