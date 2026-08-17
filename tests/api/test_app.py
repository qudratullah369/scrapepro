from fastapi.testclient import TestClient

from scrapepro.api.app import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "scrapepro",
    }


def test_scrape_endpoint_accepts_request():
    response = client.post(
        "/scrape",
        json={
            "source": "google_maps",
            "query": "cafes",
            "location": "Islamabad",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "status": "accepted",
        "task": {
            "source": "google_maps",
            "query": "cafes",
            "location": "Islamabad",
            "output": None,
            "database": None,
        },
    }


def test_scrape_endpoint_rejects_missing_source():
    response = client.post(
        "/scrape",
        json={
            "query": "cafes",
            "location": "Islamabad",
        },
    )

    assert response.status_code == 422
