from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.financial import Company
from app.schemas.financial import CompanyDetail, CompanySummary
from app.services.financials import company_metric_rows, company_summary, ingest_upload
from app.services.seed import seed_database

router = APIRouter(prefix="/api")


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/seed")
def seed(db: Session = Depends(get_db)) -> dict:
    return seed_database(db)


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
    return summary


@router.post("/financials/upload")
async def upload_financials(file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict:
    try:
        content = await file.read()
        return ingest_upload(db, content, file.filename or "upload.csv")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
