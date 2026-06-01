"""验证文章正文提取能保留真实阅读需要的正文段落。"""

from app.services.article_content import extract_article_content


def test_extract_article_content_prefers_article_body():
    html = """
    <html>
      <body>
        <nav>导航内容</nav>
        <article>
          <h1>测试标题</h1>
          <p>第一段正文内容足够长，用来模拟真实新闻正文。</p>
          <p>第二段正文继续补充事实和背景，让正文长度超过提取阈值。</p>
          <p>第三段正文说明影响和后续变化，确保阅读页能展示原文。</p>
          <p>第四段正文继续扩展内容，避免被误判为短摘要。</p>
          <p>第五段正文提供更多细节，模拟用户点进阅读页看到的内容。</p>
        </article>
      </body>
    </html>
    """

    content = extract_article_content(html)

    assert "第一段正文内容足够长" in content
    assert "第五段正文提供更多细节" in content
    assert "导航内容" not in content


def test_extract_article_content_preserves_paragraph_breaks():
    html = """
    <article>
      <p>第一段正文内容足够长，用来模拟真实新闻正文。</p>
      <p>第二段正文继续补充事实和背景，让正文长度超过提取阈值。</p>
      <p>第三段正文说明影响和后续变化，确保阅读页能展示原文。</p>
      <p>第四段正文继续扩展内容，避免被误判为短摘要。</p>
    </article>
    """

    content = extract_article_content(html)

    assert "第一段正文内容足够长，用来模拟真实新闻正文。\n\n第二段正文继续补充事实和背景" in content
