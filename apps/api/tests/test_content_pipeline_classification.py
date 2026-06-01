import asyncio

from app.services import content_pipeline


class _InsertResult:
    data = [{"id": "article-1"}]


class _ArticlesTable:
    def __init__(self) -> None:
        self.inserted_rows: list[dict] = []

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


def test_insert_articles_uses_ai_classified_domain(monkeypatch):
    supabase = _Supabase()

    monkeypatch.setattr(content_pipeline, "get_supabase", lambda: supabase)

    async def fake_generate_ai_overview(article: dict) -> str:
        return "AI 概览"

    async def fake_classify_article_domain(article: dict) -> dict:
        return {"domain_id": "gadgets", "reason": "文章主要讨论手机新品"}

    monkeypatch.setattr(content_pipeline, "generate_ai_overview", fake_generate_ai_overview)
    monkeypatch.setattr(content_pipeline, "classify_article_domain", fake_classify_article_domain)
    monkeypatch.setattr(content_pipeline, "_resolve_article_image_urls", lambda article: [])

    inserted = asyncio.run(
        content_pipeline.insert_articles(
            [
                {
                    "domain_id": "technology",
                    "title": "新款手机发布",
                    "summary": "手机新品配置曝光",
                    "content": "原始正文",
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
    assert supabase.articles.inserted_rows[0]["domain_id"] == "gadgets"
    assert supabase.articles.inserted_rows[0]["source_domain_id"] == "technology"
    assert supabase.articles.inserted_rows[0]["classification_reason"] == "文章主要讨论手机新品"


class _MissingColumnTable:
    def __init__(self) -> None:
        self.inserted_rows: list[dict] = []
        self.calls = 0

    def insert(self, row: dict):
        self.inserted_rows.append(row)
        return self

    def execute(self):
        self.calls += 1
        if self.calls == 1:
            raise Exception(
                "Could not find the 'classification_reason' column of 'articles' in the schema cache"
            )
        return _InsertResult()


def test_insert_article_row_drops_optional_columns_for_schema_cache_error():
    table = _MissingColumnTable()
    supabase = type("Supabase", (), {"table": lambda self, name: table})()

    result = content_pipeline._insert_article_row(
        supabase,
        {
            "title": "测试文章",
            "source_domain_id": "finance",
            "classification_reason": "AI 分类原因",
        },
    )

    assert result.data[0]["id"] == "article-1"
    assert "source_domain_id" not in table.inserted_rows[-1]
    assert "classification_reason" not in table.inserted_rows[-1]
