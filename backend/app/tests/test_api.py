from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_seed_and_list_companies():
    seed = client.post("/api/seed")
    assert seed.status_code == 200
    response = client.get("/api/companies")
    assert response.status_code == 200
    assert len(response.json()) >= 30
