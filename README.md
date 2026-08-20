# Financial Statement Intelligence & Exception Detection Platform

Analyst decision-support software for fetching or uploading company financial data, calculating financial metrics, detecting exceptions, visualizing trends, and retrieving supporting context from uploaded documents.

The platform does not detect fraud or make investment/credit decisions. It identifies unusual financial movements that require analyst review.

## Business Problem

Middle-market analysts often receive financial statements and supporting documents in inconsistent formats. This MVP helps answer whether revenue is growing, margins are deteriorating, cash is weakening, receivables are outpacing sales, debt is rising faster than EBITDA, and what document context may explain an anomaly.

## Architecture

See [docs/architecture.md](docs/architecture.md).

- Backend: FastAPI, SQLAlchemy, Pydantic, Pandas, NumPy, scikit-learn
- Frontend: React, TypeScript, Vite, Tailwind CSS, Recharts, TanStack Query
- Database: SQLite for local development, with PostgreSQL-ready SQLAlchemy boundaries
- RAG: local TF-IDF retrieval fallback for dependable no-key demos
- AI: optional LLM abstraction controlled by `GEMINI_API_KEY` or `OPENAI_API_KEY`
- Infrastructure: Docker and Docker Compose

## Features

- CSV/XLSX financial upload and validation
- Financial label normalization
- Real-data agent for US public companies using SEC EDGAR CompanyFacts
- CSV/XLSX upload for custom financial data
- Deterministic financial ratio engine
- Explainable rule-based anomaly detection
- Lightweight z-score statistical detection when enough history exists
- Portfolio risk overview and severity distribution
- Company financial intelligence page
- Exception center with filters
- Company comparison table and scatter plot
- PDF/TXT supporting document upload
- Retrieval with source references
- Analyst copilot that works without an AI key
- "Find Context" workflow for anomalies

## Tech Stack

Frontend: React, TypeScript, Vite, Tailwind CSS, Recharts, TanStack Query.

Backend: Python, FastAPI, Pydantic, SQLAlchemy, Pandas, NumPy, scikit-learn, pypdf.

## Setup

```bash
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cd frontend
npm install
```

## Environment Variables

```bash
DATABASE_URL=sqlite:///./financial_intelligence.db
FRONTEND_ORIGIN=http://localhost:5173
LLM_PROVIDER=auto
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
GEMINI_API_KEY=
GEMINI_MODEL=gemini-1.5-flash
VITE_API_BASE_URL=
```

Do not commit real API keys. `.env` is ignored.

## Running Locally

One-command launch:

```bash
BACKEND_PORT=8010 FRONTEND_PORT=5173 ./scripts/launch_local.sh
```

Then open `http://localhost:5173`.

Backend:

```bash
source .venv/bin/activate
cd backend
uvicorn app.main:app --reload --port 8010
```

Frontend:

```bash
cd frontend
npm run dev
```

Open `http://localhost:5173` and use the Real Data Agent. Try `Apple`, `JPM`, or `Bank of America`.

## Docker

SQLite demo mode:

```bash
./scripts/launch_docker.sh
```

The frontend runs on `http://localhost:5173`; the API runs on `http://localhost:8000`.

PostgreSQL plus pgvector-ready database:

```bash
USE_POSTGRES=1 ./scripts/launch_docker.sh
```

The PostgreSQL service uses the `pgvector/pgvector:pg16` image. The MVP retrieval layer still has a local TF-IDF fallback so demos work without external embedding credentials.

## Data Model

Core tables:

- Company
- FinancialPeriod
- FinancialMetric
- Anomaly
- Document
- DocumentChunk

## Financial Metrics

Metrics are calculated deterministically in Python. See [docs/financial_metrics.md](docs/financial_metrics.md).

Examples:

- Revenue growth: `(current_revenue - prior_revenue) / prior_revenue`
- EBITDA margin: `EBITDA / revenue`
- Debt / EBITDA: `total_debt / EBITDA`
- Operating cash conversion: `operating_cash_flow / EBITDA`
- Working capital: `current_assets - current_liabilities`

Missing values and zero denominators return `null`.

## Anomaly Methodology

See [docs/anomaly_methodology.md](docs/anomaly_methodology.md).

The rule engine stores current values, prior values, calculated changes, severity, evidence, and suggested review steps. Statistical z-score detection is used only when enough history exists.

## AI/RAG Architecture

Uploaded PDF/TXT documents are extracted, chunked, stored, and searched with local semantic retrieval. Responses include source references. The AI layer can summarize and explain validated structured data, but it never overrides deterministic calculations.

If no LLM API key is configured, the copilot still returns structured findings and retrieved sources.

With a Gemini or OpenAI API key configured, the copilot uses the LLM for narrative synthesis over the deterministic structured findings and retrieved document sources.

## API Overview

See [docs/api.md](docs/api.md).

## Demo Walkthrough

See [docs/demo_walkthrough.md](docs/demo_walkthrough.md).

Recommended demo:

1. Open the dashboard.
2. Type `Apple`, `JPM`, or `Bank of America` in the Real Data Agent.
3. Open the company page.
4. Inspect financial charts, ratios, and anomalies.
5. Upload a supporting PDF/TXT document.
6. Click `Find Context`.
7. Ask the copilot a simple question such as `What are the biggest risks?`

For a simple presentation script, see [docs/project_brief_for_demo.md](docs/project_brief_for_demo.md).

## Upload Format

See [docs/upload_format.md](docs/upload_format.md). A generated sample file is available at [data/sample_financials.csv](data/sample_financials.csv).

## Testing

Backend:

```bash
source .venv/bin/activate
PYTHONPATH=backend pytest backend/app/tests
```

Frontend:

```bash
cd frontend
npm run build
```

## Limitations

- SQLite is the default local database.
- The local RAG fallback uses TF-IDF rather than hosted embeddings.
- The LLM abstraction is intentionally conservative in this MVP.
- Synthetic data is realistic for demonstration but not a substitute for audited statements.
- The illustrative risk views are not credit ratings or investment recommendations.

## Future Improvements

- PostgreSQL and pgvector deployment profile
- Async background document processing
- OpenAI embeddings and richer model-backed synthesis
- Authentication and role-based access
- Expanded financial statement parser
- More granular quarterly-period support
- Exportable analyst reports

## Voice Agent Future Enhancement

Voice is intentionally out of scope for the four MVP phases. A future voice agent can call the same backend analyst tools:

- `get_company_financials`
- `get_company_metrics`
- `get_company_anomalies`
- `get_ratio_history`
- `compare_companies`
- `search_company_documents`

Example future voice requests: "Summarize this company," "Show the biggest anomaly," "Compare Titan and Apex," or "What does management say about receivables?"
