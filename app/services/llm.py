# app/services/llm.py
from __future__ import annotations
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime

from openai import OpenAI

# -------- 기본 설정 --------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PROMPT_ID = os.getenv("OPENAI_PROMPT_ID")  # 프롬프트 ID (예: prmpt_abc123)
PROMPT_VERSION = "latest"  # 고정 추천. 필요시 대시보드 버전 문자열로 변경

_client = OpenAI(api_key=OPENAI_API_KEY)

# 모델이 꼭 JSON 스키마로 말하도록 강제: title/link/summary
def _coerce_to_schema(text: str) -> Dict[str, str]:
    """
    모델이 JSON으로 잘 줬으면 그대로 파싱,
    아니면 안전하게 감싸서 title/link/summary를 만들어 준다.
    """
    try:
        data = json.loads(text)
        title = str(data.get("title", "")).strip()
        link = str(data.get("link", "")).strip() or None
        summary = str(data.get("summary", "")).strip()
        if title or summary:
            return {"title": title, "link": link, "summary": summary}
    except Exception:
        pass
    # fallback: 전부 요약으로 몰아넣기
    cleaned = text.strip()
    first_line = cleaned.splitlines()[0] if cleaned else ""
    return {"title": first_line[:80], "link": None, "summary": cleaned[:2000]}

def ask_with_prompt_id(*, user: Dict[str, Any], message: str) -> Dict[str, Optional[str]]:
    """
    OpenAI Prompt(ID) + Responses API 호출.
    반환: {"title": str, "link": Optional[str], "summary": str}
    """
    # 템플릿 변수(대시보드에서 정의한 변수명과 일치해야 함)
    variables = {
        "question": message,
        "user_major": user.get("major") or "",
        "user_grade": str(user.get("grade") or ""),
        "user_student_number": str(user.get("student_number") or ""),
        "today": datetime.now().strftime("%Y-%m-%d"),
    }

    # Responses API 호출 (prompt 객체 사용)
    resp = _client.responses.create(
        prompt={
            "id": PROMPT_ID,
            "version": PROMPT_VERSION,
            "variables": variables,
        },
        # 모델을 프롬프트 내부에서 지정했다면 생략 가능
        # model="gpt-5.1-mini",
    )

    # text 추출
    # Responses API는 output_text 헬퍼가 있거나(라이브러리 버전에 따라),
    # output[0].content[0].text.value 형태로 도달할 수 있음.
    text_out = None
    try:
        # SDK 헬퍼 우선
        if hasattr(resp, "output_text") and callable(getattr(resp, "output_text")):
            text_out = resp.output_text
        else:
            # 수동 파싱
            # 첫 content의 텍스트 값 사용
            if resp.output and len(resp.output) > 0:
                first_item = resp.output[0]
                if first_item.get("content"):
                    first_content = first_item["content"][0]
                    text_out = first_content.get("text", {}).get("value")
    except Exception:
        pass

    text_out = text_out or ""
    return _coerce_to_schema(text_out)
