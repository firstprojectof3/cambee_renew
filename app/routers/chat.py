# routers/chat.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import re

# Pydantic 스키마 임포트 (수정된 app/schemas.py에서 가져옴)
from app.schemas import ChatRequest, ChatResponse, User as PydanticUser # Pydantic User 모델 임포트
# DB 모델 임포트
from app.crud import get_user_by_id # 사용자 정보를 DB에서 가져오는 함수
from app.database import get_db
from app.schema_models import ChatLog, User # DB 모델의 User와 Notice 임포트

# Notice 모델(있으면 사용)
try:
    from app.schema_models import Notice
except Exception:
    Notice = None

# 테스트/더미 공지(폴백)
try:
    from app.tests.insert_dummy_data import test_notices  # list[Notice | dict | str]
    RAW_NOTICES = test_notices
except Exception as e:
    print(f"[WARN] insert_dummy_data.test_notices import 실패: {e}")
    RAW_NOTICES = []

router = APIRouter()

# ---------------- 공용 유틸 ----------------
def safe_get_from_orm_dict(obj_dict, candidates):
    for key in candidates:
        if key in obj_dict and obj_dict[key] is not None:
            return str(obj_dict[key])
    return ""

def extract_title(n):
    if n is None:
        return ""
    if isinstance(n, str):
        return n
    if isinstance(n, dict):
        return str(
            n.get("title")
            or n.get("name")
            or n.get("subject")
            or n.get("제목")
            or n.get("headline")
            or ""
        )
    d = getattr(n, "__dict__", {})
    return safe_get_from_orm_dict(d, ["title", "name", "subject", "제목", "headline"])

def extract_url(n):
    if n is None or isinstance(n, str):
        return None
    if isinstance(n, dict):
        return n.get("url") or n.get("link") or n.get("href")
    d = getattr(n, "__dict__", {})
    return safe_get_from_orm_dict(d, ["url", "link", "href"]) or None

def extract_category(n):
    if n is None or isinstance(n, str):
        return ""
    if isinstance(n, dict):
        return str(
            n.get("category")
            or n.get("분류")
            or n.get("type")
            or n.get("kind")
            or n.get("tag")
            or ""
        )
    d = getattr(n, "__dict__", {})
    return safe_get_from_orm_dict(d, ["category", "분류", "type", "kind", "tag"])

def extract_dept(n):
    """공지의 소속(학과/전공/단과대)을 최대한 읽어온다."""
    if n is None or isinstance(n, str):
        return ""
    if isinstance(n, dict):
        return str(
            n.get("dept")
            or n.get("department")
            or n.get("학과")
            or n.get("전공")
            or n.get("학부")
            or n.get("단과대")
            or n.get("college")
            or n.get("소속")
            or n.get("부서")
            or ""
        )
    d = getattr(n, "__dict__", {})
    return safe_get_from_orm_dict(d, ["dept", "department", "학과", "전공", "학부", "단과대", "college", "소속", "부서"])

def normalize_item(item):
    title = extract_title(item)
    if not title:
        return None
    return {
        "title": title,
        "url": extract_url(item),
        "category": extract_category(item),
        "dept": extract_dept(item),
    }

def load_normalized_notices(db: Session):
    items = []
    if Notice is not None:
        try:
            items = db.query(Notice).all()
        except Exception as e:
            print(f"[WARN] DB Notice 조회 실패: {e}")
    if not items:
        items = RAW_NOTICES

    out = []
    for it in items:
        n = normalize_item(it)
        if n:
            out.append(n)
    return out

# ---------------- 의도/전공 처리 ----------------
PRIO_ORDER = ["수강", "등록금", "시험", "장학", "식단", "학사"]

INTENT_SYNONYMS = {
    "수강": ["수강", "수강신청", "수강 신청", "수강정정", "정정", "수강취소", "철회", "휴보강", "폐강", "수업", "강의", "시간표", "과목", "교과목"],
    "등록금": ["등록금", "등록", "납부", "수업료", "분납"],
    "시험": ["시험", "중간", "기말", "퀴즈", "평가"],
    "장학": ["장학", "장학금", "장학생"],
    "식단": ["식단", "오늘의식단", "학식", "구내식당", "메뉴"],
    "학사": ["학사", "학사공지", "학사 일정", "학사일정", "학사안내", "학사정보"],
}

BROAD_KEYS = {"학사"}
STOPWORDS = {"공지", "안내", "관련", "정보", "일정"}

MAJOR_SYNONYMS = {
    "컴퓨터공학": ["컴퓨터공학", "컴퓨터공학과", "컴공", "컴퓨터학과", "컴퓨터공학전공", "컴퓨터"],
    "소프트웨어": ["소프트웨어", "소프트웨어학과", "SW", "소웨"],
}
MAJOR_PRONOUN_PATTERNS = [
    r"(내|나의|우리)\s*(전공|학과|학부)",
    r"소속\s*(전공|학과|학부)",
]

def canonical_major(s: str) -> str:
    s = (s or "").strip()
    s = re.sub(r"(학과|전공|과)$", "", s)
    s = s.replace(" ", "")
    for canon, syns in MAJOR_SYNONYMS.items():
        if s in [canonical_major(syn) for syn in syns]:
            return canon
    return s

def norm(s: str) -> str:
    return re.sub(r"\s+", "", (s or "").strip())

def choose_intent(msg: str):
    if not msg:
        return None
    if ("전체" in msg or "모든" in msg) and ("공지" in msg or "게시" in msg):
        return "__ALL__"
    hits = set()
    nmsg = norm(msg)
    for intent in PRIO_ORDER:
        for alias in INTENT_SYNONYMS[intent]:
            if norm(alias) in nmsg:
                hits.add(intent)
                break
    hits -= STOPWORDS
    for intent in PRIO_ORDER:
        if intent in hits:
            return intent
    return None

