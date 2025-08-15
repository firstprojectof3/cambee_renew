from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schema_models import Feedback
from app.database import get_db

router = APIRouter()

@router.get("/feedback")
def get_all_feedback(db: Session = Depends(get_db)):
    return db.query(Feedback).all()