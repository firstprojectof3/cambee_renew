
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User as UserModel
from app.schemas import User

router = APIRouter()

@router.post("/user")
def create_user(user: User, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.user_id == user.user_id).first()
    if db_user:
        raise HTTPException(status_code=400, detail="이미 등록된 사용자입니다.")
    
    new_user = UserModel(
        user_id=user.user_id,
        name=user.name,
        student_number=user.student_number,
        gender=user.gender,
        grade=user.grade,
        school=user.school,
        
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "사용자 등록 성공", "user_id": new_user.user_id}


@router.get("/users")
def list_users(db: Session = Depends(get_db)):
    users = db.query(UserModel).all()
    return users


# 사용자 정보 수정 API (테스트용 api)
@router.put("/user/{user_id}")
def update_user(user_id: str, updated_user: User, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="해당 사용자를 찾을 수 없습니다.")
    
    # 기존 값을 새로운 값으로 업데이트
    for field, value in updated_user.dict().items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return {"message": "사용자 정보가 성공적으로 수정되었습니다."}


# 사용자 정보 조회 API (테스트용 api)
@router.get("/user/{user_id}")
def read_user(user_id: str, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="해당 사용자를 찾을 수 없습니다.")
    return db_user
