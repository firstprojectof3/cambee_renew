# app/schemas.py
from pydantic import BaseModel, constr
from typing import Optional, List

class User(BaseModel):
    user_id: str
    name: str
    student_number: int
    gender: str
    grade: int
    school: str
    income_level: int
    major: str  # 250804 전공 추가

class UserCreate(BaseModel):
    user_id: str
    name: str
    student_number: int
    gender: str
    grade: int
    school: str
    income_level: int
    major: str

    # NOTE: Pydantic v2에서는 orm_mode 경고가 나올 수 있지만, 동작에는 지장 없음.
    class Config:
        orm_mode = True

class Message(BaseModel):
    user_id: str
    message: str
    timestamp: str

class Summary(BaseModel):
    original_message: str
    summary_text: str
    created_at: str

class ChatRequest(BaseModel):
    user_id: constr(pattern=r'^\d+$')  # 숫자로만 이루어진 문자열
    message: str

# ✅ 최소 변경: reply → title 로 교체 (link/summary는 유지)
class ChatResponse(BaseModel):
    title: str
    link: Optional[str] = None
    summary: str

class UserPreference(BaseModel):
    user_id: str
    preferred_topics: Optional[List[str]] = None
    notification_time: Optional[str] = None
    language: Optional[str] = "ko"

class Feedback(BaseModel):
    user_id: str
    message_id: Optional[int] = None
    feedback_text: Optional[str] = None
    rating: Optional[int] = None
    timestamp: Optional[str] = None
