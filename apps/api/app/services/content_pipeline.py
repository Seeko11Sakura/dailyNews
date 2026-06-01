"""内容采集流水线：从网页来源抓取文章候选，补全文、分类后写入数据库。"""

from __future__ import annotations

import logging
import os
import asyncio
from datetime import datetime, time, timedelta, timezone
from typing import Any

from app.repositories.base import get_supabase
from app.services.ai_overview import generate_ai_overview
from app.services.article_classifier import classify_article_domain
from app.services.article_crawler import crawl_article
from app.services.article_quality import (
    is_valid_article_candidate,
    should_replace_title,
)
from app.services.image_storage import store_article_images
from app.services.source_config import (
    SOURCES_BY_NAME,
    SourceConfig,
    get_active_sources,
)
from app.services.title_folder import fold_similar_titles, title_hash
from app.services.url_normalizer import url_hash
from app.services.web_scraper import scrape_source

logger = logging.getLogger(__name__)
LOCAL_TZ = timezone(timedelta(hours=8))

# In-memory fetch status tracker (source_name -> last fetch metadata).
_fetch_status: dict[str, dict[str, Any]] = {}


def _source_fetch_concurrency() -> int:
    """读取来源并发数，避免 78 个来源顺序阻塞。"""
    raw_value = os.getenv("SOURCE_FETCH_CONCURRENCY", "8")
    try:
        return max(1, int(raw_value))
    except ValueError:
        return 4


def _source_fetch_timeout_seconds() -> float:
    """读取单个来源抓取超时时间。"""
    raw_value = os.getenv("SOURCE_FETCH_TIMEOUT_SECONDS", "60")
    try:
        return max(10.0, float(raw_value))
    except ValueError:
        return 60.0


def _source_article_limit() -> int:
    """读取每个来源单次最多处理的文章数。"""
    raw_value = os.getenv("SOURCE_ARTICLE_LIMIT", "10")
    try:
        return max(1, int(raw_value))
    except ValueError:
        return 10


def _fallback_published_at(now: str) -> str:
    """没有发布时间时，按简报窗口给文章补一个可展示时间。"""
    current = datetime.fromisoformat(now).astimezone(LOCAL_TZ)
    if current.time() < time(hour=8):
        previous_day_end = datetime.combine(
            current.date(),
            time.min,
            tzinfo=LOCAL_TZ,
        ) - timedelta(minutes=1)
        return previous_day_end.astimezone(timezone.utc).isoformat()
    return now


def _is_missing_ai_overview_column(exc: Exception) -> bool:
    """判断 Supabase 是否还没有执行 ai_overview 字段迁移。"""
    message = str(exc)
    return "ai_overview" in message and "42703" in message


def _is_missing_optional_article_column(exc: Exception) -> bool:
    """判断 Supabase 是否缺少可选的文章增强字段。"""
    message = str(exc)
    is_schema_error = (
        "42703" in message
        or "PGRST204" in message
        or "Could not find" in message
    )
    return is_schema_error and bool(_optional_columns_to_remove(message))


def _optional_columns_to_remove(message: str) -> set[str]:
    """根据数据库错误判断需要移除哪些可选字段。"""
    columns: set[str] = set()
    if "ai_overview" in message:
        columns.add("ai_overview")
    if "source_domain_id" in message or "classification_reason" in message:
        columns.update({"source_domain_id", "classification_reason"})
    if "cover_image_url" in message:
        columns.add("cover_image_url")
    return columns


def _insert_article_row(supabase: Any, row: dict[str, Any]) -> Any:
    """插入文章，旧库缺少可选字段时自动降级重试。"""
    insert_row = dict(row)
    for _ in range(4):
        try:
            return supabase.table("articles").insert(insert_row).execute()
        except Exception as exc:
            if not _is_missing_optional_article_column(exc):
                raise
            for column in _optional_columns_to_remove(str(exc)):
                insert_row.pop(column, None)
    return supabase.table("articles").insert(insert_row).execute()


def _update_article_row(supabase: Any, article_id: str, row: dict[str, Any]) -> Any:
    """更新已存在文章，旧库缺少可选字段时自动降级重试。"""
    update_row = dict(row)
    for _ in range(4):
        try:
            return (
                supabase.table("articles")
                .update(update_row)
                .eq("id", article_id)
                .execute()
            )
        except Exception as exc:
            if not _is_missing_optional_article_column(exc):
                raise
            for column in _optional_columns_to_remove(str(exc)):
                update_row.pop(column, None)
    return supabase.table("articles").update(update_row).eq("id", article_id).execute()


def _should_crawl_article_images() -> bool:
    """判断是否在入库后补抓原文图片。"""
    value = os.getenv("ARTICLE_IMAGE_CRAWL_ENABLED", "false").lower()
    return value not in {"0", "false", "no"}


def _inserted_article_id(result: Any) -> str:
    """从 Supabase 插入结果中读取文章 ID。"""
    data = getattr(result, "data", None)
    if isinstance(data, list) and data:
        article_id = data[0].get("id")
        return str(article_id or "")
    return ""


