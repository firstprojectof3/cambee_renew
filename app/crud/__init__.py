# app/crud/__init__.py
from __future__ import annotations

import importlib
from typing import Any, Callable, Optional, Dict, List

__all__ = [
    "get_user_by_id",
    "get_cached_answer",
    "upsert_cache",
    "filter_notices_by_user_info",
]

# ----------------------------------------
# 1) 공통 유틸: 심볼을 여러 후보 모듈에서 탐색
# ----------------------------------------
def _resolve(attr: str, candidates: List[str]) -> Optional[Callable[..., Any]]:
    for mod_name in candidates:
        try:
            mod = importlib.import_module(mod_name, package=__package__)
            fn = getattr(mod, attr, None)
            if callable(fn):
                print(f"[crud] using {attr} from {mod_name}")
                return fn
        except Exception:
            continue
    return None

# ----------------------------------------
# 2) 레지스트리: 함수명 -> 후보 모듈들
# ----------------------------------------
_REGISTRY: Dict[str, List[str]] = {
    "get_user_by_id": [
        ".user",
        ".users",
        ".crud_user",
        ".repositories.user_repo",
    ],
    "get_cached_answer": [
        ".cache",
        ".gpt_cache",
        ".cache_repo",
    ],
    "upsert_cache": [
        ".cache",
        ".gpt_cache",
        ".cache_repo",
    ],
    "filter_notices_by_user_info": [
        ".notice",
        ".notices",
        ".filters",
        ".filtering",
        ".preprocess",
        ".notice_filter",
    ],
}

# 동적 바인딩 (있으면 그걸로 사용)
for _name, _cands in _REGISTRY.items():
    globals()[_name] = _resolve(_name, _cands)

# ----------------------------------------
# 3) 안전 Fallback 구현(가변 인자 지원)
# ----------------------------------------

# (a) get_user_by_id
if globals().get("get_user_by_id") is None:
    try:
        try:
            from app.models.models import User  # type: ignore
        except Exception:
            from app.models import User  # type: ignore
        from sqlalchemy.orm import Session  # type: ignore

        def get_user_by_id(db: "Session", user_id: str):
            print("[crud][fallback] get_user_by_id: using generic query")
            try:
                return db.query(User).filter(getattr(User, "user_id") == user_id).first()
            except Exception:
                return db.query(User).filter(getattr(User, "id") == user_id).first()
    except Exception:
        def get_user_by_id(*args, **kwargs):
            raise ImportError(
                "[crud] 'get_user_by_id'를 찾을 수 없고 User 모델도 확인 실패. "
                "app/models/models.py 또는 app/models.py에 User 모델이 있는지 확인하세요."
            )

# (b) get_cached_answer  —— 다양한 호출 형태 지원
#    허용 예:
#    - get_cached_answer(db)
#    - get_cached_answer(db, user_id)
#    - get_cached_answer(db, user_id, question)
#    - get_cached_answer(db, question="...", user_id="...")
if globals().get("get_cached_answer") is None:
    def get_cached_answer(*args, **kwargs):
        print("[crud][fallback] get_cached_answer: returning None (no cache module)")
        # 호환을 위해 위치/키워드 인자 파싱만 하고 결과는 항상 None
        # args: (db, [user_id], [question])
        # kwargs: user_id=..., question=...
        return None

# (c) upsert_cache —— 다양한 호출 형태 지원
#    허용 예:
#    - upsert_cache(db, user_id, question, answer)
#    - upsert_cache(db, key, answer)
#    - upsert_cache(db, answer=..., user_id=..., question=...)
if globals().get("upsert_cache") is None:
    def upsert_cache(*args, **kwargs):
        print("[crud][fallback] upsert_cache: no-op (no cache module)")
        return None

# (d) filter_notices_by_user_info —— 다양한 시그니처 지원
#    허용 예:
#    - filter_notices_by_user_info(db, notices, user)
#    - filter_notices_by_user_info(notices, user)
if globals().get("filter_notices_by_user_info") is None:
    def filter_notices_by_user_info(*args, **kwargs) -> list:
        print("[crud][fallback] filter_notices_by_user_info: passthrough")
        # notices를 최선으로 찾아서 리스트로 반환
        notices = []
        for a in args:
            if isinstance(a, list):
                notices = a
                break
        if "notices" in kwargs and isinstance(kwargs["notices"], list):
            notices = kwargs["notices"]
        return notices or []
