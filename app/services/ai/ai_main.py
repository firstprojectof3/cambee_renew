
# FAST API AI
# 설치: pip install fastapi uvicorn python-dotenv openai
# 실행 : uvicorn main:app --reload
# app/ai.py
from datetime import datetime
import json, os
from dotenv import load_dotenv
import openai

from app.services.ai.prompt.prompt_builder import build_generic_prompt
from app.services.test.insert_dummy_data import get_user_by_id
from app.services.ai.ai_setting import call_openai, client
from app.schemas import ChatResponse, ChatResponseItem, ChatRequest

from fastapi import APIRouter

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    user = get_user_by_id(req.user_id)
    prompt = build_generic_prompt(user, req.message)

    response = call_openai(client, [
        {"role": "system", "content": prompt},
        {"role": "user", "content": "다음 형식의 JSON으로만 응답해 주세요: {\"results\": [{\"title\": \"\", \"link\": \"\", \"summary\": \"\"}]}"}
    ])

    if not response or not response.choices:
        return ChatResponse(
            results=[ChatResponseItem(title="응답 실패", link="", summary="AI 응답을 가져오지 못했습니다.")],
            timestamp=datetime.now().isoformat()
        )

    try:
        parsed_json = json.loads(response.choices[0].message.content)
        items = [
            ChatResponseItem(**item)
            for item in parsed_json.get("results", [])
            if "link" in item and item["link"].startswith("https://")
        ]
        return ChatResponse(results=items, timestamp=datetime.now().isoformat())
    except Exception:
        return ChatResponse(
            results=[ChatResponseItem(title="형식 오류", link="", summary="AI 응답 형식을 이해하지 못했습니다.")],
            timestamp=datetime.now().isoformat()
        )
