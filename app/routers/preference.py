from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schema_models import UserPreference
from database import get_db

router = APIRouter()

@router.get("/preferences")
def get_user_preferences(db: Session = Depends(get_db)):
    return db.query(UserPreference).all()