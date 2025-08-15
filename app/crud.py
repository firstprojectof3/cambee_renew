# crud.py
from typing import Any, Dict, List, Optional, Tuple
import json, re

from sqlalchemy.orm import Session
from app.schema_models import User
from app.schemas import UserCreate

# ---------------- DB ----------------
def create_user(db: Session, user: UserCreate):
    db_user = User(**user.dict())
    db.add(db_user); db.commit(); db.refresh(db_user)
    return db_user

def get_user_by_id(db: Session, user_id: str):
    return db.query(User).filter(User.user_id == user_id).first()

# ------------- Utils ---------------
def _safe_lower(s: Optional[str]) -> str:
    return (s or "").strip().lower()

def _is_all_marker(x: Any) -> bool:
    if x is None: return True
    if isinstance(x, (list, tuple, set)) and len(x) == 0: return True
    if isinstance(x, int) and x == 0: return True
    if isinstance(x, str):
        t = x.strip().lower()
        return t in ("", "전체", "전학년", "전 학년", "전체대상", "전체 대상",
                     "무관", "해당없음", "해당 없음", "all", "none", "any")
    return False

def _to_list(x: Any) -> List[Any]:
    if x is None: return []
    if isinstance(x, (list, tuple, set)): return list(x)
    if isinstance(x, str):
        t = x.strip()
        if t == "": return []
        if (t.startswith("[") and t.endswith("]")) or (t.startswith("{") and t.endswith("}")):
            try:
                j = json.loads(t)
                return j if isinstance(j, list) else [j]
            except Exception:
                pass
        if "," in t: return [s.strip() for s in t.split(",") if s.strip()]
        return [t]
    return [x]

def _two_digit_year_from_student_no(sn: Any) -> Optional[str]:
    if sn is None: return None
    s = str(sn).strip()
    return s[:2] if len(s) >= 2 and s[:2].isdigit() else None

def _extract_two_digit_year_token(x: Any) -> Optional[str]:
    if x is None: return None
    if isinstance(x, int) and x == 0: return None
    if isinstance(x, str) and x.strip() == "0": return None
    if isinstance(x, (list, tuple, set)): return None
    s = str(x).strip()
    nums = re.findall(r"\d+", s)
    if not nums: return None
    c = nums[-1]
    if len(c) >= 4 and c.isdigit(): return c[-2:]
    if len(c) >= 2 and c.isdigit(): return c[:2]
    return None

_MAJOR_MAP = {
    "컴퓨터공학전공": "컴퓨터공학전공",
    "컴퓨터공학과": "컴퓨터공학전공",
    "컴퓨터공학부": "컴퓨터공학전공",
    "소프트웨어학부": "소프트웨어학부",
    "사학과": "사학과",
    "경영학과": "경영학과",
}

def _norm_major(x: Optional[str]) -> Optional[str]:
    if not x: return None
    lx = _safe_lower(x)
    for k, v in _MAJOR_MAP.items():
        if _safe_lower(k) == lx: return v
    return x.strip()

# ----------- Matchers --------------
def _match_major(user_major: Optional[str], target_major: Any) -> bool:
    if _is_all_marker(target_major): return True
    u = _norm_major(user_major) if user_major else None
    targets = [_norm_major(m) for m in _to_list(target_major)]
    return (u is not None) and (u in targets)

def _match_grade(user_grade: Optional[int], target_grade: Any) -> bool:
    if _is_all_marker(target_grade): return True
    if user_grade is None: return False
    tg_list = _to_list(target_grade); norm: List[int] = []
    for g in tg_list:
        if g is None: continue
        if isinstance(g, str):
            nums = re.findall(r"\d+", g)
            if nums:
                try: norm.append(int(nums[-1])); continue
                except Exception: pass
            continue
        try: norm.append(int(g))
        except Exception: continue
    if len(norm) == 0: return True
    return user_grade in norm

def _normalize_sn_targets(target_sn: Any) -> List[str]:
    if _is_all_marker(target_sn): return []
    acc: List[str] = []
    for item in _to_list(target_sn):
        if isinstance(item, (list, tuple, set)):
            for sub in item:
                y = _extract_two_digit_year_token(sub)
                if y: acc.append(y)
            continue
        y = _extract_two_digit_year_token(item)
        if y: acc.append(y)
    return list(dict.fromkeys(acc))

def _match_sn_prefix(user_sn: Any, target_sn: Any) -> bool:
    targets = _normalize_sn_targets(target_sn)
    if len(targets) == 0: return True
    u_prefix = _two_digit_year_from_student_no(user_sn)
    if u_prefix is None: return False
    return u_prefix in targets

def _filter_single_notice(user, notice) -> Tuple[bool, List[str]]:
    reasons: List[str] = []
    user_major = getattr(user, "major", None)
    user_grade = getattr(user, "grade", None)
    user_sn    = getattr(user, "student_number", None)
    n_major = getattr(notice, "target_major", None)
    n_grade = getattr(notice, "target_grade", None)
    n_sn    = getattr(notice, "target_student_number", None)

    if not _match_major(user_major, n_major): reasons.append("전공 불일치")
    if not _match_grade(user_grade, n_grade): reasons.append("학년 불일치")
    if not _match_sn_prefix(user_sn, n_sn):   reasons.append("학번 앞2자리 불일치")
    return (len(reasons) == 0, reasons)

# ------------- Intent --------------
def _pick_category(question: Optional[str]) -> Optional[str]:
    if not question: return None
    q = question.lower()
    rules = {
        "장학": ["장학", "학자금", "국가장학금", "국가 근로", "국가근로", "등록금"],
        "학사": ["학사", "수강", "신청", "졸업", "휴학", "복학", "시뮬레이션", "수강시뮬레이션", "졸업시뮬레이션"],
        "식단": ["식단", "학식", "메뉴", "밥"],
    }
    for cat, kws in rules.items():
        if any(kw in q for kw in kws):
            return cat
    return None

# ------------- Filter --------------
def filter_notices_by_user_info(
    user,
    notices: List[Any],
    question: Optional[str] = None,
    debug: bool = False,
    return_both: bool = False
):
    want_cat = _pick_category(question)
    passed: List[Any] = []
    dropped: List[Dict[str, Any]] = []

    for n in notices:
        n_cat = (getattr(n, "category", "") or "").strip()
        if want_cat is None:
            dropped.append({"notice": n, "reasons": ["질문 카테고리 없음"]})
            if debug:
                print(f"   └ 제외: {getattr(n, 'title', '(제목없음)')} -> 질문 카테고리 없음")
            continue

        if n_cat != want_cat:
            dropped.append({"notice": n, "reasons": ["카테고리 불일치"]})
            if debug:
                print(f"   └ 제외: {getattr(n, 'title', '(제목없음)')} -> 카테고리 불일치")
            continue

        ok, reasons = _filter_single_notice(user, n)
        if ok:
            passed.append(n)
        else:
            dropped.append({"notice": n, "reasons": reasons})
            if debug:
                print(f"   └ 제외: {getattr(n, 'title', '(제목없음)')} -> {', '.join(reasons)}")

    if return_both:
        return passed, dropped
    return passed
