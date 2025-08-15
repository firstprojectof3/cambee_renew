# models.py
from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base
from datetime import datetime

class ChatLog(Base):
    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    message = Column(String)
    summary = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)


class UserPreference(Base):
    __tablename__ = "user_preferences"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    preferred_topics = Column(String)  # 예: "공지,학식"
    notification_time = Column(String, nullable=True)
    language = Column(String, default="ko")

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    message_id = Column(Integer, nullable=True)
    feedback_text = Column(String, nullable=True)
    rating = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    name = Column(String)
    student_number = Column(Integer)
    gender = Column(String)
    grade = Column(Integer)
    school = Column(String)
    income_level = Column(Integer) # 250729 소득분위 필드 추가
    major = Column(String)  # 250804 User 모델에 전공 추가
    
    
class Notice(Base):
    __tablename__ = "notices"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String)  # 장학, 학사, 등록금 등 카테고리 종류
    title = Column(String)
    content = Column(String)
    url = Column(String)
    date = Column(DateTime)
    
     # 250807 필터링용 필드 추가
    target_grade = Column(Integer, nullable=True)    
    target_major = Column(String, nullable=True)     
    target_student_number = Column(Integer, nullable=True)     

    