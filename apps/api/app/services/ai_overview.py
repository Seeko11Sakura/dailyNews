"""AI 概览服务：把抓取到的原文压缩成适合卡片展示的短内容。"""

from __future__ import annotations

import os
from typing import Any

import httpx

DEFAULT_AI_BASE_URL = "https://token-plan-cn.xiaomimimo.com/v1"
DEFAULT_AI_MODEL = "mimo-v2.5-pro"
MAX_OVERVIEW_CHARS = 120


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
        "请用中文为下面这篇资讯生成一段适合手机卡片展示的概览。"
        "要求：只输出概览本身，不要标题；60 到 100 个中文字符；"
        "说清楚核心事实和影响，不要照抄原文。\n\n"
        f"来源：{source}\n标题：{title}\n内容：{raw_text}"
    )


async def generate_ai_overview(article: dict[str, Any]) -> str:
    """调用兼容 OpenAI 的接口生成短概览，失败时返回短兜底文本。"""
    fallback = compact_text(
        article.get("summary") or article.get("content") or article.get("title")
    )
    api_key = os.getenv("AI_API_KEY")
    if not api_key:
        return fallback

    base_url = os.getenv("AI_BASE_URL", DEFAULT_AI_BASE_URL).rstrip("/")
    model = os.getenv("AI_MODEL", DEFAULT_AI_MODEL)
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "你是新闻编辑，只生成简短、准确、可读的中文资讯概览。",
            },
            {"role": "user", "content": build_overview_prompt(article)},
        ],
        "temperature": 0.2,
        "max_tokens": 160,
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
        return fallback

    overview = (
        data.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
        .strip()
    )
    return compact_text(overview or fallback)
