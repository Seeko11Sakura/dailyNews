from datetime import datetime, timedelta

from app.domain_catalog import (
    DOMAIN_NAMES,
    EDGE_MAP,
    SAFE_FALLBACK_DOMAINS,
    DomainId,
)
from app.schemas.explore import ExploreCard, ExploreRequest, ExploreResponse


def get_explore_cards(payload: ExploreRequest) -> ExploreResponse:
    """Get 3 explore cards with 7-day dedup and dismissal downweighting."""
    excluded = set(payload.selected_domains) | set(payload.seen_domain_ids)
    dismissed = set(payload.dismissed_domains)

    cards: list[ExploreCard] = []

    # Priority 1: Adjacent domains (not dismissed)
    for source_domain_id in payload.selected_domains:
        for candidate_id in EDGE_MAP.get(source_domain_id, []):
            if candidate_id in excluded or candidate_id in dismissed:
                continue
            if _contains_card(cards, candidate_id):
                continue

            cards.append(
                _build_explore_card(
                    candidate_id=candidate_id,
                    source_domain_id=source_domain_id,
                    is_dismissed=False,
                )
            )
            if len(cards) == 3:
                return ExploreResponse(cards=cards)

    # Priority 2: Adjacent domains (dismissed, lower priority)
    for source_domain_id in payload.selected_domains:
        for candidate_id in EDGE_MAP.get(source_domain_id, []):
            if candidate_id in excluded:
                continue
            if candidate_id not in dismissed:
                continue
            if _contains_card(cards, candidate_id):
                continue

            cards.append(
                _build_explore_card(
                    candidate_id=candidate_id,
                    source_domain_id=source_domain_id,
                    is_dismissed=True,
                )
            )
            if len(cards) == 3:
                return ExploreResponse(cards=cards)

    # Priority 3: Safe fallback domains
    for fallback_id in SAFE_FALLBACK_DOMAINS:
        if fallback_id in excluded or fallback_id in dismissed:
            continue
        if _contains_card(cards, fallback_id):
            continue

        cards.append(
            _build_explore_card(
                candidate_id=fallback_id,
                source_domain_id=payload.selected_domains[0],
                is_dismissed=False,
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
    is_dismissed: bool,
) -> ExploreCard:
    candidate_name = DOMAIN_NAMES[candidate_id]
    source_name = DOMAIN_NAMES[source_domain_id]

    if is_dismissed:
        reason = f"基于你关注的{source_name}（曾标记不感兴趣）"
    else:
        reason = f"因为你关注了{source_name}"

    return ExploreCard(
        domain_id=candidate_id,
        domain_name=candidate_name,
        reason=reason,
        preview_titles=[
            f"{candidate_name} 今日值得关注的新变化",
            f"{candidate_name} 代表性趋势速览",
            f"{candidate_name} 与{source_name}的交叉观察",
        ],
    )
