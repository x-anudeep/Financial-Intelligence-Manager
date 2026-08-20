# API Overview

## Portfolio

- `GET /api/companies`
- `GET /api/companies/{company_id}`
- `GET /api/portfolio/risk`
- `GET /api/comparison?company_ids=1&company_ids=2`

## Financial Data

- `POST /api/seed`
- `POST /api/demo/reset`
- `POST /api/financials/upload`

## Anomalies

- `POST /api/anomalies/run`
- `GET /api/anomalies`
- `GET /api/companies/{company_id}/anomalies`
- `POST /api/anomalies/supporting-context`

## Documents and RAG

- `POST /api/companies/{company_id}/documents`
- `GET /api/companies/{company_id}/documents`
- `GET /api/companies/{company_id}/documents/search?q=receivables`

## Analyst Copilot

- `GET /api/companies/{company_id}/analyst-summary`
- `POST /api/assistant/ask`

All AI endpoints continue to return deterministic structured responses when `OPENAI_API_KEY` is not configured.
