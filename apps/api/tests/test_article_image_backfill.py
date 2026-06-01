from app.services import article_image_backfill


class _Result:
    def __init__(self, data):
        self.data = data


class _Table:
    def __init__(self, rows):
        self.rows = rows
        self.updated_rows: list[dict] = []

    def select(self, value: str):
        return self

    def is_(self, field: str, value: str):
        return self

    def order(self, field: str, desc: bool):
        return self

    def limit(self, value: int):
        return self

    def eq(self, field: str, value: str):
        return self

    def gte(self, field: str, value: str):
        return self

    def lte(self, field: str, value: str):
        return self

    def update(self, row: dict):
        self.updated_rows.append(row)
        return self

    def execute(self):
        return _Result(self.rows)


class _Supabase:
    def __init__(self):
        self.articles = _Table(
            [
                {
                    "id": "article-1",
                    "domain_id": "technology",
                    "title": "测试文章",
                    "source_url": "https://example.com/a",
                    "content": "短正文",
                    "cover_image_url": None,
                }
            ]
        )

    def table(self, name: str):
        assert name == "articles"
        return self.articles


def test_backfill_article_images_updates_cover(monkeypatch):
    supabase = _Supabase()

    monkeypatch.setattr(article_image_backfill, "get_supabase", lambda: supabase)
    monkeypatch.setattr(
        article_image_backfill,
        "crawl_article",
        lambda url: {
            "content": "更长的原文内容",
            "image_urls": ["https://example.com/a.jpg"],
        },
    )
    monkeypatch.setattr(
        article_image_backfill,
        "store_article_images",
        lambda article_id, image_urls, **kwargs: [
            {"public_url": "https://cdn.example.com/a.jpg"}
        ],
    )

    result = article_image_backfill.backfill_article_images(
        domain_id="technology",
        published_date="2026-05-30",
        limit=5,
    )

    assert result["matched"] == 1
    assert result["updated"] == 1
    assert supabase.articles.updated_rows[0]["cover_image_url"].endswith("a.jpg")
