from typing import Literal

DomainId = Literal[
    "technology",
    "ai",
    "gadgets",
    "business",
    "finance",
    "career",
    "education",
    "games",
    "media",
    "health",
    "society",
    "lifestyle",
]

DOMAIN_DEFINITIONS: list[dict[str, str]] = [
    {"id": "technology", "name": "科技与互联网", "emoji": "💻"},
    {"id": "ai", "name": "人工智能", "emoji": "🤖"},
    {"id": "gadgets", "name": "手机数码", "emoji": "📱"},
    {"id": "business", "name": "商业与公司", "emoji": "💼"},
    {"id": "finance", "name": "财经与宏观", "emoji": "📈"},
    {"id": "career", "name": "职场与效率", "emoji": "🚀"},
    {"id": "education", "name": "教育与学习", "emoji": "📚"},
    {"id": "games", "name": "游戏", "emoji": "🎮"},
    {"id": "media", "name": "影视与流媒体", "emoji": "🎬"},
    {"id": "health", "name": "健康与心理", "emoji": "🧠"},
    {"id": "society", "name": "社会与热点", "emoji": "🌍"},
    {"id": "lifestyle", "name": "生活方式", "emoji": "☕"},
]

DOMAIN_NAMES = {
    definition["id"]: definition["name"] for definition in DOMAIN_DEFINITIONS
}

EDGE_MAP: dict[str, list[str]] = {
    "technology": ["ai", "gadgets", "business", "career", "society"],
    "ai": ["technology", "business", "education", "career", "health"],
    "gadgets": ["technology", "ai", "games", "lifestyle", "business"],
    "business": ["technology", "ai", "finance", "career", "society"],
    "finance": ["business", "society", "lifestyle", "career", "technology"],
    "career": ["business", "education", "health", "technology", "lifestyle"],
    "education": ["career", "ai", "technology", "health", "lifestyle"],
    "games": ["gadgets", "technology", "media", "lifestyle", "ai"],
    "media": ["lifestyle", "games", "society", "technology", "health"],
    "health": ["lifestyle", "career", "education", "society", "ai"],
    "society": ["business", "finance", "media", "technology", "health"],
    "lifestyle": ["health", "gadgets", "media", "career", "finance"],
}

SAFE_FALLBACK_DOMAINS = ["lifestyle", "education", "health", "media", "finance"]
