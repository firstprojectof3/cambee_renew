# routers/chat.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.schemas import ChatRequest, ChatResponse
from app.crud import get_user_by_id
from app.database import get_db
from app.schema_models import ChatLog

# notices 로드 (ORM 객체일 수도 있음)
try:
    from app.tests.insert_dummy_data import test_notices  # list[Notice | dict | str]
    RAW_NOTICES = test_notices
except Exception as e:
    print(f"[WARN] insert_dummy_data.test_notices import 실패: {e}")
    RAW_NOTICES = []

router = APIRouter()

# ---------- 안전 추출 유틸 ----------
def safe_get_from_orm_dict(obj_dict, candidates):
    """ORM 객체의 __dict__에서만 안전하게 뽑기 (lazy-load 방지)"""
    for key in candidates:
        if key in obj_dict and obj_dict[key] is not None:
            return str(obj_dict[key])
    return ""

def extract_title(n):
    """
    dict/str/ORM(Notice) 모두에서 '제목' 문자열만 안전하게 추출.
    ORM은 __dict__만 사용해서 DetachedInstanceError 방지.
    """
    if n is None:
        return ""
    if isinstance(n, str):
        return n
    if isinstance(n, dict):
        return str(n.get("title") or n.get("name") or n.get("subject") or "")
    # ORM or 기타 객체
    d = getattr(n, "__dict__", {})  # 세션 호출 없이 로컬 메모리만 사용
    return safe_get_from_orm_dict(d, ["title", "name", "subject", "headline"])

def extract_url(n):
    if n is None or isinstance(n, str):
        return None
    if isinstance(n, dict):
        return n.get("url") or n.get("link") or n.get("href")
    d = getattr(n, "__dict__", {})
    val = safe_get_from_orm_dict(d, ["url", "link", "href"])
    return val or None

# 시작 시점에 한 번 정규화: [{title:str, url: Optional[str]}]
NORMALIZED_NOTICES = []
for item in RAW_NOTICES:
    title = extract_title(item)
    if title:  # 빈 제목은 제외
        NORMALIZED_NOTICES.append({
            "title": title,
            "url": extract_url(item)
        })

# ---------- 필터: 제목에 '장학' 포함 ----------
def filter_notices_by_scholarship(notices):
    return [n for n in notices if "장학" in n["title"]]

@router.post("/chat", response_model=ChatResponse)
async def chat_api(request: ChatRequest, db: Session = Depends(get_db)):
    # 0) 유저 확인
    user = get_user_by_id(db, request.user_id)
    if not user:
        return ChatResponse(
            summary="사용자 정보를 찾을 수 없습니다.",
            timestamp=datetime.utcnow().isoformat(),
        )

    # 1) 장학 공지 필터링 (정규화된 리스트 사용)
    filtered = filter_notices_by_scholarship(NORMALIZED_NOTICES)

    # 2) 표시 텍스트
    if filtered:
        lines = []
        for n in filtered:
            if n["url"]:
                lines.append(f"- {n['title']} ({n['url']})")
            else:
                lines.append(f"- {n['title']}")
        notice_text = "\n".join(lines)
    else:
        notice_text = "장학 관련 공지가 없습니다."

    # 3) 응답
    summary = (
        f"{user.name}({user.major}, {user.grade}학년)\n"
        f"{notice_text}\n"
        f"질문: {request.message}"
    )

    # 4) 로그 저장
    chat_log = ChatLog(
        user_id=request.user_id,
        message=request.message,
        summary=summary,
        timestamp=datetime.utcnow(),
    )
    db.add(chat_log)
    db.commit()

    # 5) 반환
    return ChatResponse(
        summary=summary,
        timestamp=datetime.utcnow().isoformat(),
    )
