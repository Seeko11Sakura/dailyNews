from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_domains_route():
    response = client.get("/domains")

    assert response.status_code == 200
    assert len(response.json()) == 12


def test_digest_route():
    response = client.post(
        "/digest/today",
        json={
            "selected_domains": ["technology", "ai", "business"],
            "sort_preference": "freshness",
            "date": "2026-05-19",
        },
    )

    assert response.status_code == 200
    assert len(response.json()["groups"]) == 3


def test_article_route():
    response = client.get("/items/technology-1")

    assert response.status_code == 200
    assert response.json()["source_url"].startswith("https://")
