from pydantic import BaseModel, constr
from typing import Optional, List
from datetime import datetime

# ✅ User 모델 통합
class User(BaseModel):
    user_id: str
    name: str
    student_number: int
    gender: str
    grade: int
    school: str
    income_level: int
    major: str
    id: Optional[int] = None  # DB에서 자동 생성될 수 있으므로 Optional 처리

class UserCreate(User):
    class Config:
        orm_mode = True

# ✅ Message 모델 통합
class Message(BaseModel):
    user_id: str
    message: str
    timestamp: str

# ✅ Summary 모델 통합
class Summary(BaseModel):
    original_message: str
    summary_text: str
    created_at: str

# ✅ ChatRequest 통합
class ChatRequest(BaseModel):
    user_id: constr(regex=r'^\d+$')
    message: constr(min_length=1)
    class Config:
        orm_mode = True

# ✅ ChatResponse 구조 통일
class ChatResponseItem(BaseModel):
    title: str
    link: Optional[str] = None
    summary: str
    class Config:
        orm_mode = True

class ChatResponse(BaseModel):
    results: List[ChatResponseItem]
    timestamp: datetime
    title: Optional[str] = None
    link: Optional[str] = None
    summary: Optional[str] = None

    class Config:
        orm_mode = True


# ✅ 기타 모델
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
