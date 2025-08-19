# app/main.py (또는 네가 서버 올리는 엔트리 파일)

from fastapi import FastAPI
from app.routers import chat, user
from app.routers import notice, feedback, preference

# ⬇⬇⬇ [추가] CORS 미들웨어
from fastapi.middleware.cors import CORSMiddleware

# DB 관련 import
from app.database import engine, get_db
from cambee.app.models.models import Base

# AI 경로 
from fastapi import HTTPException
import os
from dotenv import load_dotenv

import openai

# AI 경로 (수정 필요)

from app.services.ai.prompt.prompt_builder import build_generic_prompt
from app.db.userdb import get_user_by_id
from app.services.ai.ai_setting import call_openai,client

from app.models.chat import ChatResponse, ChatResponseItem, ChatRequest
import json

# AI 경로 (수정 필요)

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
    
openai.api_key=os.getenv("OPENAI_API_KEY")

@app.get("/")
def read_root():
    return {"message": "AI 서버가 정상적으로 작동 중입니다."}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    user = get_user_by_id(req.user_id)
    prompt = build_generic_prompt(user, req.message)

    response = call_openai(client, [
        {"role": "system", "content":prompt},
        {"role": "user", "content": "다음 형식의 JSON으로만 응답해 주세요: {\"results\": [{\"title\": \"\", \"link\": \"\", \"summary\": \"\"}]} 외의 텍스트는 포함하지 마세요."}
    ])
    # print("GPT 응답:", response.choices[0].message.content)


    if not response or not response.choices:
        # fallback 
        return ChatResponse(
            results=[
                ChatResponseItem(
                    title="응답 실패",
                    link="",
                    summary="AI 응답을 가져오지 못했습니다. 다시 시도해 주세요."
                )
            ],
            timestamp=datetime.now().isoformat()
        )


    # GPT 응답 파싱 시도
    try:
        parsed_json = json.loads(response.choices[0].message.content)

    # link 필드가 있는 항목만 필터링 (학교 url)
        items = []
        for item in parsed_json.get("results", []):
            if "link" in item and item["link"].startswith("https://"):
                items.append(ChatResponseItem(**item))

        return ChatResponse(
            results=items,
            timestamp=datetime.now().isoformat()
    )
    except Exception:
        return ChatResponse(
            results=[
            ChatResponseItem(
                title="형식 오류",
                link="",
                summary="AI 응답 형식을 이해하지 못했습니다. 프롬프트를 조정해 주세요."
            )
        ],
        timestamp=datetime.now().isoformat()
    )



