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




# --- FastAPI 앱 ---
app = FastAPI(title="Cambee API", version="0.1.0")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://effective-chainsaw-97wv5xvxppqw27xpq-4040.app.github.dev"],  # 배포 시 제한 권장
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 라우터 등록 ---
app.include_router(chat.router, prefix="/api")
app.include_router(user.router, prefix="/api")
app.include_router(preference.router, prefix="/api")
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
            "prompt_id": "pmpt_xxx",
            "prompt_version": "latest",
            "model_general": "gpt-4o-mini",
            "model_expert": "gpt-4o"
            }