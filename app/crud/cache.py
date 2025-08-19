# app/crud/cache.py
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.gpt_search_cache import GptSearchCache

def _normalize(q: str) -> str:
    # DB 스키마 최소버전 기준: question_norm 컬럼이 없으므로 파이썬에서 정규화
    return (q or "").strip().lower()

def get_cached_answer(db: Session, question: str):
    
    qn = _normalize(question)
    stmt = (
        select(GptSearchCache)
        .where(func.lower(func.btrim(GptSearchCache.question)) == qn)
        .limit(1)
    )
    row = db.execute(stmt).scalar_one_or_none()
    return row

def upsert_cache(db: Session, question: str, title: str, link: str | None, summary: str | None):
    
    qn = _normalize(question)
    # 먼저 조회
    existing = db.execute(
        select(GptSearchCache).where(func.lower(func.btrim(GptSearchCache.question)) == qn).limit(1)
    ).scalar_one_or_none()

    if existing:
        existing.title = title
        existing.link = link
        existing.summary = summary
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    # 새로 삽입
    item = GptSearchCache(
        question=question,
        title=title,
        link=link,
        summary=summary,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
