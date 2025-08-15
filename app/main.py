# app/main.py (또는 네가 서버 올리는 엔트리 파일)

from fastapi import FastAPI
from app.routers import chat, user
from app.routers import notice, feedback, preference

# ⬇⬇⬇ [추가] CORS 미들웨어
from fastapi.middleware.cors import CORSMiddleware

# DB 관련 import
from app.database import engine, get_db
from app.schema_models import Base

# DB 테이블 생성
Base.metadata.create_all(bind=engine)

# FastAPI 앱 생성
app = FastAPI()

# ⬇⬇⬇ [추가] 개발 단계: 전부 허용 (나중에 앱 도메인/IP로 좁히자)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # RN 개발 중 편하게 전체 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 연결 (네 코드 그대로)
app.include_router(chat.router, prefix="/api")
app.include_router(user.router, prefix="/api")
app.include_router(notice.router, prefix="/api")
app.include_router(feedback.router, prefix="/api")
app.include_router(preference.router, prefix="/api")

# ⬇⬇⬇ [추가] 헬스체크 엔드포인트: 프론트 연결 확인용
@app.get("/ping")
def ping():
    return {"status": "ok"}
