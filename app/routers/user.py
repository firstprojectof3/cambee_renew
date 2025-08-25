# app/routers/user.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User as UserModel
from app.schemas import User as UserSchema
from typing import Any

# ✅ 라우터 prefix/태그
router = APIRouter(prefix="/users", tags=["users"])

# ✅ 생성
@router.post("", status_code=status.HTTP_201_CREATED)
def create_user(user: UserSchema, db: Session = Depends(get_db)):
    if db.query(UserModel).filter(UserModel.user_id == user.user_id).first():
        raise HTTPException(status_code=409, detail="이미 등록된 사용자입니다.")
    new_user = UserModel(
        user_id=user.user_id,
        name=user.name,
        student_number=user.student_number,
        gender=user.gender,
        grade=user.grade,
        school=user.school,
        income_level=getattr(user, "income_level", None),
        major=getattr(user, "major", None),
    )
    db.add(new_user); db.commit(); db.refresh(new_user)
    return {"message": "사용자 등록 성공", "user_id": new_user.user_id, "id": new_user.id}

# ✅ 목록
@router.get("")
def list_users(db: Session = Depends(get_db)):
    return db.query(UserModel).all()

# ✅ 단건 조회
@router.get("/{user_id}")
def read_user(user_id: str, db: Session = Depends(get_db)):
    u = db.query(UserModel).filter(UserModel.user_id == user_id).first()
    if not u: raise HTTPException(status_code=404, detail="해당 사용자를 찾을 수 없습니다.")
    return u

# ✅ 부분수정(None 덮어쓰기 방지)
from app.schemas import User as UserSchema, UserUpdate  # ← import 추가

@router.put("/{user_id}")
def update_user(user_id: str, updated_user: UserUpdate, db: Session = Depends(get_db)):
    u = db.query(UserModel).filter(UserModel.user_id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="해당 사용자를 찾을 수 없습니다.")

    # v2/v1 호환 + 허용 필드만 반영
    try:
        data = updated_user.model_dump(exclude_unset=True)
    except Exception:
        data = updated_user.dict(exclude_unset=True)

    allowed = {"name","student_number","gender","grade","school","income_level","major"}
    for k, v in data.items():
        if k in allowed:
            setattr(u, k, v)

    db.commit(); db.refresh(u)
    return {"message":"사용자 정보가 성공적으로 수정되었습니다.","user_id":u.user_id}
