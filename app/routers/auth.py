# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import uuid4
from app.database import get_db
from app.models.models import User as UserModel
from app.models.auth_account import AuthAccount
from app.schemas import AuthRegister, AuthLogin
from app.auth_utils import hash_pw, verify_pw

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(body: AuthRegister, db: Session = Depends(get_db)):
    if db.query(AuthAccount).filter_by(email=body.email).first():
        raise HTTPException(409, "이미 가입된 이메일입니다.")
    # 유저 생성(없으면)
    new_user = UserModel(
        user_id=f"u{uuid4().hex[:8]}",
        name=body.name,
        student_number=None, gender=None, grade=None, school=None,
        income_level=None, major=None
    )
    db.add(new_user); db.flush()  # id/user_id 확보
    # 계정 생성
    acc = AuthAccount(email=body.email, password_hash=hash_pw(body.password), user_id=new_user.user_id)
    db.add(acc); db.commit(); db.refresh(new_user)
    return {"id": new_user.id, "user_id": new_user.user_id, "email": body.email, "name": new_user.name}

@router.post("/login")
def login(body: AuthLogin, db: Session = Depends(get_db)):
    acc = db.query(AuthAccount).filter_by(email=body.email).first()
    if not acc or not verify_pw(body.password, acc.password_hash):
        raise HTTPException(401, "이메일 또는 비밀번호가 올바르지 않습니다.")
    u = db.query(UserModel).filter_by(user_id=acc.user_id).first()
    return {"message":"ok", "user": {"id": u.id, "user_id": u.user_id, "email": acc.email, "name": u.name}}
