from app.repositories.base import get_supabase


class UserRepository:
    table = "users"

    @classmethod
    async def get_or_create_by_device(cls, device_id: str) -> dict:
        supabase = get_supabase()
        result = supabase.table(cls.table).select("*").eq("device_id", device_id).execute()
        if result.data:
            return result.data[0]
        result = supabase.table(cls.table).insert({"device_id": device_id}).execute()
        return result.data[0]

    @classmethod
    async def get_user_domains(cls, user_id: str) -> list[str]:
        supabase = get_supabase()
        result = supabase.table("user_domains").select("domain_id").eq("user_id", user_id).execute()
        return [row["domain_id"] for row in result.data]

    @classmethod
    async def set_user_domains(cls, user_id: str, domain_ids: list[str]) -> None:
        supabase = get_supabase()
        supabase.table("user_domains").delete().eq("user_id", user_id).execute()
        rows = [{"user_id": user_id, "domain_id": did} for did in domain_ids]
        supabase.table("user_domains").insert(rows).execute()
