from app.services.mock_repository import _query_digest_items


class _Result:
    data = []


class _Table:
    def __init__(self) -> None:
        self.filters: list[tuple[str, str, str]] = []
        self.orders: list[tuple[str, bool]] = []

    def select(self, value: str):
        return self

    def eq(self, field: str, value: str):
        self.filters.append(("eq", field, value))
        return self

    def lt(self, field: str, value: str):
        self.filters.append(("lt", field, value))
        return self

    def gte(self, field: str, value: str):
        self.filters.append(("gte", field, value))
        return self

    def order(self, field: str, desc: bool):
        self.orders.append((field, desc))
        return self

    def limit(self, value: int):
        return self

    def execute(self):
        return _Result()


class _Supabase:
    def __init__(self) -> None:
        self.table_ref = _Table()

    def table(self, name: str):
        assert name == "articles"
        return self.table_ref


def test_digest_query_filters_by_published_at():
    supabase = _Supabase()

    _query_digest_items(
        supabase,
        content_domain_id="technology",
        start_at="2026-05-29T16:00:00+00:00",
        end_at="2026-05-30T16:00:00+00:00",
    )

    assert ("gte", "published_at", "2026-05-29T16:00:00+00:00") in supabase.table_ref.filters
    assert ("lt", "published_at", "2026-05-30T16:00:00+00:00") in supabase.table_ref.filters
    assert supabase.table_ref.orders == [("published_at", True)]
