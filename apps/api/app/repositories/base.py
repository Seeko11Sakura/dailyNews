"""Supabase 客户端入口，优先使用服务端密钥执行后端写入。"""

import os
import re

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

_supabase: Client | None = None


def _is_jwt_like(value: str | None) -> bool:
    """判断 Supabase 客户端是否能识别这个 key。"""
    if not value:
        return False
    return bool(re.match(r"^[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*$", value))


def _supabase_key() -> str | None:
    """优先使用可被当前客户端识别的服务端 key，否则回退到匿名 key。"""
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if _is_jwt_like(service_role_key):
        return service_role_key
    return os.getenv("SUPABASE_ANON_KEY")


def get_supabase() -> Client:
    global _supabase
    if _supabase is None:
        url = os.getenv("SUPABASE_URL")
        key = _supabase_key()
        if not url or not key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY must be set"
            )
        _supabase = create_client(url, key)
    return _supabase
