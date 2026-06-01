"""RSS/Atom feed fetcher using feedparser.

Handles RSS 2.0, Atom, and other common feed formats.
Returns normalised article dicts ready for the content pipeline.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from time import mktime
from typing import Any
from urllib.parse import urljoin

import feedparser

from app.services.source_config import SourceConfig

logger = logging.getLogger(__name__)

# User-Agent to avoid being blocked by strict servers.
_USER_AGENT = (
    "Mozilla/5.0 (compatible; DailyNewsBot/1.0; +https://dailynews.example.com)"
)


def _parse_published(entry: dict[str, Any]) -> datetime | None:
    """Extract a timezone-aware datetime from a feed entry.

    Supports the common feedparser date fields and falls back to None.
    """
    for field in ("published_parsed", "updated_parsed", "created_parsed"):
        parsed = entry.get(field)
        if parsed is not None:
            try:
                return datetime.fromtimestamp(mktime(parsed), tz=timezone.utc)
            except (TypeError, ValueError, OverflowError):
                continue

    # Try string-based fields as a last resort.
    for field in ("published", "updated", "created"):
        raw = entry.get(field)
        if raw:
            try:
                return datetime.fromisoformat(raw)
            except (ValueError, TypeError):
                pass
    return None


def _clean_html(raw: str | None) -> str:
    """Strip HTML tags from a string, returning plain text."""
    if not raw:
        return ""
    import re

    text = re.sub(r"<[^>]+>", "", raw)
    text = text.strip()
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)
    return text[:500]  # Cap summary length


def _normalise_image_url(raw_url: str | None, base_url: str) -> str:
    """把 RSS 里的图片地址整理成可访问的完整 URL。"""
    if not raw_url:
        return ""
    value = raw_url.strip()
    if not value or value.startswith(("data:", "blob:", "javascript:")):
        return ""
    return urljoin(base_url, value)


def _append_unique(items: list[str], value: str) -> None:
    """追加不重复的图片地址。"""
    if value and value not in items:
        items.append(value)


def _extract_entry_image_urls(entry: dict[str, Any], source: SourceConfig) -> list[str]:
    """从 RSS 条目中提取封面图候选地址。"""
    image_urls: list[str] = []

    media_content = entry.get("media_content") or []
    if isinstance(media_content, list):
        for item in media_content:
            if isinstance(item, dict):
                _append_unique(
                    image_urls,
                    _normalise_image_url(str(item.get("url") or ""), source.url),
                )

    media_thumbnail = entry.get("media_thumbnail") or []
    if isinstance(media_thumbnail, list):
        for item in media_thumbnail:
            if isinstance(item, dict):
                _append_unique(
                    image_urls,
                    _normalise_image_url(str(item.get("url") or ""), source.url),
                )

    links = entry.get("links") or []
    if isinstance(links, list):
        for item in links:
            if not isinstance(item, dict):
                continue
            content_type = str(item.get("type") or "")
            if content_type.startswith("image/"):
                _append_unique(
                    image_urls,
                    _normalise_image_url(str(item.get("href") or ""), source.url),
                )

    return image_urls[:10]


def fetch_feed(source: SourceConfig) -> list[dict[str, Any]]:
    """Fetch and parse an RSS/Atom feed for the given source.

    Returns a list of article dicts with keys:
        title, link, summary, published_at, source_name, source_url, domain_id
    """
    if source.rss_url is None:
        logger.warning("Source %s has no rss_url configured", source.name)
        return []

    logger.info("Fetching RSS feed: %s (%s)", source.name, source.rss_url)

    try:
        feed = feedparser.parse(
            source.rss_url,
            agent=_USER_AGENT,
        )
    except Exception:
        logger.exception("Failed to fetch RSS feed for %s", source.name)
        return []

    if feed.bozo and not feed.entries:
        logger.warning(
            "Feed %s is malformed and has no entries: %s",
            source.name,
            feed.bozo_exception,
        )
        return []

    articles: list[dict[str, Any]] = []
    for entry in feed.entries:
        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()

        if not title or not link:
            logger.debug("Skipping entry with missing title/link in %s", source.name)
            continue

        raw_summary = entry.get("summary") or entry.get("description")
        if not raw_summary and entry.get("content"):
            raw_summary = entry["content"][0].get("value", "")
        summary = _clean_html(raw_summary)

        published_at = _parse_published(entry)

        articles.append(
            {
                "title": title,
                "link": link,
                "summary": summary,
                "published_at": published_at,
                "source_name": source.name,
                "source_url": source.url,
                "domain_id": source.domain_id,
                "image_urls": _extract_entry_image_urls(entry, source),
            }
        )

    logger.info("Fetched %d articles from %s", len(articles), source.name)
    return articles
