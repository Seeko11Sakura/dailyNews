import asyncio

from app.services.article_classifier import (
    build_classification_prompt,
    classify_article_domain,
    parse_classification_domain,
)


def test_parse_classification_domain_reads_json_result():
    result = parse_classification_domain('{"domain_id":"gadgets","reason":"手机新品"}')

    assert result == "gadgets"


def test_parse_classification_domain_rejects_unknown_domain():
    result = parse_classification_domain('{"domain_id":"unknown","reason":"未知"}')

    assert result is None


def test_parse_classification_domain_reads_chinese_domain_name():
    result = parse_classification_domain('{"domain_id":"商业与公司","reason":"公司经营"}')

    assert result == "business"


def test_build_classification_prompt_contains_all_domains():
    prompt = build_classification_prompt(
        {
            "title": "新款手机发布",
            "summary": "手机新品配置曝光",
            "content": "这是手机数码领域的文章",
            "source_domain_id": "technology",
        }
    )

    assert "gadgets=手机数码" in prompt
    assert "technology=科技与互联网" in prompt


def test_classify_article_domain_uses_keyword_route_without_api_key(monkeypatch):
    monkeypatch.delenv("AI_API_KEY", raising=False)

    result = asyncio.run(
        classify_article_domain(
            {
                "title": "新款手机发布",
                "summary": "手机新品配置曝光",
                "domain_id": "technology",
            }
        )
    )

    assert result["domain_id"] == "gadgets"
    assert result["reason"] == "关键词规则分类"


def test_classify_article_domain_prefers_strong_source_domain_keyword(monkeypatch):
    monkeypatch.setenv("AI_API_KEY", "test-key")

    result = asyncio.run(
        classify_article_domain(
            {
                "title": "本月玩什么：多款主机游戏发售",
                "summary": "玩家关注的新游戏阵容。",
                "content": "",
                "source_domain_id": "games",
            }
        )
    )

    assert result["domain_id"] == "games"


def test_classify_article_domain_keeps_business_source_when_keyword_matches(monkeypatch):
    monkeypatch.setenv("AI_API_KEY", "test-key")

    result = asyncio.run(
        classify_article_domain(
            {
                "title": "小赢科技发布一季度财报",
                "summary": "公司营收保持增长。",
                "content": "",
                "source_domain_id": "business",
            }
        )
    )

    assert result["domain_id"] == "business"


def test_classify_article_domain_routes_finance_keyword_before_ai(monkeypatch):
    monkeypatch.setenv("AI_API_KEY", "test-key")

    result = asyncio.run(
        classify_article_domain(
            {
                "title": "全球资本看好中国金融开放红利",
                "summary": "银行与证券市场保持活跃。",
                "content": "",
                "source_domain_id": "society",
            }
        )
    )

    assert result["domain_id"] == "finance"


def test_classify_article_domain_routes_ai_before_business_words(monkeypatch):
    monkeypatch.setenv("AI_API_KEY", "test-key")

    result = asyncio.run(
        classify_article_domain(
            {
                "title": "机器人原生世界动作模型问世，复旦系团队出品",
                "summary": "新模型用于机器人动作生成。",
                "content": "",
                "source_domain_id": "ai",
            }
        )
    )

    assert result["domain_id"] == "ai"
