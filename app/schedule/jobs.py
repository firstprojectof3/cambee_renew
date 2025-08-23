# app/schedule/jobs.py
from __future__ import annotations
from datetime import datetime
from typing import List, Dict
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import CRAWL_SEEDS, CRAWL_INTERVAL_MIN, TIMEZONE
from app.database import SessionLocal
from app.services.crawl_pipeline import crawl_and_store

_scheduler: AsyncIOScheduler | None = None
_last_results: List[Dict] = []
_last_run_at: datetime | None = None
_tz = pytz.timezone(TIMEZONE)

async def _job():
    global _last_results, _last_run_at
    _last_results = []
    _last_run_at = datetime.now(_tz)

    for url in CRAWL_SEEDS:
        db = SessionLocal()
        try:
            result = crawl_and_store(db, url, limit=50)
            _last_results.append({"url": url, **result})
        except Exception as e:
            _last_results.append({"url": url, "error": str(e)})
        finally:
            db.close()

def start_scheduler():
    """앱 시작 시 스케줄러 실행"""
    global _scheduler
    if _scheduler and _scheduler.running:
        return _scheduler

    _scheduler = AsyncIOScheduler(timezone=_tz)
    trigger = IntervalTrigger(minutes=CRAWL_INTERVAL_MIN, timezone=_tz)
    _scheduler.add_job(_job, trigger, id="crawl_job", replace_existing=True)
    _scheduler.start()
    return _scheduler

def shutdown_scheduler():
    """앱 종료 시 스케줄러 중단"""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)

def get_status():
    """상태 확인용 (라우터에서 호출)"""
    next_run = None
    if _scheduler:
        jobs = _scheduler.get_jobs()
        if jobs:
            next_run = jobs[0].next_run_time
            if next_run and next_run.tzinfo is None:
                next_run = _tz.localize(next_run)

    return {
        "seeds": CRAWL_SEEDS,
        "interval_min": CRAWL_INTERVAL_MIN,
        "last_run_at": _last_run_at.isoformat() if _last_run_at else None,
        "next_run_at": next_run.isoformat() if next_run else None,
        "last_results": _last_results,
        "timezone": TIMEZONE,
        "running": bool(_scheduler and _scheduler.running),
    }
