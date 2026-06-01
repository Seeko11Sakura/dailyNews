"""后端接口入口，连接今日简报、抓取、图片和来源试跑服务。"""

from typing import Any

import asyncio
import httpx
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.schemas.article import ArticleDetail
from app.schemas.crawler import ArticleCrawlRequest, ArticleCrawlResponse
from app.schemas.digest import DigestRequest, DigestResponse
from app.schemas.domain import Domain
from app.schemas.explore import ExploreRequest, ExploreResponse
from app.services.content_pipeline import (
    fetch_all_sources,
    fetch_source,
    get_fetch_status,
    get_fetch_status_for_source,
)
from app.services.ai_overview import backfill_missing_ai_overviews
from app.services.article_crawler import crawl_article
from app.services.article_image_backfill import backfill_article_images
from app.services.daily_digest_job import (
    get_daily_digest_status,
    start_manual_digest_generation,
)
from app.services.mock_repository import (
    get_article_detail,
    get_today_digest,
    list_domains,
)
from app.services.explore_service import get_explore_cards as get_explore_cards_real
from app.services.source_config import SourceConfig, get_active_sources
from app.services.web_scraper import scrape_source

router = APIRouter()


# ---------------------------------------------------------------------------
# Existing endpoints
# ---------------------------------------------------------------------------


@router.get("/domains", response_model=list[Domain])
def get_domains() -> list[Domain]:
    return list_domains()


@router.post("/digest/today", response_model=DigestResponse)
def get_digest(payload: DigestRequest) -> DigestResponse:
    return get_today_digest(payload)


@router.get("/items/{item_id}", response_model=ArticleDetail)
def get_item(item_id: str) -> ArticleDetail:
    return get_article_detail(item_id)


@router.post("/crawl/article", response_model=ArticleCrawlResponse)
def crawl_article_preview(payload: ArticleCrawlRequest) -> ArticleCrawlResponse:
    """抓取单篇文章的标题、正文和图片地址，用于验证爬虫效果。"""
    try:
        result = crawl_article(payload.url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"文章抓取失败：{exc}") from exc

    return ArticleCrawlResponse(**result)


@router.post("/explore/draw", response_model=ExploreResponse)
def draw_explore_cards(payload: ExploreRequest) -> ExploreResponse:
    return get_explore_cards_real(payload)


@router.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Fetch endpoints (Task 2A)
# ---------------------------------------------------------------------------


class FetchTriggerRequest(BaseModel):
    """Request body for POST /fetch/trigger."""

    source_name: str | None = None  # None = fetch all sources
    domain_id: str | None = None  # Filter by domain (only when source_name is None)
    tier: str | None = None  # Filter by tier (only when source_name is None)


class OverviewBackfillRequest(BaseModel):
    """Request body for POST /overview/backfill."""

    domain_id: str | None = None
    limit: int = 20
    force: bool = False


class ImageBackfillRequest(BaseModel):
    """POST /images/backfill 的请求参数。"""

    domain_id: str | None = None
    date: str | None = None
    limit: int = 20


class SourceTrialRequest(BaseModel):
    """POST /sources/trial 的请求参数。"""

    url: str
    name: str = "临时来源"
    domain_id: str = "technology"
    tier: str = "C"
    limit: int = 5
    css_selectors: dict[str, str] | None = None


@router.post("/fetch/trigger")
async def trigger_fetch(payload: FetchTriggerRequest | None = None) -> dict[str, Any]:
    """Trigger a manual fetch.

    - No body / empty body: fetch all active sources.
    - source_name set: fetch that single source.
    - domain_id / tier set (without source_name): filter all sources by domain/tier.
    """
    if payload is None:
        payload = FetchTriggerRequest()

    if payload.source_name:
        result = await fetch_source(payload.source_name)
        return result

    result = await fetch_all_sources(
        domain_id=payload.domain_id,
        tier=payload.tier,
    )
    return result


