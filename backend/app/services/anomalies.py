from collections import Counter, defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.anomaly_engine.detectors import SEVERITY_WEIGHT, detect_anomalies
from app.models.anomaly import Anomaly
from app.models.financial import Company
from app.services.financials import company_metric_rows, company_summary


def serialize_anomaly(item: Anomaly, company_name: str | None = None) -> dict:
    return {
        "id": item.id,
        "company_id": item.company_id,
        "company_name": company_name,
        "period": item.period,
        "anomaly_type": item.anomaly_type,
        "metric": item.metric,
        "severity": item.severity,
        "title": item.title,
        "description": item.description,
        "current_value": item.current_value,
        "previous_value": item.previous_value,
        "percentage_change": item.percentage_change,
        "evidence": item.evidence,
        "suggested_review": item.suggested_review,
        "anomaly_score": item.anomaly_score,
        "method": item.method,
        "supporting_statistics": item.supporting_statistics,
    }


def run_company_anomalies(db: Session, company_id: int) -> list[dict]:
    company = db.get(Company, company_id)
    if not company:
        return []
    db.query(Anomaly).filter(Anomaly.company_id == company_id).delete()
    rows = company_metric_rows(db, company_id)
    findings = detect_anomalies(rows)
    for finding in findings:
        db.add(Anomaly(company_id=company_id, **finding))
    db.commit()
    return list_company_anomalies(db, company_id)


def run_all_anomalies(db: Session) -> dict:
    company_ids = db.scalars(select(Company.id)).all()
    total = 0
    for company_id in company_ids:
        total += len(run_company_anomalies(db, company_id))
    return {"companies": len(company_ids), "anomalies": total}


def list_company_anomalies(db: Session, company_id: int) -> list[dict]:
    company = db.get(Company, company_id)
    rows = db.scalars(select(Anomaly).where(Anomaly.company_id == company_id).order_by(Anomaly.period, Anomaly.severity)).all()
    return [serialize_anomaly(item, company.name if company else None) for item in rows]


def list_anomalies(db: Session, company_id: int | None = None, severity: str | None = None, anomaly_type: str | None = None, metric: str | None = None) -> list[dict]:
    stmt = select(Anomaly, Company.name).join(Company, Company.id == Anomaly.company_id)
    if company_id:
        stmt = stmt.where(Anomaly.company_id == company_id)
    if severity:
        stmt = stmt.where(Anomaly.severity == severity)
    if anomaly_type:
        stmt = stmt.where(Anomaly.anomaly_type == anomaly_type)
    if metric:
        stmt = stmt.where(Anomaly.metric == metric)
    rows = db.execute(stmt.order_by(Anomaly.created_at.desc())).all()
    return [serialize_anomaly(item, company_name) for item, company_name in rows]


def portfolio_risk_overview(db: Session) -> dict:
    companies = db.scalars(select(Company)).all()
    anomalies = list_anomalies(db)
    severity_counts = Counter(item["severity"] for item in anomalies)
    category_counts = Counter(item["anomaly_type"] for item in anomalies)
    company_scores: dict[int, int] = defaultdict(int)
    company_names = {company.id: company.name for company in companies}
    for item in anomalies:
        company_scores[item["company_id"]] += SEVERITY_WEIGHT.get(item["severity"], 1)
    requiring_review = sorted(
        [{"company_id": cid, "company_name": company_names.get(cid), "risk_score": score, "exception_count": sum(1 for item in anomalies if item["company_id"] == cid)} for cid, score in company_scores.items()],
        key=lambda row: row["risk_score"],
        reverse=True,
    )[:10]
    return {
        "total_companies": len(companies),
        "total_anomalies": len(anomalies),
        "high_risk_exceptions": severity_counts.get("high", 0),
        "critical_exceptions": severity_counts.get("critical", 0),
        "severity_distribution": dict(severity_counts),
        "anomaly_categories": dict(category_counts),
        "companies_requiring_review": requiring_review,
    }


def compare_companies(db: Session, company_ids: list[int]) -> dict:
    rows = []
    for company_id in company_ids[:5]:
        company = db.get(Company, company_id)
        if not company:
            continue
        summary = company_summary(db, company)
        latest = company_metric_rows(db, company_id)[-1]
        anomalies = list_company_anomalies(db, company_id)
        rows.append({
            "company_id": company.id,
            "name": company.name,
            "industry": company.industry,
            "revenue_growth": latest.get("revenue_growth"),
            "ebitda_margin": latest.get("ebitda_margin"),
            "debt_to_ebitda": latest.get("debt_to_ebitda"),
            "operating_cash_conversion": latest.get("operating_cash_flow_to_ebitda"),
            "current_ratio": latest.get("current_ratio"),
            "working_capital_growth": latest.get("working_capital_growth"),
            "exception_count": len(anomalies),
            "latest_revenue": summary.get("latest_revenue"),
        })
    return {"companies": rows}
