# app/crud.py
from typing import Any, Dict, List, Optional, Tuple
import json
import re

from sqlalchemy import select, func
from sqlalchemy.orm import Session

# ✅ ORM 모델 경로 정리
from app.models.models import User
from app.schemas import UserCreate


# ---------------- DB ----------------
def create_user(db: Session, user: UserCreate):
    # Pydantic v2 우선(없으면 v1 호환)
    payload = user.model_dump() if hasattr(user, "model_dump") else user.dict()
    db_user = User(**payload)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_id(db: Session, user_id: str):
    return db.query(User).filter(User.user_id == user_id).first()


