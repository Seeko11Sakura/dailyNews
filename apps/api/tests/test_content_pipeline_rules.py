import asyncio

from app.services import content_pipeline
from app.services.source_config import SourceConfig


def test_fetch_source_limits_articles_and_fills_missing_publish_time(monkeypatch):
    source = SourceConfig(
        name="测试网页源",
        url="https://example.com/",
        domain_id="finance",
        tier="A",
        source_type="web",
    )
    monkeypatch.setitem(content_pipeline.SOURCES_BY_NAME, source.name, source)
    monkeypatch.setenv("SOURCE_ARTICLE_LIMIT", "2")

    async def fake_scrape_source(source):
        return [
            {"title": f"财经市场测试标题{i}", "link": f"https://example.com/news/{i}"}
            for i in range(3)
        ]

    captured: list[dict] = []

    async def fake_process_fetched_articles(articles):
        captured.extend(articles)
        return articles

    async def fake_insert_articles(articles):
        return len(articles)

    monkeypatch.setattr(content_pipeline, "scrape_source", fake_scrape_source)
    monkeypatch.setattr(
        content_pipeline,
        "process_fetched_articles",
        fake_process_fetched_articles,
    )
    monkeypatch.setattr(content_pipeline, "insert_articles", fake_insert_articles)

    result = asyncio.run(content_pipeline.fetch_source(source.name))

    assert result["articles_fetched"] == 2
    assert result["articles_inserted"] == 2
    assert len(captured) == 2
    assert all(article["published_at"] for article in captured)


def test_fetch_source_filters_invalid_article_candidates(monkeypatch):
    source = SourceConfig(
        name="测试网页源",
        url="https://example.com/",
        domain_id="technology",
        tier="A",
        source_type="web",
    )
    monkeypatch.setitem(content_pipeline.SOURCES_BY_NAME, source.name, source)

    async def fake_scrape_source(source):
        return [
            {
                "title": "医院资讯网站地图",
                "link": "https://example.com/news/sitemap.html",
                "summary": "",
            },
            {
                "title": "Gadio News",
                "link": "https://example.com/articles/123456",
                "summary": "文章内容为空，无法提取核心事实。",
            },
            {
                "title": "压缩效率提升约 30%，新一代 AV2 视频编码标准正式发布",
                "link": "https://example.com/news/20260531/123456.html",
                "summary": "新标准正式发布。",
            },
        ]

    captured: list[dict] = []

    async def fake_process_fetched_articles(articles):
        captured.extend(articles)
        return articles

    async def fake_insert_articles(articles):
        return len(articles)

    monkeypatch.setattr(content_pipeline, "scrape_source", fake_scrape_source)
    monkeypatch.setattr(
        content_pipeline,
        "process_fetched_articles",
        fake_process_fetched_articles,
    )
    monkeypatch.setattr(content_pipeline, "insert_articles", fake_insert_articles)

    result = asyncio.run(content_pipeline.fetch_source(source.name))

    assert result["articles_fetched"] == 1
    assert result["articles_inserted"] == 1
    assert [article["title"] for article in captured] == [
        "压缩效率提升约 30%，新一代 AV2 视频编码标准正式发布"
    ]


def test_fallback_published_at_uses_previous_digest_before_8am():
    value = content_pipeline._fallback_published_at("2026-05-30T16:30:00+00:00")

    assert value == "2026-05-30T15:59:00+00:00"
