"""文章质量过滤：拦截站点杂项、空内容和明显跑偏的候选资讯。"""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse


_INVALID_TITLE_PATTERNS = [
    r"网站地图",
    r"第[一二三四五六七八九十\d]+周作业",
    r"\d{6,}.*作业",
    r"作业\s*[-_—]",
    r"^Gadio News$",
    r"^创作笔记$",
    r"^本文已获转载授权$",
    r"^by\s+",
    r"^\d+\s*人做过",
    r"概况$",
    r"^~",
]

_INVALID_TEXT_PATTERNS = [
    r"文章内容为空",
    r"请补充文章内容",
    r"无法提取核心事实",
    r"没有实际内容可以总结",
]

_BLOCKED_PATH_PARTS = (
    "sitemap",
    "tag/",
    "tags/",
    "login",
    "register",
    "search",
    "about",
    "contact",
)

_DOMAIN_KEYWORDS: dict[str, tuple[str, ...]] = {
    "ai": (
        "ai",
        "人工智能",
        "大模型",
        "模型",
        "机器学习",
        "深度学习",
        "算法",
        "智能体",
        "算力",
        "openai",
        "claude",
        "gemini",
    ),
    "gadgets": (
        "手机",
        "数码",
        "iphone",
        "安卓",
        "小米",
        "华为",
        "oppo",
        "vivo",
        "荣耀",
        "平板",
        "笔记本",
        "耳机",
        "芯片",
        "硬件",
        "相机",
        "充电",
        "电池",
        "智能车",
        "新车",
    ),
    "business": (
        "公司",
        "企业",
        "融资",
        "财报",
        "营收",
        "ceo",
        "品牌",
        "电商",
        "商业",
        "市场",
        "投资",
        "并购",
    ),
    "finance": (
        "财经",
        "经济",
        "宏观",
        "金融",
        "股",
        "基金",
        "债",
        "利率",
        "汇率",
        "银行",
        "上市",
        "财报",
    ),
    "career": (
        "职场",
        "效率",
        "产品经理",
        "工作",
        "管理",
        "招聘",
        "面试",
        "办公",
        "团队",
        "创业",
    ),
    "education": (
        "教育",
        "学校",
        "学生",
        "课程",
        "学习",
        "教师",
        "培训",
        "大学",
        "高考",
        "考试",
    ),
    "games": (
        "游戏",
        "手游",
        "主机",
        "steam",
        "任天堂",
        "索尼",
        "xbox",
        "ps5",
        "switch",
        "电竞",
        "发售",
        "玩家",
        "dlc",
        "玩什么",
    ),
    "media": (
        "电影",
        "影视",
        "剧集",
        "综艺",
        "票房",
        "流媒体",
        "影院",
        "导演",
        "演员",
        "播出",
    ),
    "health": (
        "健康",
        "医疗",
        "心理",
        "疾病",
        "用药",
        "医生",
        "医院",
        "睡眠",
        "运动",
        "营养",
    ),
    "lifestyle": (
        "生活",
        "方式",
        "旅行",
        "美食",
        "家居",
        "消费",
        "运动",
        "咖啡",
        "时尚",
        "城市",
    ),
    "technology": (
        "科技",
        "互联网",
        "软件",
        "开源",
        "系统",
        "数据",
        "云",
        "芯片",
        "网络",
        "安全",
        "编程",
        "编码",
    ),
}

_STRICT_DOMAIN_IDS = {"ai", "gadgets", "games", "media", "health", "lifestyle"}


def _text_blob(article: dict[str, Any]) -> str:
    """拼接文章标题、摘要和正文，供规则判断使用。"""
    return " ".join(
        str(article.get(key) or "") for key in ("title", "summary", "content")
    ).lower()


def is_generic_or_invalid_title(title: str) -> bool:
    """判断标题是否像栏目名、署名或无效页面标题。"""
    cleaned = " ".join(str(title or "").split())
    if len(cleaned) < 6:
        return True
    return any(re.search(pattern, cleaned, re.IGNORECASE) for pattern in _INVALID_TITLE_PATTERNS)


def should_replace_title(current_title: str, crawled_title: str) -> bool:
    """判断原文页标题是否应该替换列表页标题。"""
    current = " ".join(str(current_title or "").split())
    crawled = " ".join(str(crawled_title or "").split())
    if is_generic_or_invalid_title(current) and len(crawled) >= 8:
        return True
    return len(crawled) >= 12 and len(crawled) > len(current) + 8


def is_valid_article_candidate(
    article: dict[str, Any],
    domain_id: str | None = None,
) -> bool:
    """判断候选文章是否值得进入后续 AI 解析和入库。"""
    title = str(article.get("title") or "")
    if is_generic_or_invalid_title(title):
        return False

    link = str(article.get("link") or article.get("source_url") or "")
    path = urlparse(link).path.lower()
    if any(part in path for part in _BLOCKED_PATH_PARTS):
        return False

    text = _text_blob(article)
    if any(re.search(pattern, text, re.IGNORECASE) for pattern in _INVALID_TEXT_PATTERNS):
        return False

    article_domain_id = domain_id or str(article.get("domain_id") or "")
    if article_domain_id not in _STRICT_DOMAIN_IDS:
        return True

    keywords = _DOMAIN_KEYWORDS.get(article_domain_id)
    if not keywords:
        return True
    return any(keyword.lower() in text for keyword in keywords)
