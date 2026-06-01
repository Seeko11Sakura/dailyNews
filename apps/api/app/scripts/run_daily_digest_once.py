"""执行一次每日简报生成任务，供 Render Cron 在每天 8 点触发。"""

from __future__ import annotations

import asyncio
import json

from app.services.daily_digest_job import run_daily_digest_generation


def main() -> None:
    """运行一次抓取和 AI 概览生成，并输出结果。"""
    result = asyncio.run(run_daily_digest_generation())
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
