"""每日简报任务：每天 8 点抓取当天资讯并生成 AI 概览。"""

from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime, time, timedelta, timezone
from typing import Any

from app.services.content_pipeline import fetch_all_sources
from app.services.article_image_backfill import backfill_article_images

logger = logging.getLogger(__name__)

LOCAL_TZ = timezone(timedelta(hours=8))
DEFAULT_RUN_HOUR = 8

_task: asyncio.Task | None = None
_manual_task: asyncio.Task | None = None
_last_run: dict[str, Any] | None = None
_current_run: dict[str, Any] | None = None


def _daily_tier_filter() -> str | None:
    """读取每日自动抓取的来源层级，默认覆盖全部来源。"""
    value = os.getenv("DAILY_DIGEST_TIER", "").strip()
    return value or None


def _daily_image_backfill_limit() -> int:
    """读取每日补抓封面图数量。"""
    raw_value = os.getenv("DAILY_IMAGE_BACKFILL_LIMIT", "30")
    try:
        return max(0, int(raw_value))
    except ValueError:
        return 30


async def _run_daily_image_backfill(published_date: str) -> dict[str, Any]:
    """每日抓取结束后补齐当天文章封面。"""
    limit = _daily_image_backfill_limit()
    if limit <= 0:
        return {"matched": 0, "updated": 0, "failed": 0, "skipped": True}

    try:
        return await asyncio.to_thread(
            backfill_article_images,
            published_date=published_date,
            limit=limit,
        )
    except Exception as exc:
        logger.warning("Daily image backfill failed: %s", exc)
        return {"matched": 0, "updated": 0, "failed": 0, "error": str(exc)}


def next_daily_run(
    now: datetime | None = None,
    hour: int = DEFAULT_RUN_HOUR,
) -> datetime:
    """计算下一次每日抓取时间。"""
    current = now.astimezone(LOCAL_TZ) if now else datetime.now(LOCAL_TZ)
    target = datetime.combine(current.date(), time(hour=hour), tzinfo=LOCAL_TZ)
    if current >= target:
        target += timedelta(days=1)
    return target


async def run_daily_digest_generation() -> dict[str, Any]:
    """执行每日抓取和 AI 概览生成。"""
    global _current_run, _last_run
    started_at = datetime.now(LOCAL_TZ).isoformat()
    _current_run = {
        "started_at": started_at,
        "status": "running",
        "finished_at": None,
        "result": None,
        "error": None,
    }
    try:
        run_date = datetime.now(LOCAL_TZ).date().isoformat()
        fetch_result = await fetch_all_sources(tier=_daily_tier_filter())
        image_backfill_result = await _run_daily_image_backfill(run_date)
        result = {
            "fetch": fetch_result,
            "image_backfill": image_backfill_result,
        }
        _last_run = {
            "started_at": started_at,
            "finished_at": datetime.now(LOCAL_TZ).isoformat(),
            "status": "success",
            "result": result,
            "error": None,
        }
        return _last_run
    except Exception as exc:
        _last_run = {
            "started_at": started_at,
            "finished_at": datetime.now(LOCAL_TZ).isoformat(),
            "status": "error",
            "result": None,
            "error": str(exc),
        }
        raise
    finally:
        _current_run = None


def start_manual_digest_generation() -> dict[str, Any]:
    """手动启动一次每日简报生成，接口立即返回。"""
    global _current_run, _manual_task
    if _current_run is not None:
        return {"status": "already_running", "current_run": _current_run}
    if _manual_task is not None and not _manual_task.done():
        return {"status": "already_running", "current_run": _current_run}

    _current_run = {
        "started_at": datetime.now(LOCAL_TZ).isoformat(),
        "status": "starting",
        "finished_at": None,
        "result": None,
        "error": None,
    }
    _manual_task = asyncio.create_task(run_daily_digest_generation())
    return {"status": "started", "current_run": _current_run}


async def _scheduler_loop() -> None:
    """后台循环，到每天 8 点执行一次每日简报任务。"""
    while True:
        run_at = next_daily_run()
        wait_seconds = max(0, (run_at - datetime.now(LOCAL_TZ)).total_seconds())
        logger.info("Next daily digest generation scheduled at %s", run_at.isoformat())
        await asyncio.sleep(wait_seconds)
        try:
            await run_daily_digest_generation()
        except Exception:
            logger.exception("Daily digest generation failed")


def start_daily_digest_scheduler() -> None:
    """启动每日简报后台任务。"""
    global _task
    if os.getenv("DISABLE_DAILY_DIGEST_SCHEDULER") == "1":
        return
    if _task is None or _task.done():
        _task = asyncio.create_task(_scheduler_loop())


async def stop_daily_digest_scheduler() -> None:
    """停止每日简报后台任务。"""
    global _task
    if _task is None:
        return
    _task.cancel()
    try:
        await _task
    except asyncio.CancelledError:
        pass
    _task = None


def get_daily_digest_status() -> dict[str, Any]:
    """查看每日简报任务状态。"""
    return {
        "next_run_at": next_daily_run().isoformat(),
        "current_run": _current_run,
        "last_run": _last_run,
    }
