# app/routers/chat.py
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas import ChatRequest, ChatResponse
from app.crud import get_user_by_id
from app.database import get_db
from app.services.llm import ask_with_prompt_id

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest, db: Session = Depends(get_db)):
    # 1) 유저 조회
    user = get_user_by_id(db, payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2) LLM 호출 (Prompt ID 기반)
    result = ask_with_prompt_id(
        user={
            "major": getattr(user, "major", None),
            "grade": getattr(user, "grade", None),
            "student_number": getattr(user, "student_number", None),
        },
        message=payload.message,
    )

    # 3) 스키마 맞춰 반환 (title, link, summary)
    return ChatResponse(
        title=result["title"],
        link=result["link"],
        summary=result["summary"],
    )

