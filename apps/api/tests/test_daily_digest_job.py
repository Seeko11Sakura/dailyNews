"""测试每日简报任务会抓文章并补齐封面。"""

import asyncio

from app.services import daily_digest_job


def test_run_daily_digest_generation_runs_image_backfill(monkeypatch):
    calls: dict[str, object] = {}

    async def fake_fetch_all_sources(*, tier=None):
        calls["tier"] = tier
        return {"total_articles_inserted": 3}

    def fake_backfill_article_images(**kwargs):
        calls["backfill"] = kwargs
        return {"matched": 3, "updated": 2, "failed": 1}

    monkeypatch.setenv("DAILY_DIGEST_TIER", "A")
    monkeypatch.setenv("DAILY_IMAGE_BACKFILL_LIMIT", "7")
    monkeypatch.setattr(daily_digest_job, "fetch_all_sources", fake_fetch_all_sources)
    monkeypatch.setattr(
        daily_digest_job,
        "backfill_article_images",
        fake_backfill_article_images,
    )

    result = asyncio.run(daily_digest_job.run_daily_digest_generation())

    assert calls["tier"] == "A"
    assert calls["backfill"]["limit"] == 7
    assert result["result"]["fetch"]["total_articles_inserted"] == 3
    assert result["result"]["image_backfill"]["updated"] == 2


def test_run_daily_digest_generation_can_skip_image_backfill(monkeypatch):
    async def fake_fetch_all_sources(*, tier=None):
        return {"total_articles_inserted": 1}

    monkeypatch.setenv("DAILY_IMAGE_BACKFILL_LIMIT", "0")
    monkeypatch.setattr(daily_digest_job, "fetch_all_sources", fake_fetch_all_sources)

    result = asyncio.run(daily_digest_job.run_daily_digest_generation())

    assert result["result"]["image_backfill"]["skipped"] is True
