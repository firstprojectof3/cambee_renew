# app/routers/crawl_admin.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session

from app.services.crawl_pipeline import crawl_and_store
from app.database import get_db  # 네 프로젝트에 이미 있는 의존성

router = APIRouter()

class RunReq(BaseModel):
    list_url: HttpUrl
    limit: int = 30

@router.post("/crawl/run")
def crawl_run(req: RunReq, db: Session = Depends(get_db)):
    result = crawl_and_store(db, str(req.list_url), limit=req.limit)
    return result
