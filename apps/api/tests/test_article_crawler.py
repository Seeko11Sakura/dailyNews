from app.services.article_crawler import extract_article_preview


def test_extract_article_preview_collects_title_content_and_images():
    html = """
    <html>
      <head>
        <meta property="og:title" content="测试文章标题" />
        <meta property="og:image" content="/cover.jpg" />
      </head>
      <body>
        <header><img src="/logo.png" /></header>
        <article>
          <h1>页面标题</h1>
          <p>第一段正文内容足够长，用来模拟真实新闻正文。</p>
          <p>第二段正文继续补充事实和背景，让正文长度超过提取阈值。</p>
          <p>第三段正文说明影响和后续变化，确保阅读页能展示原文。</p>
          <img data-src="/images/news-1.jpg" />
          <p>第四段正文继续扩展内容，避免被误判为短摘要。</p>
          <img src="https://cdn.example.com/news-2.png" />
        </article>
      </body>
    </html>
    """

    preview = extract_article_preview(html, "https://example.com/news/123")

    assert preview["title"] == "测试文章标题"
    assert "第一段正文内容足够长" in preview["content"]
    assert preview["image_urls"] == [
        "https://example.com/cover.jpg",
        "https://example.com/images/news-1.jpg",
        "https://cdn.example.com/news-2.png",
    ]


def test_extract_article_preview_reads_json_ld_image_and_time():
    html = """
    <html>
      <head>
        <script type="application/ld+json">
        {
          "@type": "NewsArticle",
          "image": ["https://example.com/cover.jpg"],
          "datePublished": "2026-06-02T08:10:00+08:00"
        }
        </script>
      </head>
      <body>
        <article>
          <h1>测试新闻标题</h1>
          <p>第一段正文足够长，用来验证正文提取。</p>
          <p>第二段正文继续补充，让内容达到有效长度。</p>
          <p>第三段正文说明背景和影响，避免被当成短内容。</p>
        </article>
      </body>
    </html>
    """

    preview = extract_article_preview(html, "https://example.com/news/1")

    assert preview["title"] == "测试新闻标题"
    assert preview["published_at"] == "2026-06-02T08:10:00+08:00"
    assert preview["image_urls"] == ["https://example.com/cover.jpg"]


def test_extract_article_preview_reads_time_tag_when_meta_missing():
    html = """
    <html>
      <body>
        <time datetime="2026-06-02T09:20:00+08:00">2026-06-02</time>
        <article>
          <h1>另一篇测试新闻标题</h1>
          <p>第一段正文足够长，用来验证正文提取。</p>
          <p>第二段正文继续补充，让内容达到有效长度。</p>
          <p>第三段正文说明背景和影响，避免被当成短内容。</p>
        </article>
      </body>
    </html>
    """

    preview = extract_article_preview(html, "https://example.com/news/2")

    assert preview["published_at"] == "2026-06-02T09:20:00+08:00"
