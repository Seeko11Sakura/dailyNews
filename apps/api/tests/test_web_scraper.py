from app.services.source_config import SourceConfig
"""验证网页列表页能从常见新闻链接格式里识别候选文章。"""

from app.services.web_scraper import _looks_like_article_link, _parse_article_links_fallback


def test_web_scraper_fallback_extracts_article_links():
    html = """
    <html>
      <body>
        <a href="/about">关于我们</a>
        <a href="/news/2026/05/30/123456.html">财经市场今日出现新变化</a>
        <a href="https://example.com/article/98765">商业公司发布重要公告</a>
      </body>
    </html>
    """
    source = SourceConfig(
        name="测试来源",
        url="https://example.com/",
        domain_id="finance",
        tier="A",
        source_type="web",
    )

    articles = _parse_article_links_fallback(html, source)

    assert [article["title"] for article in articles] == [
        "财经市场今日出现新变化",
        "商业公司发布重要公告",
    ]
    assert all(article["published_at"] is None for article in articles)


def test_web_scraper_accepts_segmented_numeric_article_paths():
    assert _looks_like_article_link(
        "https://www.ithome.com/0/958/088.htm",
        "英伟达 RTX Spark PC 处理器正式发布",
        "https://www.ithome.com/",
    )
