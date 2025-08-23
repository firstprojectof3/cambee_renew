# app/routers/chat.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from datetime import datetime
import re
from typing import Any, Dict, Optional, List

from app.schemas import ChatRequest, ChatResponse, ChatResponseItem
from app.database import get_db
from app.crud import (
    get_user_by_id,
    get_cached_answer,
    upsert_cache,
)
from app.models.models import ChatLog
from app.services.llm import gpt_answer

router = APIRouter()

# ---------------- 요청 정규화 ----------------
def normalize_chat_request(payload: Dict[str, Any]) -> Dict[str, str]:
    uid = (
        payload.get("user_id")
        or (payload.get("user") or {}).get("id")
        or payload.get("uid")
        or payload.get("id")
    )
    msg = (
        payload.get("message")
        or payload.get("text")
        or payload.get("q")
        or payload.get("query")
    )
    return {"user_id": str(uid or ""), "message": str(msg or "")}

# ---------------- LLM만 강제할지 / 캐시 우회할지 ----------------
def should_force_llm(payload: Dict[str, Any]) -> bool:
    # source: "llm" 이면 무조건 LLM
    src = (payload.get("source") or "").strip().lower()
    return src == "llm"

def should_skip_cache(payload: Dict[str, Any]) -> bool:
    # nocache: true 이면 캐시 조회/저장을 건너뜀
    v = payload.get("nocache")
    return bool(v) is True

# ---------------- 라우터 ----------------
@router.post("/chat", response_model=ChatResponse)
def chat_api(body: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    # 0) 요청 정규화 + 검증
    try:
        req = ChatRequest(**normalize_chat_request(body))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"잘못된 요청 바디: {e}")

    uid = req.user_id.strip()
    question = req.message.strip()

    # 1) 사용자 확인
    user = get_user_by_id(db, uid)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"사용자 정보를 찾을 수 없습니다. (user_id='{uid}')")
    if not question:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="질문이 비어 있습니다.")

    force_llm = should_force_llm(body)
    nocache = should_skip_cache(body)

    # === 경로 A: LLM 강제 (DB/캐시 우회) ===
    if force_llm:
        try:
            ans = gpt_answer(question)
            gpt_title = ans.get("title") or "자동 생성된 요약"
            gpt_link = ans.get("link")
            gpt_summary = ans.get("summary") or ""
        except Exception as e:
            print(f"[WARN] GPT call failed (force): {e}")
            gpt_title, gpt_link = "GPT 응답 생성 실패(임시)", None
            gpt_summary = "현재 외부 응답 생성에 실패했습니다. 잠시 후 다시 시도해주세요."

        # 로그 저장
        try:
            chat_log = ChatLog(
                user_id=uid,
                message=question,
                summary=f"{gpt_title}\n{gpt_link or ''}\n{gpt_summary}".strip(),
                timestamp=datetime.utcnow(),
            )
            db.add(chat_log); db.commit()
        except Exception as e:
            print(f"[WARN] chat log 저장 실패(force LLM): {e}")
            db.rollback()

        # 캐시 저장 (nocache가 아니면)
        if not nocache:
            try:
                upsert_cache(db, uid, question, {"title": gpt_title, "link": gpt_link, "summary": gpt_summary})
            except Exception as e:
                print(f"[WARN] cache upsert 실패(force LLM): {e}")

        item = ChatResponseItem(title=gpt_title, link=gpt_link, summary=gpt_summary)
        return ChatResponse(results=[item], timestamp=datetime.utcnow(),
                            title=item.title, link=item.link, summary=item.summary)

    # === 경로 B: 기본(캐시 → LLM) ===
    cached = None
    if not nocache:
        try:
            cached = get_cached_answer(db, uid, question)
        except TypeError:
            try:
                cached = get_cached_answer(db, question)
            except Exception:
                cached = None

    if cached:
        if isinstance(cached, dict):
            title = cached.get("title") or "자동 생성된 요약"
            link = cached.get("link")
            summary = cached.get("summary") or ""
        else:
            d = getattr(cached, "__dict__", {})
            title = d.get("title") or "자동 생성된 요약"
            link = d.get("link")
            summary = d.get("summary") or d.get("content") or ""
        item = ChatResponseItem(title=title, link=link, summary=summary)
        return ChatResponse(results=[item], timestamp=datetime.utcnow(),
                            title=item.title, link=item.link, summary=item.summary)

    # LLM 호출
    try:
        ans = gpt_answer(question)
        gpt_title = ans.get("title") or "자동 생성된 요약"
        gpt_link = ans.get("link")
        gpt_summary = ans.get("summary") or ""
    except Exception as e:
        print(f"[WARN] GPT call failed: {e}")
        gpt_title, gpt_link = "GPT 응답 생성 실패(임시)", None
        gpt_summary = "현재 외부 응답 생성에 실패했습니다. 잠시 후 다시 시도해주세요."

    # 로그 저장
    try:
        chat_log = ChatLog(
            user_id=uid,
            message=question,
            summary=f"{gpt_title}\n{gpt_link or ''}\n{gpt_summary}".strip(),
            timestamp=datetime.utcnow(),
        )
        db.add(chat_log); db.commit()
    except Exception as e:
        print(f"[WARN] chat log 저장 실패: {e}")
        db.rollback()

    # 캐시 저장 (nocache가 아니면)
    if not nocache:
        try:
            upsert_cache(db, uid, question, {"title": gpt_title, "link": gpt_link, "summary": gpt_summary})
        except TypeError:
            try:
                upsert_cache(db, question, gpt_title, gpt_link, gpt_summary)
            except Exception as e:
                print(f"[WARN] cache upsert 실패: {e}")
        except Exception as e:
            print(f"[WARN] cache upsert 실패: {e}")

    # chat_api 마지막 반환부
    item = ChatResponseItem(title=gpt_title, link=gpt_link, summary=gpt_summary)
    return ChatResponse(
    results=[item],
    timestamp=datetime.utcnow(),
    title=item.title,      # ✅ 최상위도 채움
    link=item.link,
    summary=item.summary,
    )
