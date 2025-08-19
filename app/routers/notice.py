# routers/notice.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, Any, Dict, List

from app.database import get_db
from app.models.models import User, Notice
from app.crud import filter_notices_by_user_info

router = APIRouter(prefix="/notice", tags=["notice"])

def _to_dict(n: Any) -> Dict[str, Any]:
    return {
        "id": getattr(n, "id", None),
        "title": getattr(n, "title", None),
        "category": getattr(n, "category", None),
        "url": getattr(n, "url", None),
    }

@router.get("/all")
def get_all_notices(db: Session = Depends(get_db)):
    return db.query(Notice).all()

@router.get("/filtered")
def get_filtered_notices(
    user_id: str = Query(..., description="테스트 사용자 ID"),
    question: Optional[str] = Query(None, description="사용자 질문"),
    limit: int = Query(200, ge=1, le=1000),
    only_passed: bool = Query(True, description="True면 통과만 반환, False면 dropped도 함께 반환"),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        notices = (
            db.query(Notice)
              .order_by(Notice.created_at.desc())
              .limit(limit)
              .all()
        )
    except Exception:
        notices = db.query(Notice).limit(limit).all()

    if only_passed:
        passed = filter_notices_by_user_info(
            user, notices, question=question, debug=False, return_both=False
        )
        return {
            "user": {
                "user_id": user.user_id,
                "name": user.name,
                "major": user.major,
                "grade": user.grade
            },
            "question": question,
            "count": len(passed),
            "results": [_to_dict(n) for n in passed],
        }
    else:
        passed, dropped = filter_notices_by_user_info(
            user, notices, question=question, debug=False, return_both=True
        )
        return {
            "user": {
                "user_id": user.user_id,
                "name": user.name,
                "major": user.major,
                "grade": user.grade
            },
            "question": question,
            "counts": {"passed": len(passed), "dropped": len(dropped)},
            "passed": [_to_dict(n) for n in passed],
            "dropped": [{"notice": _to_dict(it["notice"]), "reasons": it["reasons"]} for it in dropped],
        }
