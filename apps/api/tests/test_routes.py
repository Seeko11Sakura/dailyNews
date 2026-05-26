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
    for group in response.json()["groups"]:
        assert len(group["items"]) <= 10
        assert all(len(item["summary"]) <= 100 for item in group["items"])


def test_digest_rejects_more_than_five_domains():
    response = client.post(
        "/digest/today",
        json={
            "selected_domains": [
                "technology",
                "ai",
                "business",
                "finance",
                "career",
                "education",
            ],
            "sort_preference": "freshness",
            "date": "2026-05-19",
        },
    )

    assert response.status_code == 422


def test_digest_rejects_unknown_domains():
    response = client.post(
        "/digest/today",
        json={
            "selected_domains": ["technology", "unknown"],
            "sort_preference": "freshness",
            "date": "2026-05-19",
        },
    )

    assert response.status_code == 422


def test_digest_rejects_duplicate_domains():
    response = client.post(
        "/digest/today",
        json={
            "selected_domains": ["technology", "technology"],
            "sort_preference": "freshness",
            "date": "2026-05-19",
        },
    )

    assert response.status_code == 422


def test_digest_rejects_unknown_sort_preference():
    response = client.post(
        "/digest/today",
        json={
            "selected_domains": ["technology"],
            "sort_preference": "engagement",
            "date": "2026-05-19",
        },
    )

    assert response.status_code == 422


def test_article_route():
    digest_response = client.post(
        "/digest/today",
        json={
            "selected_domains": ["technology"],
            "sort_preference": "freshness",
            "date": "2026-05-19",
        },
    )
    item_id = digest_response.json()["groups"][0]["items"][0]["id"]

    response = client.get(f"/items/{item_id}")

    assert response.status_code == 200
    assert response.json()["source_url"].startswith("https://")


def test_explore_route():
    response = client.post(
        "/explore/draw",
        json={
            "selected_domains": ["technology", "ai", "business"],
            "seen_domain_ids": [],
            "date": "2026-05-19",
        },
    )

    assert response.status_code == 200
    assert len(response.json()["cards"]) == 3
    returned_domain_ids = {card["domain_id"] for card in response.json()["cards"]}
    assert returned_domain_ids.isdisjoint({"technology", "ai", "business"})


def test_explore_excludes_seen_domains_and_still_returns_three_cards():
    response = client.post(
        "/explore/draw",
        json={
            "selected_domains": ["technology", "ai"],
            "seen_domain_ids": ["education", "business", "career"],
            "date": "2026-05-19",
        },
    )

    assert response.status_code == 200
    cards = response.json()["cards"]
    assert len(cards) == 3
    assert {card["domain_id"] for card in cards}.isdisjoint(
        {"technology", "ai", "education", "business", "career"}
    )
    assert all(card["reason"] for card in cards)


def test_explore_rejects_unknown_seen_domains():
    response = client.post(
        "/explore/draw",
        json={
            "selected_domains": ["technology"],
            "seen_domain_ids": ["not-a-domain"],
            "date": "2026-05-19",
        },
    )

    assert response.status_code == 422


def test_health_route():
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
