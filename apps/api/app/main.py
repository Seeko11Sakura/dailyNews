from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.services.daily_digest_job import (
    start_daily_digest_scheduler,
    stop_daily_digest_scheduler,
)

app = FastAPI(title="dailyNews API")

# CORS middleware - allow frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.on_event("startup")
async def startup_daily_digest_scheduler() -> None:
    """服务启动后注册每日 8 点简报任务。"""
    start_daily_digest_scheduler()


@app.on_event("shutdown")
async def shutdown_daily_digest_scheduler() -> None:
    """服务关闭时停止每日简报任务。"""
    await stop_daily_digest_scheduler()
