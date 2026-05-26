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
