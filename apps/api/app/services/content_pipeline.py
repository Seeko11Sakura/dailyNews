"""Content pipeline — orchestrates fetching from all sources and stores articles.

Coordinates RSS fetching and web scraping, deduplicates via URL hash,
persists to Supabase, and tracks per-source fetch status.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from app.repositories.base import get_supabase
from app.services.ai_overview import generate_ai_overview
from app.services.rss_fetcher import fetch_feed
from app.services.source_config import (
    SOURCES_BY_NAME,
    SourceConfig,
    get_active_sources,
)
from app.services.title_folder import fold_similar_titles, title_hash
from app.services.url_normalizer import url_hash
from app.services.web_scraper import scrape_source

logger = logging.getLogger(__name__)

# In-memory fetch status tracker (source_name -> last fetch metadata).
_fetch_status: dict[str, dict[str, Any]] = {}


def _is_missing_ai_overview_column(exc: Exception) -> bool:
    """判断 Supabase 是否还没有执行 ai_overview 字段迁移。"""
    message = str(exc)
    return "ai_overview" in message and "42703" in message


# ---------------------------------------------------------------------------
# Article enrichment & dedup helpers (reuse url_normalizer + title_folder)
# ---------------------------------------------------------------------------


async def check_url_exists(source_url: str) -> bool:
    """Return True if the normalized URL already exists in the articles table."""
    supabase = get_supabase()
    h = url_hash(source_url)
    result = (
        supabase.table("articles")
        .select("id")
        .eq("url_hash", h)
        .limit(1)
        .execute()
    )
    return len(result.data) > 0


def enrich_article(article: dict[str, Any]) -> dict[str, Any]:
    """Add url_hash and title_similarity_hash to an article dict before insert.

    Does NOT mutate the original dict -- returns a new dict.
    """
    enriched = dict(article)
    enriched["url_hash"] = url_hash(article["source_url"])
    enriched["title_similarity_hash"] = title_hash(article["title"])
    return enriched


async def filter_new_articles(articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Filter out articles whose normalized URL already exists in the database.

    Returns only articles that are new (not yet stored).
    """
    if not articles:
        return []

    supabase = get_supabase()

    # Collect all hashes in one query for efficiency.
    hashes = [url_hash(a["source_url"]) for a in articles]
    existing = (
        supabase.table("articles")
        .select("url_hash")
        .in_("url_hash", hashes)
        .execute()
    )
    existing_hashes = {row["url_hash"] for row in existing.data}

    return [
        enrich_article(a)
        for a in articles
        if url_hash(a["source_url"]) not in existing_hashes
    ]


