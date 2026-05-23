from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.schemas.article import ArticleDetail
from app.schemas.digest import DigestRequest, DigestResponse
from app.schemas.domain import Domain
from app.schemas.explore import ExploreRequest, ExploreResponse
from app.services.content_pipeline import (
    fetch_all_sources,
    fetch_source,
    get_fetch_status,
    get_fetch_status_for_source,
)
from app.services.mock_repository import (
    get_article_detail,
    get_today_digest,
    list_domains,
)
from app.services.explore_service import get_explore_cards as get_explore_cards_real
from app.services.source_config import get_active_sources

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
