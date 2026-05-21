from app.schemas.article import ArticleDetail
from app.schemas.digest import DigestGroup, DigestItem, DigestRequest, DigestResponse
from app.schemas.domain import Domain
from app.schemas.explore import ExploreCard, ExploreRequest, ExploreResponse
from app.domain_catalog import (
    DOMAIN_DEFINITIONS,
    DOMAIN_NAMES,
    EDGE_MAP,
    SAFE_FALLBACK_DOMAINS,
    DomainId,
)

DOMAINS = [Domain(**definition) for definition in DOMAIN_DEFINITIONS]


def list_domains() -> list[Domain]:
    return DOMAINS


def build_digest_items(domain_id: DomainId) -> list[DigestItem]:
    domain_name = DOMAIN_NAMES[domain_id]
    return [
        DigestItem(
            id=f"{domain_id}-{index}",
            domain_id=domain_id,
            title=f"{domain_name} 今日第 {index} 条重要资讯核心速报",
            summary=f"{domain_name} 今日要点 {index}：用于联调的结论卡摘要，控制在 100 字以内。",
            source="Mock Source",
            published_at="2026-05-19T08:00:00+08:00",
        )
        for index in range(1, 11)
    ]


def get_today_digest(payload: DigestRequest) -> DigestResponse:
    groups = [
        DigestGroup(domain_id=domain_id, items=build_digest_items(domain_id))
        for domain_id in payload.selected_domains
    ]
    return DigestResponse(groups=groups)


def get_article_detail(item_id: str) -> ArticleDetail:
    return ArticleDetail(
        id=item_id,
        title="Mock 详情",
        summary="结论卡回顾",
        content="正文内容联调用。",
        source_url="https://example.com/article",
        fetch_status="success",
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
