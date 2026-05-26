from app.repositories.base import get_supabase
from app.schemas.article import ArticleDetail
from app.schemas.digest import DigestGroup, DigestItem, DigestRequest, DigestResponse
from app.schemas.domain import Domain
from app.services.ai_overview import compact_text
from app.schemas.explore import ExploreCard, ExploreRequest, ExploreResponse
from app.domain_catalog import (
    DOMAIN_DEFINITIONS,
    DOMAIN_NAMES,
    EDGE_MAP,
    SAFE_FALLBACK_DOMAINS,
    DomainId,
)

DOMAINS = [Domain(**definition) for definition in DOMAIN_DEFINITIONS]


def _is_missing_ai_overview_column(exc: Exception) -> bool:
    """判断 Supabase 是否还没有执行 ai_overview 字段迁移。"""
    message = str(exc)
    return "ai_overview" in message and "42703" in message


def list_domains() -> list[Domain]:
    return DOMAINS


def get_today_digest(payload: DigestRequest) -> DigestResponse:
    supabase = get_supabase()
    groups = []

    for domain_id in payload.selected_domains:
        query = (
            supabase.table("articles")
            .select("id, domain_id, title, summary, ai_overview, source_name, published_at")
            .eq("domain_id", domain_id)
            .order("published_at", desc=True)
            .limit(10)
        )
        try:
            result = query.execute()
        except Exception as exc:
            if not _is_missing_ai_overview_column(exc):
                raise
            result = (
                supabase.table("articles")
                .select("id, domain_id, title, summary, source_name, published_at")
                .eq("domain_id", domain_id)
                .order("published_at", desc=True)
                .limit(10)
                .execute()
            )

        items = [
            DigestItem(
                id=row["id"],
                domain_id=row["domain_id"],
                title=row["title"],
                summary=compact_text(row.get("ai_overview") or row["summary"] or "", 100),
                source=row["source_name"] or "",
                published_at=row["published_at"] or "",
            )
            for row in result.data
        ]
        groups.append(DigestGroup(domain_id=domain_id, items=items))

    return DigestResponse(groups=groups)


def get_article_detail(item_id: str) -> ArticleDetail:
    supabase = get_supabase()
    query = (
        supabase.table("articles")
        .select("id, title, summary, ai_overview, content, source_url, fetch_status")
        .eq("id", item_id)
    )
    try:
        result = query.execute()
    except Exception as exc:
        if not _is_missing_ai_overview_column(exc):
            raise
        result = (
            supabase.table("articles")
            .select("id, title, summary, content, source_url, fetch_status")
            .eq("id", item_id)
            .execute()
        )

    if not result.data:
        return ArticleDetail(
            id=item_id,
            title="未找到",
            summary="",
            content="",
            source_url="",
            fetch_status="not_found",
        )

    row = result.data[0]
    return ArticleDetail(
        id=row["id"],
        title=row["title"],
        summary=row.get("ai_overview") or row["summary"] or "",
        content=row["content"] or "",
        source_url=row["source_url"] or "",
        fetch_status=row["fetch_status"] or "success",
    )


def get_explore_cards(payload: ExploreRequest) -> ExploreResponse:
    excluded = set(payload.selected_domains) | set(payload.seen_domain_ids)
    cards: list[ExploreCard] = []

    for source_domain_id in payload.selected_domains:
        for candidate_id in EDGE_MAP[source_domain_id]:
            if candidate_id in excluded or _contains_card(cards, candidate_id):
                continue

            cards.append(
                _build_explore_card(
                    candidate_id=candidate_id,
                    source_domain_id=source_domain_id,
                )
            )
            if len(cards) == 3:
                return ExploreResponse(cards=cards)

    for fallback_id in SAFE_FALLBACK_DOMAINS:
        if fallback_id in excluded or _contains_card(cards, fallback_id):
            continue

        cards.append(
            _build_explore_card(
                candidate_id=fallback_id,
                source_domain_id=payload.selected_domains[0],
            )
        )
        if len(cards) == 3:
            break

    return ExploreResponse(cards=cards)


def _contains_card(cards: list[ExploreCard], domain_id: str) -> bool:
    return any(card.domain_id == domain_id for card in cards)


def _build_explore_card(
    candidate_id: DomainId,
    source_domain_id: DomainId,
) -> ExploreCard:
    candidate_name = DOMAIN_NAMES[candidate_id]
    source_name = DOMAIN_NAMES[source_domain_id]
    return ExploreCard(
        domain_id=candidate_id,
        domain_name=candidate_name,
        reason=f"因为你关注了{source_name}",
        preview_titles=[
            f"{candidate_name} 今日值得关注的新变化",
            f"{candidate_name} 代表性趋势速览",
            f"{candidate_name} 与{source_name}的交叉观察",
        ],
    )
