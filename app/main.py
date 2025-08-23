# app/main.py
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import inspect

# --- DB 스키마 초기화(선택, Alembic 쓰면 제거 가능) ---
try:
    from app.database import Base, engine
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"[WARN] DB schema init skipped: {e}")

# --- 기본 라우터들 ---
from app.routers import chat, user, notice, feedback, preference

# 라우터 직접 import
from app.routers.crawl_debug import router as crawl_debug_router
from app.routers.crawl_admin import router as crawl_admin_router
from app.routers.schedule_status import router as schedule_status_router

# 스케줄러 start/stop
from app.schedule.jobs import start_scheduler, shutdown_scheduler


# --- AI 라우터(있으면 등록, 없으면 경고만) ---
ai_router = None
try:
    from app.services.ai.ai_main import router as _ai_router  # router 객체를 내보내는 경우
    ai_router = _ai_router
except Exception as e:
    print(f"[WARN] ai_router not available: {e}")

# --- ai_main(startup 작업) 함수 탐색: ai_main / main / run 중 존재하는 것 사용 ---
_ai_main_callable = None
try:
    ai_mod = __import__("app.services.ai.ai_main", fromlist=["*"])
    for _name in ("ai_main", "main", "run"):
        fn = getattr(ai_mod, _name, None)
        if callable(fn):
            _ai_main_callable = fn
            print(f"[INFO] Using startup function from ai_main: '{_name}'")
            break
except Exception as e:
    print(f"[WARN] ai_main module import skipped: {e}")

# --- FastAPI 앱 ---
app = FastAPI(title="Cambee API", version="0.1.0")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 배포 시 제한 권장
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 라우터 등록 ---
app.include_router(chat.router, prefix="/api")
app.include_router(user.router, prefix="/api")
app.include_router(notice.router, prefix="/api")
app.include_router(feedback.router, prefix="/api")
app.include_router(preference.router, prefix="/api")
app.include_router(crawl_debug_router,    prefix="/api")
app.include_router(crawl_admin_router,    prefix="/api")
app.include_router(schedule_status_router, prefix="/api")
if ai_router:
    app.include_router(ai_router, prefix="/api")

# --- 스타트업 훅: ai_main이 있으면 실행(동기/비동기 모두 지원) ---
@app.on_event("startup")
async def _startup_tasks():
    if _ai_main_callable:
        try:
            result = _ai_main_callable()
            if inspect.iscoroutine(result):
                await result
        except Exception as e:
            print(f"[WARN] ai_main startup failed: {e}")

# --- 헬스체크 & 기본 엔드포인트 ---
@app.get("/")
def root():
    return {"message": "Cambee API is running 🚀"}

@app.get("/health")
def health():
    return {"status": "ok"}

# --- 스케줄러 추가 ---
from app.schedule.jobs import start_scheduler, shutdown_scheduler

@app.on_event("startup")
async def _on_start():
    start_scheduler()  # 가드가 있어서 중복 호출되어도 안전

@app.on_event("shutdown")
async def _on_stop():
    shutdown_scheduler()