import asyncio

from app.services import content_pipeline


class _InsertResult:
    data = [{"id": "article-1"}]


class _ArticlesTable:
    def __init__(self) -> None:
        self.inserted_rows = []

    def insert(self, row: dict):
        self.inserted_rows.append(row)
        return self

    def execute(self):
        return _InsertResult()


class _Supabase:
    def __init__(self) -> None:
        self.articles = _ArticlesTable()

    def table(self, name: str):
        assert name == "articles"
        return self.articles


def test_insert_articles_stores_ai_overview(monkeypatch):
    supabase = _Supabase()

    monkeypatch.setattr(content_pipeline, "get_supabase", lambda: supabase)

    async def fake_generate_ai_overview(article: dict) -> str:
        return f"AI 概览：{article['title']}"

    monkeypatch.setattr(
        content_pipeline,
        "generate_ai_overview",
        fake_generate_ai_overview,
    )
    async def fake_classify_article_domain(article: dict) -> dict:
        return {"domain_id": article["domain_id"], "reason": "测试沿用来源领域"}

    monkeypatch.setattr(
        content_pipeline,
        "classify_article_domain",
        fake_classify_article_domain,
    )
    monkeypatch.setattr(content_pipeline, "_resolve_article_image_urls", lambda article: [])

    inserted = asyncio.run(
        content_pipeline.insert_articles(
            [
                {
                    "domain_id": "ai",
                    "title": "测试文章标题",
                    "summary": "原始摘要很长",
                    "content": "原始正文很长",
                    "source_url": "https://example.com/a",
                    "source_name": "Example",
                    "published_at": None,
                    "url_hash": "hash-a",
                    "title_similarity_hash": "title-hash-a",
                }
            ]
        )
    )

    assert inserted == 1
    assert supabase.articles.inserted_rows[0]["ai_overview"] == "AI 概览：测试文章标题"


def test_digest_uses_pending_text_when_ai_overview_missing():
    from app.services.ai_overview import PENDING_OVERVIEW_TEXT

    assert PENDING_OVERVIEW_TEXT == "AI 概览生成中，稍后刷新查看。"


def test_generate_ai_overview_returns_none_without_api_key(monkeypatch):
    from app.services.ai_overview import generate_ai_overview

    monkeypatch.delenv("AI_API_KEY", raising=False)

    overview = asyncio.run(
        generate_ai_overview(
            {
                "title": "测试文章标题",
                "summary": "这是一段原始摘要",
                "content": "这是一段原始正文",
            }
        )
    )

    assert overview is None
