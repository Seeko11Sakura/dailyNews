from app.domain_catalog import DOMAIN_DEFINITIONS
from app.services.source_config import SOURCES_BY_DOMAIN, get_active_sources


def test_every_user_domain_has_at_least_one_source():
    domain_ids = {definition["id"] for definition in DOMAIN_DEFINITIONS}

    missing = sorted(domain_ids - set(SOURCES_BY_DOMAIN))

    assert missing == []


def test_every_user_domain_has_active_sources():
    domain_ids = {definition["id"] for definition in DOMAIN_DEFINITIONS}

    inactive = [
        domain_id
        for domain_id in domain_ids
        if not any(source.active for source in SOURCES_BY_DOMAIN.get(domain_id, []))
    ]

    assert inactive == []


def test_active_sources_are_web_only_and_include_first_batch():
    sources = get_active_sources()
    active_names = {source.name for source in sources}

    assert all(source.source_type == "web" for source in sources)
    assert {
        "IT之家",
        "InfoQ 中文",
        "机器之心",
        "量子位",
        "中关村在线",
        "36氪",
        "财新（财经）",
        "机核",
    }.issubset(active_names)
