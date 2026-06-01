from app.services.image_storage import store_article_images


class _Response:
    content = b"fake-image-bytes"
    headers = {"content-type": "image/jpeg", "content-length": "16"}

    def raise_for_status(self) -> None:
        return None


class _Bucket:
    def __init__(self) -> None:
        self.uploaded: list[tuple[str, bytes, dict]] = []

    def upload(self, path: str, file: bytes, file_options: dict | None = None):
        self.uploaded.append((path, file, file_options or {}))
        return {"path": path}

    def get_public_url(self, path: str) -> str:
        return f"https://cdn.example.com/{path}"


class _Storage:
    def __init__(self, bucket: _Bucket) -> None:
        self.bucket = bucket

    def from_(self, bucket_name: str) -> _Bucket:
        assert bucket_name == "article-images"
        return self.bucket


class _Table:
    def __init__(self) -> None:
        self.rows: list[dict] = []

    def insert(self, row: dict):
        self.rows.append(row)
        return self

    def execute(self):
        return type("Result", (), {"data": self.rows})()


class _Supabase:
    def __init__(self, bucket: _Bucket, table: _Table) -> None:
        self.storage = _Storage(bucket)
        self.table_obj = table

    def table(self, name: str) -> _Table:
        assert name == "article_images"
        return self.table_obj


def test_store_article_images_uploads_and_records_unique_images():
    bucket = _Bucket()
    table = _Table()
    supabase = _Supabase(bucket, table)

    records = store_article_images(
        "article-1",
        ["https://example.com/a.jpg", "https://example.com/a.jpg"],
        supabase=supabase,
        http_get=lambda url, **kwargs: _Response(),
    )

    assert len(records) == 1
    assert table.rows[0]["article_id"] == "article-1"
    assert table.rows[0]["original_url"] == "https://example.com/a.jpg"
    assert table.rows[0]["public_url"].startswith("https://cdn.example.com/")
    assert bucket.uploaded[0][2]["content-type"] == "image/jpeg"
