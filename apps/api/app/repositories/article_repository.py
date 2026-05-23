from app.repositories.base import get_supabase


class ArticleRepository:
    table = "articles"

    @classmethod
    async def get_by_domain(cls, domain_id: str, limit: int = 10) -> list[dict]:
        supabase = get_supabase()
        result = (
            supabase.table(cls.table)
            .select("*")
            .eq("domain_id", domain_id)
            .order("published_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data

    @classmethod
    async def get_by_id(cls, article_id: str) -> dict | None:
        supabase = get_supabase()
        result = supabase.table(cls.table).select("*").eq("id", article_id).execute()
        return result.data[0] if result.data else None

    @classmethod
    async def create(cls, article: dict) -> dict:
        supabase = get_supabase()
        result = supabase.table(cls.table).insert(article).execute()
        return result.data[0]

    @classmethod
    async def mark_read(cls, user_id: str, article_id: str) -> None:
        supabase = get_supabase()
        supabase.table("read_records").upsert(
            {"user_id": user_id, "article_id": article_id}
        ).execute()

    @classmethod
    async def get_read_articles(cls, user_id: str) -> list[str]:
        supabase = get_supabase()
        result = supabase.table("read_records").select("article_id").eq("user_id", user_id).execute()
        return [row["article_id"] for row in result.data]

    @classmethod
    async def toggle_favorite(cls, user_id: str, article_id: str) -> bool:
        supabase = get_supabase()
        existing = (
            supabase.table("favorites")
            .select("id")
            .eq("user_id", user_id)
            .eq("article_id", article_id)
            .execute()
        )
        if existing.data:
            supabase.table("favorites").delete().eq("id", existing.data[0]["id"]).execute()
            return False
        supabase.table("favorites").insert(
            {"user_id": user_id, "article_id": article_id}
        ).execute()
        return True

    @classmethod
    async def get_favorites(cls, user_id: str) -> list[dict]:
        supabase = get_supabase()
        result = (
            supabase.table("favorites")
            .select("article_id, created_at")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        return result.data
