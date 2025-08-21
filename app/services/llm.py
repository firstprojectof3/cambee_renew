# app/services/llm.py
from __future__ import annotations

import json
from typing import Optional, Dict

from openai import OpenAI
from app.core import config


# --- System Prompt 로딩: config에서만 관리 ---
def _get_system_prompt() -> str:
    """
    우선순위는 config.py가 이미 처리:
    - SYSTEM_PROMPT_FILE → 파일 내용
    - SYSTEM_PROMPT     → 문자열 값
    - 둘 다 없으면 기본값
    """
    return config.SYSTEM_PROMPT or (
        "역할: 대학 행정/공지/학사 도우미.\n"
        "규칙: 항상 한국어로 간결/정확하게 답하고, JSON만 반환.\n"
        '출력 스키마: {"title": str, "link": str|null, "summary": str}'
    )


# --- OpenAI 클라이언트 (config에서 키 로드) ---
if not config.OPENAI_API_KEY:
    raise RuntimeError(
        "[LLM] OPENAI_API_KEY가 비어 있습니다. .env에 OPENAI_API_KEY를 설정하세요."
    )

_client = OpenAI(api_key=config.OPENAI_API_KEY)

# 모델/온도는 유연하게: 모델명만 필요시 .env에서 조절 (없으면 기본)
# 예) OPENAI_MODEL=gpt-4o-mini / OPENAI_TEMPERATURE=0.2
import os
_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))

_SYSTEM = _get_system_prompt()


def _parse_json(content: str) -> Dict[str, Optional[str]]:
    """
    모델이 json_object로 응답하더라도 혹시를 대비해 안전 파싱.
    """
    try:
        data = json.loads(content or "{}")
    except Exception:
        data = {}

    title = data.get("title") or "자동 생성된 요약"
    link = data.get("link")
    summary = data.get("summary") or ""

    return {
        "title": str(title),
        "link": (str(link) if link else None),
        "summary": str(summary),
    }


def gpt_answer(question: str, context: Optional[str] = None) -> Dict[str, Optional[str]]:
    """
    단일 LLM 호출로 JSON 응답 생성. (외부 검색 없음)
    필요시 context로 추가 힌트를 전달.
    """
    user_content = (
        f"질문: {question}\n\n추가컨텍스트:\n{context}" if context else question
    )

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
    return _parse_json(resp.choices[0].message.content or "")
