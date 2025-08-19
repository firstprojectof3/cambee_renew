# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 프로젝트 라우터: 실제 비즈니스 로직은 각 라우터/서비스로 분리
from app.routers import chat, user, notice, feedback, preference

# (선택) health 라우터가 있으면 함께 포함
try:
    from app.routers.health import router as health_router
except Exception:
    health_router = None

app = FastAPI(title="Cambee API", version="0.1.0")

# CORS: 개발 단계에서는 넓게 허용 (배포 시 도메인/IP로 제한)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # TODO: 배포 시 실제 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 마운트
# chat 라우터 내부 경로가 "/api/chat"이라면 prefix="" 유지
# 만약 chat 라우터가 "/chat"이라면 아래 줄을 prefix="/api"로 바꿔줘.
app.include_router(chat.router, prefix="/api")            # /api/chat으로 노출됨
app.include_router(user.router, prefix="/api")
app.include_router(notice.router, prefix="/api")
app.include_router(feedback.router, prefix="/api")
app.include_router(preference.router, prefix="/api")

if health_router:
    app.include_router(health_router, prefix="")      # /health

# 헬스체크(프론트 연결 확인용)
@app.get("/ping")
def ping():
    return {"status": "ok"}

# 루트 핑
@app.get("/")
def root():
    return {"message": "AI 서버가 정상적으로 작동 중입니다.", "service": "cambee", "version": "0.1.0"}

# 실행 명령:
# uvicorn app.main:app --reload
