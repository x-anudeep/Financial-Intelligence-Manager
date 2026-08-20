# Architecture

The platform uses deterministic backend services for financial calculations and anomaly detection.

## Backend

- FastAPI exposes REST endpoints.
- SQLAlchemy persists companies, periods, metrics, anomalies, documents, and chunks.
- Pandas handles CSV/XLSX ingestion and normalization.
- Financial calculations live in `backend/app/financial_engine`.
- Explainable exception detection lives in `backend/app/anomaly_engine`.
- RAG services live in `backend/app/rag` and use local TF-IDF retrieval for no-key operation.
- AI services live behind `backend/app/ai` abstractions.

## Frontend

- React/TypeScript/Vite powers the analyst dashboard.
- TanStack Query owns API state and loading/error flows.
- Recharts renders financial, risk, and comparison visualizations.
- Tailwind provides a restrained institutional UI.

## AI Boundary

LLMs never calculate ratios, growth rates, or anomaly thresholds. The AI layer explains and summarizes data already calculated by backend services and cites retrieved document chunks when document context is used.
