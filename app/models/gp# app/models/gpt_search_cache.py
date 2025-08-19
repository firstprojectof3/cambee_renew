# app/models/gpt_search_cache.py
from sqlalchemy import Column, Integer, Text, TIMESTAMP, func
from sqlalchemy.orm import declarative_base


from app.database import Base


class GptSearchCache(Base):
    __tablename__ = "gpt_search_cache"
    __table_args__ = {"schema": "app"}  # ← 우리가 만든 app 스키마

    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    link = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
