# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services.ai.ai_main import ai_main 
# 라우터 임포트
from app.routers import chat, user, notice, feedback, preference

# ai 라우터
from app.services.ai.ai_main import router as ai_router

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 추후 보안상 도메인 제한 권장
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(chat.router, prefix="/api")
app.include_router(user.router, prefix="/api")
app.include_router(notice.router, prefix="/api")
app.include_router(feedback.router, prefix="/api")
app.include_router(preference.router, prefix="/api")

# ✅ AI 라우터 등록
app.include_router(ai_router, prefix="/api")

# 기본 엔드포인트
@app.get("/")
async def root():
    return {"message": "Cambee API is running 🚀"}
