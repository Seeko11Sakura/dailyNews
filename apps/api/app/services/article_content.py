"""文章正文提取：在详情页需要时从原文站补抓完整正文。"""

from __future__ import annotations

import logging
import re

import httpx
from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)

_CONTENT_SELECTORS = [
    "article",
    "[itemprop='articleBody']",
    ".c-article-content",
    ".article-content",
    ".entry-content",
    ".post-content",
    ".content",
    ".article",
]

_NOISE_SELECTORS = [
    "script",
    "style",
    "noscript",
    "nav",
    "footer",
    "header",
    ".share",
    ".comment",
    ".comments",
    ".related",
    ".recommend",
    ".advertisement",
    ".ad",
]

_MIN_CONTENT_CHARS = 80


def _clean_text(value: str) -> str:
    """清理正文中的多余空白和站点噪音。"""
    text = re.sub(r"[ \t\r\f\v]+", " ", value).strip()
    text = re.sub(r"(分享到微信|使用微信扫码将网页分享到微信)", "", text)
    return text.strip()


def _paragraphs_from_tag(tag: Tag) -> list[str]:
    """从正文节点中按块级元素提取段落。"""
    paragraphs: list[str] = []
    block_tags = tag.select("p, h2, h3, h4, li, blockquote")
    for block in block_tags:
        text = _clean_text(block.get_text(" ", strip=True))
        if len(text) >= 8:
            paragraphs.append(text)
    return paragraphs


def _text_from_tag(tag: Tag) -> str:
    """从候选正文节点提取纯文本。"""
    for noisy in tag.select(",".join(_NOISE_SELECTORS)):
        noisy.decompose()
    paragraphs = _paragraphs_from_tag(tag)
    if paragraphs:
        return "\n\n".join(paragraphs)
    return _clean_text(tag.get_text(" ", strip=True))


def extract_article_content(html: str) -> str:
    """从网页 HTML 中提取最像正文的一段文本。"""
    soup = BeautifulSoup(html, "html.parser")
    candidates: list[str] = []

    for selector in _CONTENT_SELECTORS:
        for tag in soup.select(selector):
            text = _text_from_tag(tag)
            if len(text) >= _MIN_CONTENT_CHARS:
                candidates.append(text)

    if not candidates:
        paragraphs = [_clean_text(p.get_text(" ", strip=True)) for p in soup.find_all("p")]
        text = "\n\n".join(p for p in paragraphs if len(p) >= 20)
        if len(text) >= _MIN_CONTENT_CHARS:
            candidates.append(text)

    if not candidates:
        return ""

    return max(candidates, key=len)


def fetch_article_content(source_url: str) -> str:
    """打开原文链接并提取正文，失败时返回空字符串。"""
    if not source_url:
        return ""

    try:
        response = httpx.get(
            source_url,
            headers={"User-Agent": _USER_AGENT},
            timeout=15.0,
            follow_redirects=True,
        )
        response.raise_for_status()
    except Exception as exc:
        logger.warning("Failed to fetch article content from %s: %s", source_url, exc)
        return ""

    return extract_article_content(response.text)