def _resolve_article_image_urls(article: dict[str, Any]) -> list[str]:
    """优先使用已有图片地址，没有时再打开原文页补抓。"""
    image_urls = article.get("image_urls") or []
    if image_urls:
        return list(image_urls)

    source_url = article.get("source_url")
    if not source_url or not _should_crawl_article_images():
        return []

    try:
        preview = crawl_article(source_url)
    except Exception as exc:
        logger.warning("Failed to crawl article images from %s: %s", source_url, exc)
        return []

    preview_urls = preview.get("image_urls") or []
    return list(preview_urls) if isinstance(preview_urls, list) else []


def _store_images_for_article(
    supabase: Any,
    article_id: str,
    article: dict[str, Any],
) -> None:
    """保存文章图片，并把第一张图写回文章封面。"""
    if not article_id:
        return

    image_urls = _resolve_article_image_urls(article)
    if not image_urls:
        return

    records = store_article_images(article_id, image_urls, supabase=supabase)
    if not records:
        return

    cover_url = records[0].get("public_url")
    if not cover_url:
        return

    try:
        supabase.table("articles").update({"cover_image_url": cover_url}).eq(
            "id", article_id
        ).execute()
    except Exception as exc:
        logger.warning("Failed to update article cover image %s: %s", article_id, exc)


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


def enrich_article_with_crawler(article: dict[str, Any]) -> dict[str, Any]:
    """打开原文页补充完整正文和图片地址。"""
    source_url = article.get("source_url")
    if not source_url:
        return article

    try:
        preview = crawl_article(source_url)
    except Exception as exc:
        logger.warning("Failed to enrich article from %s: %s", source_url, exc)
        return article

    enriched = dict(article)
    crawled_title = str(preview.get("title") or "")
    if should_replace_title(str(enriched.get("title") or ""), crawled_title):
        enriched["title"] = crawled_title

    crawled_content = str(preview.get("content") or "")
    current_content = str(enriched.get("content") or "")
    if len(crawled_content) > len(current_content):
        enriched["content"] = crawled_content

    image_urls = preview.get("image_urls") or []
    if isinstance(image_urls, list) and image_urls:
        enriched["image_urls"] = image_urls

    crawled_published_at = preview.get("published_at")
    if crawled_published_at:
        enriched["published_at"] = crawled_published_at

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
        .select("id, url_hash")
        .in_("url_hash", hashes)
        .execute()
    )
    existing_by_hash = {row["url_hash"]: row["id"] for row in existing.data}

    enriched_articles: list[dict[str, Any]] = []
    for article in articles:
        enriched = enrich_article(article)
        existing_id = existing_by_hash.get(enriched["url_hash"])
        if existing_id:
            enriched["existing_article_id"] = existing_id
        enriched_articles.append(enriched)
    return enriched_articles


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
    enriched_articles = await asyncio.gather(
        *[
            asyncio.to_thread(enrich_article_with_crawler, article)
            for article in new_articles
        ]
    )
    return fold_similar_titles(enriched_articles)


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

        source_domain_id = article.get("source_domain_id") or article.get("domain_id", "")
        classification = await classify_article_domain(
            {**article, "source_domain_id": source_domain_id}
        )
        classified_domain_id = classification["domain_id"]

        row = {
            "domain_id": classified_domain_id,
            "source_domain_id": source_domain_id,
            "classification_reason": classification.get("reason", ""),
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
            existing_article_id = str(article.get("existing_article_id") or "")
            if existing_article_id:
                _update_article_row(supabase, existing_article_id, row)
                article_id = existing_article_id
            else:
                result = _insert_article_row(supabase, row)
                article_id = _inserted_article_id(result)
            await asyncio.to_thread(_store_images_for_article, supabase, article_id, article)
            inserted += 1
        except Exception as exc:
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
        raw_articles = await scrape_source(source)
        raw_articles = [
            article
            for article in raw_articles
            if is_valid_article_candidate(article, source.domain_id)
        ][:_source_article_limit()]

        # 列表页只提供候选链接，详情页会在后续步骤补齐正文、图片和发布时间。
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
                    "published_at": a.get("published_at") or _fallback_published_at(now),
                    "image_urls": a.get("image_urls", []),
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

    semaphore = asyncio.Semaphore(_source_fetch_concurrency())
    timeout_seconds = _source_fetch_timeout_seconds()

    async def fetch_with_limit(source: SourceConfig) -> dict[str, Any]:
        """带并发限制和超时保护地抓取单个来源。"""
        async with semaphore:
            try:
                return await asyncio.wait_for(
                    fetch_source(source.name),
                    timeout=timeout_seconds,
                )
            except TimeoutError:
                status = {
                    "source": source.name,
                    "domain_id": source.domain_id,
                    "tier": source.tier,
                    "source_type": source.source_type,
                    "status": "error",
                    "articles_fetched": 0,
                    "articles_inserted": 0,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "error": f"Source fetch timed out after {timeout_seconds:.0f}s",
                }
                _fetch_status[source.name] = status
                return status

    results = await asyncio.gather(*[fetch_with_limit(source) for source in sources])

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
