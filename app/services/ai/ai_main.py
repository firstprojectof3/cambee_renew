
# FAST API AI
# 설치: pip install fastapi uvicorn python-dotenv openai
# 실행 : uvicorn main:app --reload
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException

from datetime import datetime

import os
from dotenv import load_dotenv

import openai

from app.services.ai.prompt.prompt_builder import build_generic_prompt
# from app.db.userdb import get_user_by_id
from app.services.test.insert_dummy_data import get_user_by_id

from app.services.ai.ai_setting import call_openai,client

# from app.models.chat import ChatResponse, ChatResponseItem, ChatRequest
from app.schemas import ChatResponse, ChatResponseItem, ChatRequest

import json

load_dotenv()

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# AI 파트 본격 시작

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

