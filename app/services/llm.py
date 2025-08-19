# app/services/llm.py
import os, json
from typing import Optional, Dict
from openai import OpenAI

def _load_system_prompt() -> str:
    """
    시스템 프롬프트를 주입하는 우선순위:
    1) SYSTEM_PROMPT_FILE 경로에 있는 파일 내용
    2) SYSTEM_PROMPT 환경변수
    3) 기본값(임시 프롬프트)
    👉 팀의 공식 프롬프트를 파일/환경변수로 넣어 쓰면 된다.
    """
    path = os.getenv("SYSTEM_PROMPT_FILE")
    if path and os.path.exists(path):
        try:
            return open(path, "r", encoding="utf-8").read()
        except Exception:
            pass
    return os.getenv("SYSTEM_PROMPT", "").strip() or (
        "역할: 대학 행정/공지/학사 도우미.\n"
        "규칙: 항상 한국어로 간결/정확하게 답하고, JSON만 반환.\n"
        '출력 스키마: {"title": str, "link": str|null, "summary": str}'
    )

_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
_SYSTEM = _load_system_prompt()

def _parse_json(content: str) -> Dict[str, Optional[str]]:
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
    필요하면 context로 추가 힌트를 전달할 수 있음.
    """
    messages = [
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": (f"질문: {question}\n\n추가컨텍스트:\n{context}" if context else question)},
        {"role": "user", "content": '다음 JSON 스키마로만 응답하세요: {"title": str, "link": str|null, "summary": str}'},
    ]
    resp = _client.chat.completions.create(
        model=_MODEL,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.2")),
        timeout=60,
    )
    return _parse_json(resp.choices[0].message.content)
