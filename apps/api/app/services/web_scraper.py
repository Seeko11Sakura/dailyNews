"""Web scraper for sources without RSS feeds.

Uses httpx for HTTP requests and BeautifulSoup for HTML parsing.
Includes per-domain rate limiting (1 request/second).
"""

from __future__ import annotations

import asyncio
import logging
import re
import time
from typing import Any
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup, Tag

from app.services.article_quality import is_valid_article_candidate
from app.services.source_config import SourceConfig

logger = logging.getLogger(__name__)

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)

# Per-domain rate-limit timestamps: domain -> last request time.
_last_request_time: dict[str, float] = {}
_rate_limit_lock = asyncio.Lock()

# Default request timeout.
_TIMEOUT = httpx.Timeout(15.0, connect=10.0)


async def _rate_limit(domain: str) -> None:
    """Enforce at most 1 request per second per domain."""
    async with _rate_limit_lock:
        now = time.monotonic()
        last = _last_request_time.get(domain, 0.0)
        wait = 1.0 - (now - last)
        if wait > 0:
            await asyncio.sleep(wait)
        _last_request_time[domain] = time.monotonic()


def _extract_text(tag: Tag | None) -> str:
    """Extract and clean text from a BeautifulSoup tag."""
    if tag is None:
        return ""
    text = tag.get_text(strip=True)
    text = re.sub(r"\s+", " ", text)
    return text[:500]


def _extract_link(tag: Tag | None, base_url: str) -> str:
    """Extract href from a tag and resolve it to an absolute URL."""
    if tag is None:
        return ""
    href = tag.get("href", "")
    if not href:
        return ""
    return urljoin(base_url, href)


def _parse_articles_from_html(
    html: str,
    source: SourceConfig,
) -> list[dict[str, Any]]:
    """Parse article list from HTML using configurable CSS selectors."""
    soup = BeautifulSoup(html, "html.parser")

    selectors = source.css_selectors
    article_list_sel = selectors.get("article_list", "article a, .article a")
    title_sel = selectors.get("title", "h2, h3, .title")
    link_sel = selectors.get("link", "a[href]")

    articles: list[dict[str, Any]] = []
    seen_links: set[str] = set()

    containers = soup.select(article_list_sel)
    for container in containers[:30]:  # Cap at 30 to avoid noise.
        # Find the link element.
        link_el = container.select_one(link_sel) if container.name != "a" else container
        if link_el is None:
            # The container itself might be the link.
            link_el = container if container.name == "a" else None

        # Find the title element.
        title_el = container.select_one(title_sel)
        title = _extract_text(title_el)
        if not title:
            # Fallback: use the link text.
            title = _extract_text(container if container.name == "a" else link_el)
        if not title or len(title) < 4:
            continue

        link = _extract_link(link_el, source.url)
        if not link or link in seen_links:
            continue
        # Skip anchor-only and javascript links.
        if link.startswith("#") or link.startswith("javascript:"):
            continue
        if not _looks_like_article_link(link, title, source.url):
            continue
        if not is_valid_article_candidate(
            {"title": title, "link": link},
            source.domain_id,
        ):
            continue
        seen_links.add(link)

        articles.append(
            {
                "title": title,
                "link": link,
                "summary": "",
                "published_at": None,
                "source_name": source.name,
                "source_url": source.url,
                "domain_id": source.domain_id,
            }
        )

    return articles


