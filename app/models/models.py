# app/models/models.py
from __future__ import annotations

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


# 대화 로그
class ChatLog(Base):
    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(64), index=True)
    message = Column(Text)  # 질문은 길 수 있어 Text 권장
    summary = Column(Text)  # 요약/응답도 길 수 있어 Text
    # DB 서버 시간이 기본값, timezone-aware
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)


# 사용자 선호
class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(64), index=True)
    preferred_topics = Column(String(256))  # 예: "공지,학식"
    notification_time = Column(String(32), nullable=True)
    language = Column(String(8), default="ko")



# 사용자
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(64), unique=True, index=True)  # 외부 식별자
    name = Column(String(128))
    student_number = Column(Integer, index=True)
    gender = Column(String(16))
    grade = Column(Integer, index=True)
    school = Column(String(128))
    income_level = Column(Integer, index=True)  # 250729 소득분위
    major = Column(String(128), index=True)     # 250804 전공


