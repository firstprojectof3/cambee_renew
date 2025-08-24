# app/routers/preference.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import UserPreference as PrefModel
from app.schemas import UserPreference as PrefSchema

router = APIRouter()

def _to_csv(arr):  # ["학사","장학"] -> "학사,장학"
    return ",".join(arr) if arr else None

def _to_list(csv):  # "학사,장학" -> ["학사","장학"]
    return [s for s in (csv or "").split(",") if s] if csv else []

@router.post("/preference")
def upsert_preference(pref: PrefSchema, db: Session = Depends(get_db)):
    db_pref = db.query(PrefModel).filter(PrefModel.user_id == pref.user_id).first()
    if db_pref:
        db_pref.preferred_topics = _to_csv(pref.preferred_topics)
        db_pref.notification_time = pref.notification_time
        db_pref.language = pref.language or "ko"
    else:
        db_pref = PrefModel(
            user_id=pref.user_id,
            preferred_topics=_to_csv(pref.preferred_topics),
            notification_time=pref.notification_time,
            language=pref.language or "ko",
        )
        db.add(db_pref)
    db.commit()
    db.refresh(db_pref)
    return {
        "user_id": db_pref.user_id,
        "preferred_topics": _to_list(db_pref.preferred_topics),
        "notification_time": db_pref.notification_time,
        "language": db_pref.language,
    }

@router.get("/preference/{user_id}")
def get_preference(user_id: str, db: Session = Depends(get_db)):
    db_pref = db.query(PrefModel).filter(PrefModel.user_id == user_id).first()
    if not db_pref:
        raise HTTPException(status_code=404, detail="설정 없음")
    return {
        "user_id": db_pref.user_id,
        "preferred_topics": _to_list(db_pref.preferred_topics),
        "notification_time": db_pref.notification_time,
        "language": db_pref.language,
    }