def _looks_like_article_link(link: str, title: str, source_url: str) -> bool:
    """判断一个普通链接是否像文章链接。"""
    if len(title) < 6:
        return False

    parsed = urlparse(link)
    source_host = urlparse(source_url).netloc.removeprefix("www.")
    link_host = parsed.netloc.removeprefix("www.")
    if source_host and link_host and source_host != link_host:
        return False

    path = parsed.path.lower()
    if not path or path in {"/", "#"}:
        return False
    if any(
        blocked in path
        for blocked in (
            "login",
            "register",
            "signup",
            "search",
            "sitemap",
            "tag/",
            "tags/",
            "about",
            "contact",
            "video",
            ".jpg",
            ".png",
            ".gif",
            ".css",
            ".js",
        )
    ):
        return False

    article_markers = (
        "article",
        "articles",
        "news",
        "post",
        "detail",
        "story",
        "content",
        "item",
        "/p/",
        "recipe",
        "202",
    )
    return any(marker in path for marker in article_markers) or bool(
        re.search(r"/\d{5,}", path)
        or re.search(r"/\d+/\d+/\d+\.html?$", path)
    )


def _parse_article_links_fallback(
    html: str,
    source: SourceConfig,
) -> list[dict[str, Any]]:
    """专用选择器失效时，从页面所有链接里兜底识别文章。"""
    soup = BeautifulSoup(html, "html.parser")
    articles: list[dict[str, Any]] = []
    seen_links: set[str] = set()
    for anchor in soup.select("a[href]"):
        link = _extract_link(anchor, source.url)
        title = _extract_text(anchor)
        if not link or link in seen_links:
            continue
        if not _looks_like_article_link(link, title, source.url):
            continue
        if not is_valid_article_candidate(
            {"title": title, "link": link},
            source.domain_id,
        ):
            continue

        seen_links.add(link)
        articles.append(
            {
                "title": title,
                "link": link,
                "summary": "",
                "published_at": None,
                "source_name": source.name,
                "source_url": source.url,
                "domain_id": source.domain_id,
            }
        )
        if len(articles) >= 30:
            break

    return articles


async def scrape_source(
    source: SourceConfig,
    client: httpx.AsyncClient | None = None,
) -> list[dict[str, Any]]:
    """Scrape article list from a web source.

    Returns a list of article dicts with keys matching the RSS fetcher output.
    """
    if source.source_type != "web":
        logger.warning("Source %s is not a web source, skipping", source.name)
        return []

    logger.info("Scraping web source: %s (%s)", source.name, source.url)

    own_client = client is None
    if own_client:
        client = httpx.AsyncClient(
            headers={"User-Agent": _USER_AGENT},
            timeout=_TIMEOUT,
            follow_redirects=True,
        )

    try:
        # Extract domain for rate limiting (strip port, path, etc.).
        from urllib.parse import urlparse

        parsed = urlparse(source.url)
        domain = parsed.netloc

        await _rate_limit(domain)

        response = await client.get(source.url)
        response.raise_for_status()

        articles = _parse_articles_from_html(response.text, source)
        if not articles:
            articles = _parse_article_links_fallback(response.text, source)
        logger.info("Scraped %d articles from %s", len(articles), source.name)
        return articles

    except httpx.HTTPStatusError as exc:
        logger.warning(
            "HTTP %d from %s: %s", exc.response.status_code, source.name, exc
        )
        return []
    except httpx.RequestError as exc:
        logger.warning("Request error for %s: %s", source.name, exc)
        return []
    except Exception:
        logger.exception("Unexpected error scraping %s", source.name)
        return []
    finally:
        if own_client and client:
            await client.aclose()


async def scrape_multiple_sources(
    sources: list[SourceConfig],
) -> dict[str, list[dict[str, Any]]]:
    """Scrape multiple web sources concurrently (respecting rate limits).

    Returns a dict mapping source_name -> list of article dicts.
    """
    results: dict[str, list[dict[str, Any]]] = {}

    async with httpx.AsyncClient(
        headers={"User-Agent": _USER_AGENT},
        timeout=_TIMEOUT,
        follow_redirects=True,
    ) as client:
        tasks = {
            source.name: asyncio.create_task(scrape_source(source, client))
            for source in sources
            if source.source_type == "web" and source.active
        }

        for name, task in tasks.items():
            try:
                results[name] = await task
            except Exception:
                logger.exception("Task failed for %s", name)
                results[name] = []

    return results
