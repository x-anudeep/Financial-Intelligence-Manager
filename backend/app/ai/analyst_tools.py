from sqlalchemy.orm import Session

from app.rag.retrieval import search_company_documents
from app.services.anomalies import compare_companies, list_company_anomalies
from app.services.financials import company_metric_rows


def get_company_financials(db: Session, company_id: int) -> list[dict]:
    return company_metric_rows(db, company_id)


def get_company_metrics(db: Session, company_id: int) -> dict:
    rows = company_metric_rows(db, company_id)
    return rows[-1] if rows else {}


def get_company_anomalies(db: Session, company_id: int) -> list[dict]:
    return list_company_anomalies(db, company_id)


def get_ratio_history(db: Session, company_id: int, ratio: str) -> list[dict]:
    return [{"period": row["period"], ratio: row.get(ratio)} for row in company_metric_rows(db, company_id)]


def compare_company_set(db: Session, company_ids: list[int]) -> dict:
    return compare_companies(db, company_ids)


def search_documents(db: Session, company_id: int, query: str) -> list[dict]:
    return search_company_documents(db, company_id, query)
