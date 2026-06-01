from app.repositories.base import get_supabase
from app.schemas.article import ArticleDetail
from app.schemas.digest import DigestGroup, DigestItem, DigestRequest, DigestResponse
from app.schemas.domain import Domain
from app.services.article_content import fetch_article_content
from app.services.ai_overview import PENDING_OVERVIEW_TEXT, compact_text
from app.schemas.explore import ExploreCard, ExploreRequest, ExploreResponse
from app.domain_catalog import (
    DOMAIN_DEFINITIONS,
    DOMAIN_NAMES,
    EDGE_MAP,
    SAFE_FALLBACK_DOMAINS,
    DomainId,
)
from app.services.source_config import SOURCES_BY_DOMAIN
from datetime import datetime, time, timedelta, timezone

DOMAINS = [Domain(**definition) for definition in DOMAIN_DEFINITIONS]
LOCAL_TZ = timezone(timedelta(hours=8))


def _local_day_to_utc_range(date_value: str) -> tuple[str, str]:
    """把本地日期转换成 Supabase 使用的 UTC 时间范围。"""
    day = datetime.fromisoformat(date_value).date()
    start_local = datetime.combine(day, time.min, tzinfo=LOCAL_TZ)
    end_local = start_local + timedelta(days=1)
    return (
        start_local.astimezone(timezone.utc).isoformat(),
        end_local.astimezone(timezone.utc).isoformat(),
    )


def _resolve_digest_window(
    date_value: str,
    now: datetime | None = None,
) -> tuple[str | None, str]:
    """计算简报查询窗口，8 点前查今天 0 点前的上一期数据。"""
    current = now.astimezone(LOCAL_TZ) if now else datetime.now(LOCAL_TZ)
    requested_day = datetime.fromisoformat(date_value).date()

    if requested_day == current.date() and current.time() < time(hour=8):
        current_day_start = datetime.combine(requested_day, time.min, tzinfo=LOCAL_TZ)
        return None, current_day_start.astimezone(timezone.utc).isoformat()

    return _local_day_to_utc_range(date_value)


def _is_missing_ai_overview_column(exc: Exception) -> bool:
    """判断 Supabase 是否还没有执行 ai_overview 字段迁移。"""
    message = str(exc)
    return "ai_overview" in message and "42703" in message


def _is_missing_digest_optional_column(exc: Exception) -> bool:
    """判断 Supabase 是否还没有执行今日页需要的增强字段迁移。"""
    message = str(exc)
    return "42703" in message and (
        "ai_overview" in message or "cover_image_url" in message
    )


def _needs_full_content(content: str, summary: str) -> bool:
    """判断详情页是否需要从原文站补抓完整正文。"""
    if not content:
        return True
    if len(content) < 240:
        return True
    return content.strip() == summary.strip()


def list_domains() -> list[Domain]:
    return DOMAINS


def _candidate_content_domains(domain_id: str) -> list[str]:
    """只读取本领域内容，避免不同领域互相借文章。"""
    return [domain_id] if domain_id in SOURCES_BY_DOMAIN else []


def _query_digest_items(
    supabase,
    content_domain_id: str,
    start_at: str | None,
    end_at: str,
):
    """按文章发布时间查询某个领域的简报。"""
    query = (
        supabase.table("articles")
        .select(
            "id, domain_id, title, summary, ai_overview, source_name, "
            "published_at, cover_image_url"
        )
        .eq("domain_id", content_domain_id)
        .lt("published_at", end_at)
        .order("published_at", desc=True)
        .limit(10)
    )
    if start_at:
        query = query.gte("published_at", start_at)
    try:
        return query.execute()
    except Exception as exc:
        if not _is_missing_digest_optional_column(exc):
            raise
        fallback_query = (
            supabase.table("articles")
            .select("id, domain_id, title, summary, source_name, published_at")
            .eq("domain_id", content_domain_id)
            .lt("published_at", end_at)
            .order("published_at", desc=True)
            .limit(10)
        )
        if start_at:
            fallback_query = fallback_query.gte("published_at", start_at)
        return fallback_query.execute()


def get_today_digest(payload: DigestRequest) -> DigestResponse:
    supabase = get_supabase()
    groups = []
    start_at, end_at = _resolve_digest_window(payload.date)

    for domain_id in payload.selected_domains:
        result = None
        for content_domain_id in _candidate_content_domains(domain_id):
            result = _query_digest_items(
                supabase=supabase,
                content_domain_id=content_domain_id,
                start_at=start_at,
                end_at=end_at,
            )
            if result.data:
                break

        rows = result.data if result else []

        items = [
            DigestItem(
                id=row["id"],
                domain_id=row["domain_id"],
                title=row["title"],
                summary=compact_text(row.get("ai_overview") or PENDING_OVERVIEW_TEXT, 100),
                source=row["source_name"] or "",
                published_at=row["published_at"] or "",
                cover_image_url=row.get("cover_image_url"),
            )
            for row in rows
        ]
        groups.append(DigestGroup(domain_id=domain_id, items=items))

    return DigestResponse(groups=groups)


def get_article_detail(item_id: str) -> ArticleDetail:
    supabase = get_supabase()
    query = (
        supabase.table("articles")
        .select(
            "id, title, summary, ai_overview, content, source_url, "
            "cover_image_url, fetch_status"
        )
        .eq("id", item_id)
    )
    try:
        result = query.execute()
    except Exception as exc:
        if not _is_missing_digest_optional_column(exc):
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
        cover_image_url=None,
        fetch_status="not_found",
        )

    row = result.data[0]
    summary = row.get("ai_overview") or PENDING_OVERVIEW_TEXT
    content = row["content"] or ""
    if _needs_full_content(content, summary):
        fetched_content = fetch_article_content(row["source_url"] or "")
        if fetched_content and len(fetched_content) > len(content):
            content = fetched_content
            try:
                (
                    supabase.table("articles")
                    .update({"content": fetched_content})
                    .eq("id", row["id"])
                    .execute()
                )
            except Exception:
                pass

    return ArticleDetail(
        id=row["id"],
        title=row["title"],
        summary=summary,
        content=content,
        source_url=row["source_url"] or "",
        cover_image_url=row.get("cover_image_url"),
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
