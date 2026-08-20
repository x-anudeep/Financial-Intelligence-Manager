# Financial Statement Intelligence & Exception Detection Platform

A full-stack analyst decision-support platform for ingesting middle-market company financial statements, normalizing financial labels, calculating ratios deterministically, and visualizing financial trends.

Phase 1 includes the foundation, data model, synthetic dataset, CSV/XLSX ingestion, deterministic financial calculations, APIs, and a working React dashboard.

## Tech Stack

- Frontend: React, TypeScript, Vite, Tailwind CSS, Recharts, TanStack Query
- Backend: FastAPI, Pydantic, SQLAlchemy
- Data: Pandas, NumPy, scikit-learn-ready foundation
- Database: SQLite by default for local development
- Infrastructure: Docker and Docker Compose

## Setup

```bash
cp .env.example .env
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
cd frontend && npm install
```

## Running Locally

Backend:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm run dev
```

Open `http://localhost:5173`, then click `Seed Demo Data`.

## Docker

```bash
docker compose up --build
```

## API Overview

- `GET /api/health`
- `POST /api/seed`
- `GET /api/companies`
- `GET /api/companies/{company_id}`
- `POST /api/financials/upload`

## Data Model

Core tables:

- Company
- FinancialPeriod
- FinancialMetric

Anomaly, document, chunk, RAG, and AI analyst models are added in later phases.

## Financial Metrics

Financial calculations are performed by backend Python logic. LLMs are never used to calculate ratios or growth percentages. See [docs/financial_metrics.md](docs/financial_metrics.md).

## Uploads

CSV and XLSX uploads are supported. See [docs/upload_format.md](docs/upload_format.md).

## Testing

```bash
cd backend
pytest

cd frontend
npm run build
```

## Voice Agent Future Enhancement

Voice is intentionally out of scope for the MVP phases. A future voice agent can call the same analyst service functions and API boundaries used by the web application.
