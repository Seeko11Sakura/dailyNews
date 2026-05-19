from app.schemas.article import ArticleDetail
from app.schemas.digest import DigestGroup, DigestItem, DigestRequest, DigestResponse
from app.schemas.domain import Domain

DOMAINS = [
    Domain(id="technology", name="科技与互联网", emoji="💻"),
    Domain(id="ai", name="人工智能", emoji="🤖"),
    Domain(id="gadgets", name="手机数码", emoji="📱"),
    Domain(id="business", name="商业与公司", emoji="💼"),
    Domain(id="finance", name="财经与宏观", emoji="📈"),
    Domain(id="career", name="职场与效率", emoji="🚀"),
    Domain(id="education", name="教育与学习", emoji="📚"),
    Domain(id="games", name="游戏", emoji="🎮"),
    Domain(id="media", name="影视与流媒体", emoji="🎬"),
    Domain(id="health", name="健康与心理", emoji="🧠"),
    Domain(id="society", name="社会与热点", emoji="🌍"),
    Domain(id="lifestyle", name="生活方式", emoji="☕"),
]


def list_domains() -> list[Domain]:
    return DOMAINS


def build_digest_items(domain_id: str) -> list[DigestItem]:
    return [
        DigestItem(
            id=f"{domain_id}-{index}",
            domain_id=domain_id,
            title=f"{domain_id} 今日第 {index} 条重要资讯",
            summary="结论卡：这是一条用于联调的 mock 摘要，保持 100 字以内。",
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