@router.get("/fetch/status")
async def fetch_status(
    source_name: str | None = Query(None, description="Filter by source name"),
) -> dict[str, Any]:
    """Check the last fetch status per source.

    - No query param: returns status for all sources that have been fetched.
    - source_name set: returns status for that specific source.
    """
    if source_name:
        status = get_fetch_status_for_source(source_name)
        if status is None:
            return {"error": f"No fetch status for source: {source_name}"}
        return status

    all_status = get_fetch_status()

    # Also include sources that haven't been fetched yet.
    summary: dict[str, Any] = {
        "fetched_count": len(all_status),
        "total_active_sources": len(get_active_sources()),
        "sources": {},
    }

    for src in get_active_sources():
        if src.name in all_status:
            summary["sources"][src.name] = all_status[src.name]
        else:
            summary["sources"][src.name] = {
                "source": src.name,
                "domain_id": src.domain_id,
                "tier": src.tier,
                "source_type": src.source_type,
                "status": "not_fetched",
                "articles_fetched": 0,
                "articles_inserted": 0,
                "timestamp": None,
                "error": None,
            }

    return summary


@router.post("/digest/generate")
async def generate_today_digest() -> dict[str, Any]:
    """Manual trigger for today's scheduled digest generation."""
    return start_manual_digest_generation()


@router.get("/digest/job/status")
async def daily_digest_status() -> dict[str, Any]:
    """Return daily digest job status."""
    return get_daily_digest_status()


@router.get("/fetch/sources")
async def list_sources(
    domain_id: str | None = Query(None, description="Filter by domain"),
    tier: str | None = Query(None, description="Filter by tier"),
) -> list[dict[str, Any]]:
    """List all configured sources with their metadata."""
    sources = get_active_sources()
    if domain_id:
        sources = [s for s in sources if s.domain_id == domain_id]
    if tier:
        sources = [s for s in sources if s.tier == tier]

    return [
        {
            "name": s.name,
            "url": s.url,
            "domain_id": s.domain_id,
            "tier": s.tier,
            "source_type": s.source_type,
            "rss_url": s.rss_url,
            "active": s.active,
        }
        for s in sources
    ]


@router.post("/sources/trial")
async def trial_source(payload: SourceTrialRequest) -> dict[str, Any]:
    """试跑一个网页来源，返回候选文章和少量详情预览。"""
    source = SourceConfig(
        name=payload.name,
        url=payload.url,
        domain_id=payload.domain_id,
        tier=payload.tier,
        source_type="web",
        css_selectors=payload.css_selectors or {},
    )

    candidates = await scrape_source(source)
    limited_candidates = candidates[: max(1, payload.limit)]
    previews: list[dict[str, Any]] = []
    for candidate in limited_candidates[:3]:
        try:
            preview = await asyncio.to_thread(crawl_article, candidate["link"])
        except Exception as exc:
            previews.append(
                {
                    "url": candidate["link"],
                    "title": candidate.get("title", ""),
                    "ok": False,
                    "error": str(exc),
                }
            )
            continue

        previews.append(
            {
                "url": preview.get("url", candidate["link"]),
                "title": preview.get("title") or candidate.get("title", ""),
                "published_at": preview.get("published_at", ""),
                "content_length": preview.get("content_length", 0),
                "image_count": len(preview.get("image_urls") or []),
                "ok": True,
            }
        )

    return {
        "source": source.name,
        "url": source.url,
        "candidate_count": len(candidates),
        "candidates": limited_candidates,
        "previews": previews,
    }


@router.post("/overview/backfill")
async def backfill_overviews(payload: OverviewBackfillRequest) -> dict[str, Any]:
    """Backfill missing AI overviews for existing articles."""
    return await backfill_missing_ai_overviews(
        domain_id=payload.domain_id,
        limit=payload.limit,
        force=payload.force,
    )


@router.post("/images/backfill")
async def backfill_images(payload: ImageBackfillRequest) -> dict[str, Any]:
    """补齐缺失的文章封面图。"""
    return await asyncio.to_thread(
        backfill_article_images,
        domain_id=payload.domain_id,
        published_date=payload.date,
        limit=payload.limit,
    )