async def process_fetched_articles(
    articles: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Full pipeline: dedup by URL, fold by title, return enriched articles.

    Steps:
    1. Filter out articles whose URL hash already exists in DB.
    2. Enrich remaining articles with url_hash and title_similarity_hash.
    3. Run title folding to mark near-duplicates.

    Returns the processed list with `is_duplicate` and `similar_count` fields
    added.  Callers should only insert articles where `is_duplicate == False`.
    """
    new_articles = await filter_new_articles(articles)
    return fold_similar_titles(new_articles)


async def insert_articles(articles: list[dict[str, Any]]) -> int:
    """Insert processed (non-duplicate) articles into Supabase.

    Expects articles to already have url_hash and title_similarity_hash.
    Only inserts articles where is_duplicate is False.

    Returns the number of articles inserted.
    """
    if not articles:
        return 0

    supabase = get_supabase()
    now = datetime.now(timezone.utc).isoformat()
    inserted = 0

    for article in articles:
        if article.get("is_duplicate", False):
            continue

        row = {
            "domain_id": article.get("domain_id", ""),
            "title": article["title"],
            "summary": article.get("summary", ""),
            "ai_overview": article.get("ai_overview")
            or await generate_ai_overview(article),
            "content": article.get("content") or article.get("summary", ""),
            "source_url": article["source_url"],
            "source_name": article.get("source_name", ""),
            "published_at": article.get("published_at"),
            "fetched_at": now,
            "fetch_status": "success",
            "url_hash": article["url_hash"],
            "title_similarity_hash": article["title_similarity_hash"],
        }

        # Ensure published_at is a string for Supabase.
        published = row["published_at"]
        if isinstance(published, datetime):
            row["published_at"] = published.isoformat()

        try:
            supabase.table("articles").insert(row).execute()
            inserted += 1
        except Exception as exc:
            if _is_missing_ai_overview_column(exc):
                row_without_ai = dict(row)
                row_without_ai.pop("ai_overview", None)
                supabase.table("articles").insert(row_without_ai).execute()
                inserted += 1
                continue
            logger.exception(
                "Failed to insert article: %s", row.get("source_url", "unknown")
            )

    return inserted


# ---------------------------------------------------------------------------
# Source-level fetching orchestration
# ---------------------------------------------------------------------------


async def fetch_source(source_name: str) -> dict[str, Any]:
    """Fetch articles from a single named source.

    Returns a status dict:
        {
            "source": str,
            "domain_id": str,
            "tier": str,
            "source_type": str,
            "status": "success" | "error",
            "articles_fetched": int,
            "articles_inserted": int,
            "timestamp": str,
            "error": str | None,
        }
    """
    source = SOURCES_BY_NAME.get(source_name)
    if source is None:
        return {
            "source": source_name,
            "status": "error",
            "articles_fetched": 0,
            "articles_inserted": 0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": f"Unknown source: {source_name}",
        }

    now = datetime.now(timezone.utc).isoformat()

    try:
        if source.source_type == "rss":
            raw_articles = fetch_feed(source)
        else:
            raw_articles = await scrape_source(source)

        # Convert RSS fetcher output format to pipeline format.
        normalised: list[dict[str, Any]] = []
        for a in raw_articles:
            normalised.append(
                {
                    "title": a["title"],
                    "source_url": a["link"],
                    "summary": a.get("summary", ""),
                    "content": a.get("summary", ""),
                    "source_name": a.get("source_name", source.name),
                    "domain_id": a.get("domain_id", source.domain_id),
                    "published_at": a.get("published_at"),
                }
            )

        # Run through dedup + title folding pipeline.
        processed = await process_fetched_articles(normalised)
        inserted = await insert_articles(processed)

        status = {
            "source": source_name,
            "domain_id": source.domain_id,
            "tier": source.tier,
            "source_type": source.source_type,
            "status": "success",
            "articles_fetched": len(raw_articles),
            "articles_inserted": inserted,
            "timestamp": now,
            "error": None,
        }
        _fetch_status[source_name] = status
        return status

    except Exception as exc:
        error_msg = str(exc)
        logger.exception("Error fetching source %s", source_name)
        status = {
            "source": source_name,
            "domain_id": source.domain_id,
            "tier": source.tier,
            "source_type": source.source_type,
            "status": "error",
            "articles_fetched": 0,
            "articles_inserted": 0,
            "timestamp": now,
            "error": error_msg,
        }
        _fetch_status[source_name] = status
        return status


async def fetch_all_sources(
    domain_id: str | None = None,
    tier: str | None = None,
) -> dict[str, Any]:
    """Fetch articles from all active sources (optionally filtered).

    Args:
        domain_id: If set, only fetch sources for this domain.
        tier: If set, only fetch sources of this tier ("A", "B", "C").

    Returns a summary dict:
        {
            "total_sources": int,
            "success_count": int,
            "error_count": int,
            "total_articles_fetched": int,
            "total_articles_inserted": int,
            "results": list[dict],
        }
    """
    sources = get_active_sources()

    if domain_id:
        sources = [s for s in sources if s.domain_id == domain_id]
    if tier:
        sources = [s for s in sources if s.tier == tier]

    results: list[dict[str, Any]] = []
    for source in sources:
        result = await fetch_source(source.name)
        results.append(result)

    success_count = sum(1 for r in results if r["status"] == "success")
    error_count = sum(1 for r in results if r["status"] == "error")
    total_fetched = sum(r["articles_fetched"] for r in results)
    total_inserted = sum(r["articles_inserted"] for r in results)

    summary = {
        "total_sources": len(sources),
        "success_count": success_count,
        "error_count": error_count,
        "total_articles_fetched": total_fetched,
        "total_articles_inserted": total_inserted,
        "results": results,
    }

    logger.info(
        "Fetch complete: %d/%d sources succeeded, "
        "%d articles fetched, %d inserted",
        success_count,
        len(sources),
        total_fetched,
        total_inserted,
    )

    return summary


# ---------------------------------------------------------------------------
# Fetch status queries
# ---------------------------------------------------------------------------


def get_fetch_status() -> dict[str, dict[str, Any]]:
    """Return the last fetch status for all sources that have been fetched."""
    return dict(_fetch_status)


def get_fetch_status_for_source(source_name: str) -> dict[str, Any] | None:
    """Return the last fetch status for a specific source."""
    return _fetch_status.get(source_name)
