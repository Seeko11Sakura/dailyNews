"""文章封面补齐：为已经入库但没有封面的文章重新抓取并保存图片。"""

from __future__ import annotations

from datetime import date
from typing import Any

from app.repositories.base import get_supabase
from app.services.article_crawler import crawl_article
from app.services.image_storage import store_article_images


def _query_articles_without_cover(
    supabase: Any,
    *,
    domain_id: str | None,
    published_date: str | None,
    limit: int,
) -> list[dict[str, Any]]:
    """查询缺少封面、但有原文地址的文章。"""
    query = (
        supabase.table("articles")
        .select("id, domain_id, title, source_url, content, cover_image_url")
        .is_("cover_image_url", "null")
        .order("published_at", desc=True)
        .limit(limit)
    )
    if domain_id:
        query = query.eq("domain_id", domain_id)
    if published_date:
        start = f"{published_date}T00:00:00+08:00"
        end = f"{published_date}T23:59:59+08:00"
        query = query.gte("published_at", start).lte("published_at", end)
    result = query.execute()
    return list(result.data or [])


def _backfill_one_article(supabase: Any, article: dict[str, Any]) -> bool:
    """为单篇文章补抓图片，并把第一张图写成封面。"""
    article_id = str(article.get("id") or "")
    source_url = str(article.get("source_url") or "")
    if not article_id or not source_url:
        return False

    preview = crawl_article(source_url)
    image_urls = preview.get("image_urls") or []
    if not isinstance(image_urls, list) or not image_urls:
        return False

    records = store_article_images(article_id, image_urls, supabase=supabase)
    if not records:
        return False

    cover_url = records[0].get("public_url")
    if not cover_url:
        return False

    update_data: dict[str, Any] = {"cover_image_url": cover_url}
    crawled_content = str(preview.get("content") or "")
    current_content = str(article.get("content") or "")
    if len(crawled_content) > len(current_content):
        update_data["content"] = crawled_content

    supabase.table("articles").update(update_data).eq("id", article_id).execute()
    return True


def backfill_article_images(
    *,
    domain_id: str | None = None,
    published_date: str | None = None,
    limit: int = 20,
) -> dict[str, Any]:
    """批量补齐文章封面图。"""
    safe_limit = max(1, min(limit, 50))
    safe_date = published_date or date.today().isoformat()
    supabase = get_supabase()
    articles = _query_articles_without_cover(
        supabase,
        domain_id=domain_id,
        published_date=safe_date,
        limit=safe_limit,
    )

    updated = 0
    failed = 0
    for article in articles:
        try:
            if _backfill_one_article(supabase, article):
                updated += 1
            else:
                failed += 1
        except Exception:
            failed += 1

    return {
        "matched": len(articles),
        "updated": updated,
        "failed": failed,
        "date": safe_date,
        "domain_id": domain_id,
    }
