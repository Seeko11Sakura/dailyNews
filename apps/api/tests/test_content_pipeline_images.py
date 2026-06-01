import asyncio

from app.services import content_pipeline


class _InsertResult:
    data = [{"id": "article-1"}]


class _Table:
    def __init__(self) -> None:
        self.inserted_rows: list[dict] = []
        self.updated_rows: list[dict] = []
        self.updated_id = ""

    def insert(self, row: dict):
        self.inserted_rows.append(row)
        return self

    def update(self, row: dict):
        self.updated_rows.append(row)
        return self

    def eq(self, field: str, value: str):
        if field == "id":
            self.updated_id = value
        return self

    def execute(self):
        return _InsertResult()


class _Supabase:
    def __init__(self) -> None:
        self.articles = _Table()

    def table(self, name: str):
        assert name == "articles"
        return self.articles


def test_insert_articles_stores_cover_image(monkeypatch):
    supabase = _Supabase()
    stored_calls: list[tuple[str, list[str]]] = []

    monkeypatch.setattr(content_pipeline, "get_supabase", lambda: supabase)

    async def fake_generate_ai_overview(article: dict) -> str:
        return "AI 概览"

    async def fake_classify_article_domain(article: dict) -> dict:
        return {"domain_id": article["domain_id"], "reason": "测试沿用来源领域"}

    def fake_store_article_images(article_id: str, image_urls: list[str], **kwargs):
        stored_calls.append((article_id, image_urls))
        return [{"public_url": "https://cdn.example.com/article-1/cover.jpg"}]

    monkeypatch.setattr(content_pipeline, "generate_ai_overview", fake_generate_ai_overview)
    monkeypatch.setattr(content_pipeline, "classify_article_domain", fake_classify_article_domain)
    monkeypatch.setattr(content_pipeline, "store_article_images", fake_store_article_images)

    inserted = asyncio.run(
        content_pipeline.insert_articles(
            [
                {
                    "domain_id": "ai",
                    "title": "测试文章标题",
                    "summary": "原始摘要",
                    "content": "原始正文",
                    "source_url": "https://example.com/a",
                    "source_name": "Example",
                    "published_at": None,
                    "image_urls": ["https://example.com/a.jpg"],
                    "url_hash": "hash-a",
                    "title_similarity_hash": "title-hash-a",
                }
            ]
        )
    )

    assert inserted == 1
    assert stored_calls == [("article-1", ["https://example.com/a.jpg"])]
    assert supabase.articles.updated_rows[0]["cover_image_url"].endswith("cover.jpg")


def test_insert_articles_crawls_cover_image_when_enabled(monkeypatch):
    supabase = _Supabase()
    stored_calls: list[tuple[str, list[str]]] = []

    monkeypatch.setattr(content_pipeline, "get_supabase", lambda: supabase)
    monkeypatch.setenv("ARTICLE_IMAGE_CRAWL_ENABLED", "true")

    async def fake_generate_ai_overview(article: dict) -> str:
        return "AI 概览"

    async def fake_classify_article_domain(article: dict) -> dict:
        return {"domain_id": article["domain_id"], "reason": "测试沿用来源领域"}

    def fake_crawl_article(url: str):
        return {"image_urls": ["https://example.com/from-page.jpg"]}

    def fake_store_article_images(article_id: str, image_urls: list[str], **kwargs):
        stored_calls.append((article_id, image_urls))
        return [{"public_url": "https://cdn.example.com/article-1/cover.jpg"}]

    monkeypatch.setattr(content_pipeline, "generate_ai_overview", fake_generate_ai_overview)
    monkeypatch.setattr(content_pipeline, "classify_article_domain", fake_classify_article_domain)
    monkeypatch.setattr(content_pipeline, "crawl_article", fake_crawl_article)
    monkeypatch.setattr(content_pipeline, "store_article_images", fake_store_article_images)

    inserted = asyncio.run(
        content_pipeline.insert_articles(
            [
                {
                    "domain_id": "ai",
                    "title": "测试文章标题",
                    "summary": "原始摘要",
                    "content": "原始正文",
                    "source_url": "https://example.com/a",
                    "source_name": "Example",
                    "published_at": None,
                    "image_urls": [],
                    "url_hash": "hash-a",
                    "title_similarity_hash": "title-hash-a",
                }
            ]
        )
    )

    assert inserted == 1
    assert stored_calls == [("article-1", ["https://example.com/from-page.jpg"])]


def test_insert_articles_updates_existing_article(monkeypatch):
    supabase = _Supabase()

    monkeypatch.setattr(content_pipeline, "get_supabase", lambda: supabase)

    async def fake_generate_ai_overview(article: dict) -> str:
        return "AI 概览"

    async def fake_classify_article_domain(article: dict) -> dict:
        return {"domain_id": article["domain_id"], "reason": "测试沿用来源领域"}

    monkeypatch.setattr(content_pipeline, "generate_ai_overview", fake_generate_ai_overview)
    monkeypatch.setattr(content_pipeline, "classify_article_domain", fake_classify_article_domain)
    monkeypatch.setattr(content_pipeline, "_store_images_for_article", lambda *args: None)

    affected = asyncio.run(
        content_pipeline.insert_articles(
            [
                {
                    "existing_article_id": "existing-1",
                    "domain_id": "business",
                    "title": "公司发布新财报",
                    "summary": "公司营收增长。",
                    "content": "公司营收增长。",
                    "source_url": "https://example.com/a",
                    "source_name": "Example",
                    "published_at": "2026-05-31T01:00:00+00:00",
                    "image_urls": [],
                    "url_hash": "hash-a",
                    "title_similarity_hash": "title-hash-a",
                }
            ]
        )
    )

    assert affected == 1
    assert supabase.articles.updated_id == "existing-1"
    assert supabase.articles.updated_rows[0]["domain_id"] == "business"
