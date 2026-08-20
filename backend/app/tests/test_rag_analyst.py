from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_document_upload_search_and_ai_fallback():
    client.post("/api/seed")
    companies = client.get("/api/companies").json()
    company_id = companies[0]["id"]
    upload = client.post(
        f"/api/companies/{company_id}/documents",
        files={"file": ("management.txt", b"Management noted receivables increased because customers received extended payment terms and collections slowed.", "text/plain")},
    )
    assert upload.status_code == 200
    assert upload.json()["chunks"] >= 1
    search = client.get(f"/api/companies/{company_id}/documents/search", params={"q": "receivables payment terms collections"})
    assert search.status_code == 200
    assert search.json()["sources"]
    answer = client.post("/api/assistant/ask", json={"company_id": company_id, "question": "What does management say about receivables?"})
    assert answer.status_code == 200
    body = answer.json()
    assert body["ai_enabled"] is False
    assert body["sources"]


def test_supporting_context_for_anomaly_returns_structured_finding():
    client.post("/api/seed")
    anomalies = client.get("/api/anomalies").json()
    anomaly_id = anomalies[0]["id"]
    response = client.post("/api/anomalies/supporting-context", json={"anomaly_id": anomaly_id})
    assert response.status_code == 200
    assert "Structured finding" in response.json()["answer"]
