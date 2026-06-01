"""AI 概览服务：把抓取到的原文压缩成适合卡片展示的短内容。"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

from app.repositories.base import get_supabase

DEFAULT_AI_BASE_URL = "https://token-plan-cn.xiaomimimo.com/v1"
DEFAULT_AI_MODEL = "mimo-v2.5-pro"
MAX_OVERVIEW_CHARS = 120
PENDING_OVERVIEW_TEXT = "AI 概览生成中，稍后刷新查看。"
PROJECT_ROOT = Path(__file__).resolve().parents[4]

load_dotenv(PROJECT_ROOT / ".env")


def compact_text(value: str | None, limit: int = MAX_OVERVIEW_CHARS) -> str:
    """把兜底文本压到固定长度，避免长正文撑爆卡片。"""
    if not value:
        return ""
    text = " ".join(value.split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def build_overview_prompt(article: dict[str, Any]) -> str:
    """拼出给 AI 的文章信息，只保留生成概览需要的内容。"""
    title = article.get("title") or ""
    summary = article.get("summary") or ""
    content = article.get("content") or ""
    source = article.get("source_name") or ""
    raw_text = compact_text(f"{summary}\n{content}", limit=4000)
    return (
        "直接输出一条中文资讯概览，80字以内。"
        "不要标题、不要 Markdown、不要解释。"
        "说清楚核心事实和影响，不要照抄原文。\n\n"
        f"来源：{source}\n文章标题：{title}\n文章内容：{raw_text}"
    )


def clean_overview_text(value: str) -> str:
    """清理模型偶尔返回的标题或 Markdown 包装。"""
    lines = [line.strip() for line in value.splitlines() if line.strip()]
    cleaned_lines = [
        line.strip("*# ")
        for line in lines
        if not (line.startswith("**") and line.endswith("**"))
    ]
    return " ".join(cleaned_lines)


async def generate_ai_overview(article: dict[str, Any]) -> str | None:
    """调用兼容 OpenAI 的接口生成短概览，失败时返回空值。"""
    api_key = os.getenv("AI_API_KEY")
    if not api_key:
        return None

    base_url = os.getenv("AI_BASE_URL", DEFAULT_AI_BASE_URL).rstrip("/")
    model = os.getenv("AI_MODEL", DEFAULT_AI_MODEL)
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": build_overview_prompt(article)},
        ],
        "temperature": 0.2,
        "max_tokens": 700,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
    except Exception:
        return None

    overview = (
        data.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
        .strip()
    )
    overview = clean_overview_text(overview) if overview else ""
    return compact_text(overview) if overview else None


async def backfill_missing_ai_overviews(
    domain_id: str | None = None,
    limit: int = 20,
    force: bool = False,
) -> dict[str, Any]:
    """为缺少 AI 概览的历史文章补生成概览。"""
    supabase = get_supabase()
    query = (
        supabase.table("articles")
        .select("id, title, summary, content, source_name, ai_overview")
        .order("fetched_at", desc=True)
        .limit(limit)
    )
    if not force:
        query = query.is_("ai_overview", "null")
    if domain_id:
        query = query.eq("domain_id", domain_id)

    result = query.execute()
    updated = 0
    failed = 0

    for article in result.data:
        overview = await generate_ai_overview(article)
        if not overview:
            failed += 1
            continue

        try:
            (
                supabase.table("articles")
                .update({"ai_overview": overview})
                .eq("id", article["id"])
                .execute()
            )
            updated += 1
        except Exception:
            failed += 1

    return {
        "matched": len(result.data),
        "updated": updated,
        "failed": failed,
    }
