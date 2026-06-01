"""AI 二次分类：根据文章内容判断最终展示领域。"""

from __future__ import annotations

import json
import os
from typing import Any

import httpx

from app.domain_catalog import DOMAIN_NAMES
from app.services.ai_overview import (
    DEFAULT_AI_BASE_URL,
    DEFAULT_AI_MODEL,
    compact_text,
)

_SOURCE_DOMAIN_KEYWORDS: dict[str, tuple[str, ...]] = {
    "ai": ("ai", "人工智能", "大模型", "模型", "智能体", "算力"),
    "business": ("公司", "企业", "商业", "品牌", "财报", "营收", "融资", "ceo", "电商"),
    "career": ("职场", "效率", "团队", "协作", "产品经理", "工作", "管理", "mvp"),
    "education": ("教育", "学习", "学校", "课程", "学生", "教师", "培训", "考试"),
    "finance": ("财经", "金融", "财商", "证券", "银行", "基金", "股票", "宏观", "经济"),
    "gadgets": ("手机", "数码", "硬件", "win10", "电脑", "芯片", "电池"),
    "games": ("游戏", "玩家", "主机", "steam", "ps5", "switch", "玩什么"),
    "media": ("电影", "影视", "剧集", "票房", "导演", "演员"),
    "health": ("健康", "医疗", "疾病", "运动", "腹痛", "心理"),
    "lifestyle": ("生活", "旅行", "美食", "家居", "消费", "城市"),
    "technology": ("科技", "互联网", "软件", "开源", "系统", "智能", "芯片", "硬件"),
}

_ROUTE_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("finance", ("金融", "证券", "基金", "股票", "银行", "资本", "财商", "宏观", "经济")),
    ("ai", ("人工智能", "大模型", "模型", "智能体", "算力", "token")),
    ("games", ("游戏", "玩家", "steam", "ps5", "switch", "任天堂")),
    ("gadgets", ("手机", "数码", "硬件", "win10", "芯片", "机箱", "电脑", "智能眼镜")),
    ("media", ("电影", "影视", "剧集", "票房", "导演", "演员")),
    ("health", ("健康", "医疗", "疾病", "运动", "腹痛", "心理")),
    ("career", ("职场", "团队协作", "产品经理", "项目管理", "mvp")),
    ("education", ("教育", "学校", "课程", "学生", "教师", "学习")),
    ("business", ("企业", "财报", "营收", "融资", "品牌", "产业", "商业", "ceo")),
)


def _source_domain(article: dict[str, Any]) -> str:
    """读取文章来源领域。"""
    return str(article.get("source_domain_id") or article.get("domain_id") or "")


def _fallback_result(article: dict[str, Any], reason: str) -> dict[str, str]:
    """分类失败时沿用来源领域。"""
    source_domain_id = _source_domain(article)
    if source_domain_id not in DOMAIN_NAMES:
        source_domain_id = "technology"
    return {"domain_id": source_domain_id, "reason": reason}


def _source_keyword_result(article: dict[str, Any]) -> dict[str, str] | None:
    """垂直来源命中强关键词时，优先沿用来源领域。"""
    source_domain_id = _source_domain(article)
    keywords = _SOURCE_DOMAIN_KEYWORDS.get(source_domain_id)
    if not keywords:
        return None

    text = " ".join(
        str(article.get(key) or "") for key in ("title", "summary", "content")
    ).lower()
    if any(keyword.lower() in text for keyword in keywords):
        return {"domain_id": source_domain_id, "reason": "来源领域关键词匹配"}
    return None


def _route_keyword_result(article: dict[str, Any]) -> dict[str, str] | None:
    """明显命中领域关键词时，先做确定性分类。"""
    text = " ".join(
        str(article.get(key) or "") for key in ("title", "summary", "content")
    ).lower()
    for domain_id, keywords in _ROUTE_KEYWORDS:
        if any(keyword.lower() in text for keyword in keywords):
            return {"domain_id": domain_id, "reason": "关键词规则分类"}
    return None


def build_classification_prompt(article: dict[str, Any]) -> str:
    """生成 AI 分类提示词。"""
    title = article.get("title") or ""
    summary = article.get("summary") or ""
    content = article.get("content") or ""
    source = article.get("source_name") or ""
    source_domain_id = _source_domain(article)
    domain_lines = "\n".join(
        f"- {domain_id}={domain_name}" for domain_id, domain_name in DOMAIN_NAMES.items()
    )
    raw_text = compact_text(f"{summary}\n{content}", limit=2500)

    return (
        "你是资讯分类器。请只从下面 12 个领域里选择最适合文章展示的一个领域。\n"
        "如果文章同时涉及多个领域，选择文章主体最直接讨论的领域。\n"
        "只输出 JSON，不要 Markdown，不要解释。\n"
        '格式：{"domain_id":"gadgets","reason":"一句话原因"}\n\n'
        f"可选领域：\n{domain_lines}\n\n"
        f"来源领域：{source_domain_id}\n来源：{source}\n标题：{title}\n内容：{raw_text}"
    )


def parse_classification_domain(value: str) -> str | None:
    """从模型返回内容里解析领域 ID。"""
    text = value.strip()
    if not text:
        return None

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = None

    domain_id = ""
    if isinstance(data, dict):
        domain_id = str(data.get("domain_id") or "").strip()
        if domain_id not in DOMAIN_NAMES:
            domain_id = next(
                (
                    candidate_id
                    for candidate_id, domain_name in DOMAIN_NAMES.items()
                    if domain_id == domain_name
                ),
                domain_id,
            )
    else:
        for candidate in DOMAIN_NAMES:
            if candidate in text:
                domain_id = candidate
                break
        if not domain_id:
            for candidate_id, domain_name in DOMAIN_NAMES.items():
                if domain_name in text:
                    domain_id = candidate_id
                    break

    return domain_id if domain_id in DOMAIN_NAMES else None


def _parse_reason(value: str) -> str:
    """从模型返回内容里解析分类原因。"""
    try:
        data = json.loads(value.strip())
    except json.JSONDecodeError:
        return ""
    if not isinstance(data, dict):
        return ""
    reason = str(data.get("reason") or "").strip()
    return compact_text(reason, limit=80)


async def classify_article_domain(article: dict[str, Any]) -> dict[str, str]:
    """调用 AI 判断文章最终展示领域，失败时沿用来源领域。"""
    route_result = _route_keyword_result(article)
    if route_result:
        return route_result

    source_result = _source_keyword_result(article)
    if source_result:
        return source_result

    api_key = os.getenv("AI_API_KEY")
    if not api_key:
        return _fallback_result(article, "未配置 AI，沿用来源领域")

    base_url = os.getenv("AI_BASE_URL", DEFAULT_AI_BASE_URL).rstrip("/")
    model = os.getenv("AI_MODEL", DEFAULT_AI_MODEL)
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": build_classification_prompt(article)}],
        "temperature": 0.1,
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
        return _fallback_result(article, "AI 分类失败，沿用来源领域")

    content = (
        data.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
        .strip()
    )
    domain_id = parse_classification_domain(content)
    if not domain_id:
        return _fallback_result(article, "AI 分类结果无效，沿用来源领域")

    return {
        "domain_id": domain_id,
        "reason": _parse_reason(content) or "AI 二次分类",
    }
