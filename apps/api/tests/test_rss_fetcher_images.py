from types import SimpleNamespace

from app.services import rss_fetcher
from app.services.source_config import SourceConfig


def test_fetch_feed_extracts_entry_images(monkeypatch):
    source = SourceConfig(
        name="测试 RSS",
        url="https://example.com/",
        domain_id="technology",
        tier="A",
        source_type="rss",
        rss_url="https://example.com/feed.xml",
    )
    feed = SimpleNamespace(
        bozo=False,
        entries=[
            {
                "title": "测试新闻标题",
                "link": "https://example.com/news/1",
                "summary": "测试摘要",
                "media_content": [{"url": "https://example.com/cover.jpg"}],
            }
        ],
    )

    monkeypatch.setattr(rss_fetcher.feedparser, "parse", lambda *args, **kwargs: feed)

    articles = rss_fetcher.fetch_feed(source)

    assert articles[0]["image_urls"] == ["https://example.com/cover.jpg"]