def find_major_in_text(msg: str, user_major: str):
    text = (msg or "").strip()
    for canon, syns in MAJOR_SYNONYMS.items():
        for w in syns:
            if w in text:
                return canon, "explicit"
    for pat in MAJOR_PRONOUN_PATTERNS:
        if re.search(pat, text):
            canon_user_major = canonical_major(user_major)
            if canon_user_major:
                return canon_user_major, "mine"
    return "", None

def match_intent(notice, intent: str) -> bool:
    if intent is None:
        return False
    if intent == "__ALL__":
        return True
    T = norm(notice["title"])
    C = norm(notice["category"])
    if intent in BROAD_KEYS:
        for alias in INTENT_SYNONYMS[intent]:
            na = norm(alias)
            if na and (na in T or na in C):
                return True
        return "학사" in C
    for alias in INTENT_SYNONYMS[intent]:
        na = norm(alias)
        if na and (na in T or na in C):
            return True
    return False

def match_major(notice, major_canon: str) -> bool:
    if not major_canon:
        return True
    
    notice_dept = canonical_major(notice["dept"])
    notice_title = canonical_major(notice["title"])
    notice_category = canonical_major(notice["category"])

    syns = [canonical_major(s) for s in MAJOR_SYNONYMS.get(major_canon, [major_canon])]
    
    for w in syns:
        if w and (w in notice_dept or w in notice_title or w in notice_category):
            return True
    return False

def filter_with_intent_and_major(notices, intent: str, major_canon: str, major_source: str):
    base = [n for n in notices if match_intent(n, intent)] if intent else []
    if intent == "__ALL__":
        base = notices[:]
    if not base:
        return []

    if major_source in ("explicit", "mine") and major_canon:
        return [n for n in base if match_major(n, major_canon)]

    return base

# ---------------- 라우터 ----------------
@router.post("/chat", response_model=ChatResponse)
async def chat_api(request: ChatRequest, db: Session = Depends(get_db)):
    # 0) 유저 확인: ChatRequest에서 받은 user_id를 사용
    uid_raw = request.user_id # request.user_id는 이미 constr 패턴으로 유효성 검사됨
    uid_str = str(uid_raw).strip() # 혹시 모를 공백 제거 및 문자열 확실히 보장

    user = get_user_by_id(db, uid_str)
    
    # DB의 user_id 타입이 int일 경우를 대비한 추가 시도 (필요시)
    # 현재 Pydantic ChatRequest의 user_id는 str(숫자만)이므로, DB의 user_id 타입에 따라 적절히 변환.
    # 만약 DB의 user_id가 int라면 아래 로직 필요.
    # if not user:
    #     try:
    #         user = get_user_by_id(db, int(uid_str))
    #     except ValueError:
    #         pass # int 변환 실패 시 무시

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"사용자 정보를 찾을 수 없습니다. (user_id='{uid_str}')",
        )

    # 1) 공지 로드
    notices = load_normalized_notices(db)

    # 2) 의도 + 전공 결정
    intent = choose_intent(request.message)
    major_canon, major_source = find_major_in_text(request.message, user.major) 

    # 3) 필터링
    filtered = filter_with_intent_and_major(notices, intent, major_canon, major_source)

    # 4) 출력 문구
    if filtered:
        MAX_SHOW = 10
        lines = []
        for n in filtered[:MAX_SHOW]:
            if n["url"]:
                lines.append(f"- {n['title']} ({n['url']})")
            else:
                lines.append(f"- {n['title']}")
        more = f"\n... 외 {len(filtered) - MAX_SHOW}건" if len(filtered) > MAX_SHOW else ""
        head_parts = []
        if intent and intent != "__ALL__":
            head_parts.append(f"'{intent}'")
        if major_source == "explicit" and major_canon:
            head_parts.append(f"'{major_canon}' 전공")
        elif major_source == "mine" and major_canon:
            head_parts.append(f"'{major_canon}' (내 전공)")
        head_txt = " 및 ".join(head_parts) if head_parts else "요청과 관련된"
        
        reply_text_body = f"{head_txt} 공지입니다:\n" + "\n. ".join(lines) + more
    else:
        if major_source == "explicit" and major_canon:
            reply_text_body = f"요청하신 전공('{major_canon}')의 관련 공지를 찾지 못했어요."
        elif major_source == "mine" and user.major:
            reply_text_body = f"'{user.major}' (내 전공) 관련 공지를 찾지 못했어요."
        elif intent in (None, "__ALL__"):
            reply_text_body = "질문에서 키워드를 찾지 못했어요. 예) '학사 공지', '내 전공의 학사 공지', '컴퓨터공학 학사 공지'"
        else:
            reply_text_body = f"'{intent}' 관련 공지를 찾지 못했어요."

    # 최종 reply_text 구성
    final_reply_content = (
        f"{user.name}({user.major}, {user.grade}학년)\n"
        f"{reply_text_body}\n"
        f"질문: {request.message}"
    )

    # 5) 로그 저장
    chat_log = ChatLog(
        user_id=uid_str, 
        message=request.message,
        summary=final_reply_content, 
        timestamp=datetime.utcnow(),
    )
    db.add(chat_log)
    db.commit()

    # 6) 반환
    return ChatResponse(
        reply=final_reply_content, 
        timestamp=datetime.utcnow().isoformat(),
    )

# (선택) 디버그용
@router.get("/debug/notices")
def debug_notices(db: Session = Depends(get_db)):
    notices = load_normalized_notices(db)
    return {
        "count": len(notices),
        "samples": [n["title"] for n in notices[:8]],
    }