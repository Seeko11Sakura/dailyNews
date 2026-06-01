"""验证内容采集流程会用文章详情页补全正文、图片和发布时间。"""

import asyncio

from app.services import content_pipeline


def test_enrich_article_with_crawler_uses_full_content_and_images(monkeypatch):
    monkeypatch.setattr(
        content_pipeline,
        "crawl_article",
        lambda url: {
            "title": "原文标题",
            "content": "这是一段来自原文页的完整正文内容，比 RSS 摘要更适合 AI 解析。",
            "image_urls": ["https://example.com/a.jpg"],
        },
    )

    article = content_pipeline.enrich_article_with_crawler(
        {
            "title": "RSS 标题",
            "summary": "RSS 摘要",
            "content": "短内容",
            "source_url": "https://example.com/a",
        }
    )

    assert article["content"] == "这是一段来自原文页的完整正文内容，比 RSS 摘要更适合 AI 解析。"
    assert article["image_urls"] == ["https://example.com/a.jpg"]


def test_enrich_article_with_crawler_updates_publish_time(monkeypatch):
    monkeypatch.setattr(
        content_pipeline,
        "crawl_article",
        lambda url: {
            "title": "原文标题",
            "content": "原文正文",
            "published_at": "2026-06-02T09:30:00+08:00",
            "image_urls": [],
        },
    )

    article = content_pipeline.enrich_article_with_crawler(
        {
            "title": "候选标题",
            "content": "",
            "published_at": "2026-06-01T23:59:00+08:00",
            "source_url": "https://example.com/a",
        }
    )

    assert article["published_at"] == "2026-06-02T09:30:00+08:00"


def test_enrich_article_with_crawler_replaces_generic_title(monkeypatch):
    monkeypatch.setattr(
        content_pipeline,
        "crawl_article",
        lambda url: {
            "title": "任天堂新主机首发游戏阵容公布",
            "content": "任天堂公布新主机首发游戏阵容，包含多款第一方作品。",
            "image_urls": [],
        },
    )

    article = content_pipeline.enrich_article_with_crawler(
        {
            "title": "Gadio News",
            "summary": "",
            "content": "",
            "source_url": "https://example.com/a",
        }
    )

    assert article["title"] == "任天堂新主机首发游戏阵容公布"


def test_process_fetched_articles_crawls_only_new_articles(monkeypatch):
    async def fake_filter_new_articles(articles: list[dict]) -> list[dict]:
        return [{**articles[0], "url_hash": "hash-a", "title_similarity_hash": "title-a"}]

    monkeypatch.setattr(content_pipeline, "filter_new_articles", fake_filter_new_articles)
    monkeypatch.setattr(
        content_pipeline,
        "enrich_article_with_crawler",
        lambda article: {**article, "content": "原文正文", "image_urls": ["https://example.com/a.jpg"]},
    )

    processed = asyncio.run(
        content_pipeline.process_fetched_articles(
            [
                {
                    "title": "测试标题",
                    "summary": "RSS 摘要",
                    "content": "RSS 摘要",
                    "source_url": "https://example.com/a",
                }
            ]
        )
    )

    assert processed[0]["content"] == "原文正文"
    assert processed[0]["image_urls"] == ["https://example.com/a.jpg"]
