# app/services/llm.py
from __future__ import annotations

import json
import os
from typing import Optional, Dict, List

from openai import OpenAI
from sqlalchemy.orm import Session
from app.core import config
from app.database import SessionLocal
from app.models.models import Notice
from app.services.crawl_pipeline import crawl_and_store  # ✅ 파이프라인 사용


def _get_system_prompt() -> str:
    return config.SYSTEM_PROMPT or (
        "역할: 대학 행정/공지/학사 도우미.\n"
        "규칙: 항상 한국어로 간결/정확하게 답하고, JSON만 반환.\n"
        '출력 스키마: {"title": str, "link": str|null, "summary": str}'
    )


if not config.OPENAI_API_KEY:
    raise RuntimeError("[LLM] OPENAI_API_KEY가 비어 있습니다. .env에 OPENAI_API_KEY를 설정하세요.")

_client = OpenAI(api_key=config.OPENAI_API_KEY)
_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))
_SYSTEM = _get_system_prompt()


def _parse_json(content: str) -> Dict[str, Optional[str]]:
    try:
        data = json.loads(content or "{}")
    except Exception:
        data = {}
    title = data.get("title") or "자동 생성된 요약"
    link = data.get("link")
    summary = data.get("summary") or ""
    return {"title": str(title), "link": (str(link) if link else None), "summary": str(summary)}


def _recent_notices(db: Session, limit: int = 3) -> List[Notice]:
    return (
        db.query(Notice)
        .order_by(Notice.date.desc().nullslast(), Notice.created_at.desc())
        .limit(limit)
        .all()
    )


def _notice_context_from_list(rows: List[Notice]) -> str:
    lines = []
    for n in rows:
        d = (n.date or n.created_at)
        d_str = d.isoformat()[:10] if d else ""
        preview = (n.content or "")[:120].replace("\n", " ").strip()
        lines.append(f"- {n.title} ({d_str}) {n.url}\n  {preview}")
    return "\n".join(lines)


def _crawl_refresh(db: Session, limit: int = 30) -> None:
    seeds = getattr(config, "CRAWL_SEEDS", None) or [
        "https://www.ewha.ac.kr/ewha/news/notice.do"
    ]
    for url in seeds:
        try:
            crawl_and_store(db, url, limit=limit)
        except Exception as e:
            print(f"[WARN] crawl failed for {url}: {e}")


def gpt_answer(question: str, context: Optional[str] = None) -> Dict[str, Optional[str]]:
    db = SessionLocal()
    try:
        _crawl_refresh(db, limit=30)
        recent = _recent_notices(db, limit=3)
        notice_ctx = _notice_context_from_list(recent)
        top_link = recent[0].url if recent else None
    finally:
        db.close()

    user_content = f"질문: {question}"
    if notice_ctx:
        user_content += f"\n\n최근 공지사항 요약:\n{notice_ctx}"
    if context:
        user_content += f"\n\n추가컨텍스트:\n{context}"

    messages = [
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": user_content},
        {
            "role": "user",
            "content": '다음 JSON 스키마로만 응답하세요: {"title": str, "link": str|null, "summary": str}',
        },
    ]

    resp = _client.chat.completions.create(
        model=_MODEL,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=_TEMPERATURE,
    )
    result = _parse_json(resp.choices[0].message.content or "")
    if not result.get("link") and top_link:
        result["link"] = top_link
    return result
