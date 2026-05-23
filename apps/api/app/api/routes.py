from fastapi import APIRouter

from app.schemas.article import ArticleDetail
from app.schemas.digest import DigestRequest, DigestResponse
from app.schemas.domain import Domain
from app.schemas.explore import ExploreRequest, ExploreResponse
from app.services.mock_repository import (
    get_article_detail,
    get_today_digest,
    list_domains,
)
from app.services.explore_service import get_explore_cards as get_explore_cards_real

router = APIRouter()


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
