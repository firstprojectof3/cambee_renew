# app/main.py
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import inspect
from contextlib import asynccontextmanager
from sqlalchemy import text
from app.core.config import SETTINGS

# --- DB 스키마 초기화(선택, Alembic 쓰면 제거 가능) ---
try:
    from app.database import Base, engine
    from app.models import models            # ✅ 기존 테이블 로드
    from app.models import auth_account 
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"[WARN] DB schema init skipped: {e}")

# --- 기본 라우터들 ---
import app.routers.chat as chat
import app.routers.user as user
import app.routers.preference as preference
import app.routers.auth as auth



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
app.include_router(preference.router, prefix="/api")
if ai_router:
    app.include_router(ai_router, prefix="/api")
app.include_router(auth.router, prefix="/api")



# --- 헬스체크 & 기본 엔드포인트 ---
@app.get("/")
def root():
    return {"message": "Cambee API is running 🚀"}

@app.get("/health")
def health():
    return {
            "status": "ok",
            "ai_ready": true,
            "db_ready": true,
            "prompt_id": "prmpt_xxx",
            "prompt_version": "latest",
            "model_general": "gpt-4o-mini",
            "model_expert": "gpt-4o"
            }