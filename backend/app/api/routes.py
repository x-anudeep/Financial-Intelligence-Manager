from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.financial import Company
from app.schemas.anomaly import AnomalyOut, CompanyComparison, PortfolioRiskOverview
from app.schemas.document import AnalystAnswer, AnalystQuestion, DocumentOut, SupportingContextRequest
from app.schemas.financial import CompanyDetail, CompanySummary
from app.rag.retrieval import search_company_documents
from app.services.analyst import analyst_summary, answer_question, supporting_context_for_anomaly
from app.services.anomalies import compare_companies, list_anomalies, list_company_anomalies, portfolio_risk_overview, run_all_anomalies, run_company_anomalies
from app.services.documents import list_documents, upload_document
from app.services.financials import company_metric_rows, company_summary, ingest_upload
from app.services.seed import seed_database

router = APIRouter(prefix="/api")


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/seed")
def seed(db: Session = Depends(get_db)) -> dict:
    result = seed_database(db)
    result["anomaly_run"] = run_all_anomalies(db)
    return result


@router.get("/companies", response_model=list[CompanySummary])
def list_companies(db: Session = Depends(get_db)) -> list[dict]:
    companies = db.scalars(select(Company).order_by(Company.name)).all()
    return [company_summary(db, company) for company in companies]


@router.get("/companies/{company_id}", response_model=CompanyDetail)
def get_company(company_id: int, db: Session = Depends(get_db)) -> dict:
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    summary = company_summary(db, company)
    summary["metrics"] = company_metric_rows(db, company.id)
    summary["anomalies"] = list_company_anomalies(db, company.id)
    return summary


@router.post("/financials/upload")
async def upload_financials(file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict:
    try:
        content = await file.read()
        result = ingest_upload(db, content, file.filename or "upload.csv")
        result["anomaly_run"] = run_all_anomalies(db)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/anomalies/run")
def run_anomalies(db: Session = Depends(get_db)) -> dict:
    return run_all_anomalies(db)


@router.post("/companies/{company_id}/anomalies/run")
def run_company_anomaly_detection(company_id: int, db: Session = Depends(get_db)) -> list[dict]:
    return run_company_anomalies(db, company_id)


@router.get("/anomalies", response_model=list[AnomalyOut])
def get_anomalies(
    company_id: int | None = None,
    severity: str | None = None,
    anomaly_type: str | None = None,
    metric: str | None = None,
    db: Session = Depends(get_db),
) -> list[dict]:
    return list_anomalies(db, company_id, severity, anomaly_type, metric)


@router.get("/companies/{company_id}/anomalies", response_model=list[AnomalyOut])
def get_company_anomalies(company_id: int, db: Session = Depends(get_db)) -> list[dict]:
    return list_company_anomalies(db, company_id)


@router.get("/portfolio/risk", response_model=PortfolioRiskOverview)
def get_portfolio_risk(db: Session = Depends(get_db)) -> dict:
    return portfolio_risk_overview(db)


@router.get("/comparison", response_model=CompanyComparison)
def get_company_comparison(company_ids: list[int] = Query(default=[]), db: Session = Depends(get_db)) -> dict:
    if len(company_ids) < 2:
        raise HTTPException(status_code=400, detail="Select at least two companies to compare.")
    return compare_companies(db, company_ids)


@router.post("/companies/{company_id}/documents")
async def upload_supporting_document(company_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict:
    try:
        return upload_document(db, company_id, file.filename or "document.txt", await file.read())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/companies/{company_id}/documents", response_model=list[DocumentOut])
def get_documents(company_id: int, db: Session = Depends(get_db)):
    return list_documents(db, company_id)


@router.get("/companies/{company_id}/documents/search")
def search_documents(company_id: int, q: str, db: Session = Depends(get_db)) -> dict:
    return {"sources": search_company_documents(db, company_id, q)}


@router.get("/companies/{company_id}/analyst-summary", response_model=AnalystAnswer)
def get_analyst_summary(company_id: int, db: Session = Depends(get_db)) -> dict:
    try:
        return analyst_summary(db, company_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/assistant/ask", response_model=AnalystAnswer)
def ask_analyst(payload: AnalystQuestion, db: Session = Depends(get_db)) -> dict:
    return answer_question(db, payload.company_id, payload.question)


@router.post("/anomalies/supporting-context", response_model=AnalystAnswer)
def find_supporting_context(payload: SupportingContextRequest, db: Session = Depends(get_db)) -> dict:
    try:
        return supporting_context_for_anomaly(db, payload.anomaly_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
