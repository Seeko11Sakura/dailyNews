"""验证后端主要接口，包括抓取、试跑来源和图片补齐。"""

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
    response = client.get("/items/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 200
    assert response.json()["fetch_status"] == "not_found"


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


def test_digest_generate_starts_background_job(monkeypatch):
    from app.api import routes

    monkeypatch.setattr(
        routes,
        "start_manual_digest_generation",
        lambda: {"status": "started", "current_run": None},
    )

    response = client.post("/digest/generate")

    assert response.status_code == 200
    assert response.json()["status"] == "started"


def test_crawl_article_route_returns_preview(monkeypatch):
    from app.api import routes

    monkeypatch.setattr(
        routes,
        "crawl_article",
        lambda url: {
            "url": url,
            "title": "测试文章",
            "content": "测试正文内容",
            "image_urls": ["https://example.com/a.jpg"],
            "content_length": 6,
        },
    )

    response = client.post(
        "/crawl/article",
        json={"url": "https://example.com/news/1"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "测试文章"
    assert response.json()["image_urls"] == ["https://example.com/a.jpg"]


def test_source_trial_route_returns_candidates_and_previews(monkeypatch):
    from app.api import routes

    async def fake_scrape_source(source):
        return [
            {
                "title": "测试来源抓到第一篇文章",
                "link": "https://example.com/news/1",
                "summary": "",
                "domain_id": source.domain_id,
            }
        ]

    monkeypatch.setattr(routes, "scrape_source", fake_scrape_source)
    monkeypatch.setattr(
        routes,
        "crawl_article",
        lambda url: {
            "url": url,
            "title": "详情页标题",
            "content": "详情页正文",
            "published_at": "2026-06-02T09:00:00+08:00",
            "image_urls": ["https://example.com/a.jpg"],
            "content_length": 5,
        },
    )

    response = client.post(
        "/sources/trial",
        json={"url": "https://example.com/", "domain_id": "technology", "limit": 1},
    )

    assert response.status_code == 200
    assert response.json()["candidate_count"] == 1
    assert response.json()["previews"][0]["ok"] is True
    assert response.json()["previews"][0]["image_count"] == 1


def test_images_backfill_route(monkeypatch):
    from app.api import routes

    monkeypatch.setattr(
        routes,
        "backfill_article_images",
        lambda **kwargs: {"matched": 1, "updated": 1, "failed": 0},
    )

    response = client.post(
        "/images/backfill",
        json={"domain_id": "technology", "date": "2026-05-30", "limit": 1},
    )

    assert response.status_code == 200
    assert response.json()["updated"] == 1
