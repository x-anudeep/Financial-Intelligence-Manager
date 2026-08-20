from sqlalchemy.orm import Session

from app.ai.llm import llm_client
from app.models.anomaly import Anomaly
from app.models.financial import Company
from app.rag.retrieval import search_company_documents
from app.services.anomalies import list_company_anomalies
from app.services.financials import company_metric_rows


def analyst_summary(db: Session, company_id: int) -> dict:
    company = db.get(Company, company_id)
    rows = company_metric_rows(db, company_id)
    anomalies = list_company_anomalies(db, company_id)
    if not company or not rows:
        raise ValueError("Company not found")
    latest = rows[-1]
    top = sorted(anomalies, key=lambda item: {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(item["severity"], 1), reverse=True)[:3]
    anomaly_text = "; ".join(item["title"] for item in top) or "no current exceptions"
    fallback = (
        f"{company.name} latest period is {latest['period']}. Revenue growth was {_pct(latest.get('revenue_growth'))}, "
        f"EBITDA margin was {_pct(latest.get('ebitda_margin'))}, and debt / EBITDA was {_num(latest.get('debt_to_ebitda'))}x. "
        f"Current analyst attention items include {anomaly_text}."
    )
    prompt = (
        f"Company: {company.name}\nLatest metrics: {latest}\nTop anomalies: {top}\n"
        "Write a concise analyst summary. Separate deterministic structured findings from interpretation."
    )
    answer = llm_client.complete(prompt) or fallback
    return {"answer": answer, "ai_enabled": llm_client.enabled, "structured_findings": top, "sources": []}


def answer_question(db: Session, company_id: int, question: str) -> dict:
    lower = question.lower()
    rows = company_metric_rows(db, company_id)
    anomalies = list_company_anomalies(db, company_id)
    sources = search_company_documents(db, company_id, question, limit=4)
    latest = rows[-1] if rows else {}
    if "cash" in lower:
        cash_history = ", ".join(f"{row['period']}: {_money(row.get('cash'))}" for row in rows)
        answer = f"Structured finding: cash history is {cash_history}."
    elif "receivable" in lower or "ar " in lower:
        ar_items = [item for item in anomalies if item["metric"] == "accounts_receivable"]
        answer = "Structured finding: " + (ar_items[0]["evidence"] if ar_items else "no receivables exception is currently stored.")
    elif "risk" in lower or "largest" in lower or "anomaly" in lower:
        top = sorted(anomalies, key=lambda item: {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(item["severity"], 1), reverse=True)[:5]
        answer = "Structured finding: largest exceptions are " + "; ".join(f"{item['title']} ({item['severity']})" for item in top)
    elif "debt" in lower:
        answer = f"Structured finding: latest debt / EBITDA is {_num(latest.get('debt_to_ebitda'))}x and total debt is {_money(latest.get('total_debt'))}."
    else:
        answer = analyst_summary(db, company_id)["answer"]
    if sources:
        answer += " Document context was retrieved and is listed with source references."
    elif not llm_client.enabled:
        answer += " AI narrative generation is disabled because no API key is configured; deterministic structured analysis remains available."
    if llm_client.enabled:
        prompt = (
            f"Question: {question}\nStructured answer draft: {answer}\n"
            f"Latest metrics: {latest}\nAnomalies: {anomalies[:5]}\nRetrieved sources: {sources}\n"
            "Improve the answer using only this information. Cite document context generally by source names when present."
        )
        answer = llm_client.complete(prompt) or answer
    return {"answer": answer, "ai_enabled": llm_client.enabled, "structured_findings": anomalies[:5], "sources": sources}


def supporting_context_for_anomaly(db: Session, anomaly_id: int) -> dict:
    anomaly = db.get(Anomaly, anomaly_id)
    if not anomaly:
        raise ValueError("Anomaly not found")
    query_terms = {
        "accounts_receivable": "receivables collections payment terms customers billing delays working capital",
        "inventory": "inventory aging supply chain obsolescence demand forecast",
        "total_debt": "debt leverage covenant maturity interest refinancing",
        "cash": "cash liquidity operating cash flow capital expenditures working capital",
        "operating_expenses": "expenses legal professional fees headcount one-time charges",
    }
    query = query_terms.get(anomaly.metric, f"{anomaly.metric} {anomaly.anomaly_type} management explanation risk")
    sources = search_company_documents(db, anomaly.company_id, query, limit=5)
    fallback = f"Structured finding: {anomaly.description} Evidence: {anomaly.evidence}"
    if llm_client.enabled:
        prompt = (
            f"Anomaly: {anomaly.title}\nDescription: {anomaly.description}\nEvidence: {anomaly.evidence}\n"
            f"Suggested review: {anomaly.suggested_review}\nRetrieved sources: {sources}\n"
            "Explain the structured finding and any relevant document context. Do not claim document support if sources are empty."
        )
        answer = llm_client.complete(prompt) or fallback
    else:
        answer = fallback
    return {
        "answer": answer,
        "ai_enabled": llm_client.enabled,
        "structured_findings": [{"id": anomaly.id, "title": anomaly.title, "evidence": anomaly.evidence, "suggested_review": anomaly.suggested_review}],
        "sources": sources,
    }


def _pct(value: float | None) -> str:
    return "N/A" if value is None else f"{value * 100:.1f}%"


def _num(value: float | None) -> str:
    return "N/A" if value is None else f"{value:.2f}"


def _money(value: float | None) -> str:
    return "N/A" if value is None else f"${value / 1_000_000:.1f}M"
