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
    major: str #250804 전공 추가 
    
class UserCreate(BaseModel):
    user_id: str
    name: str
    student_number: int
    gender: str
    grade: int
    school: str
    income_level: int
    major: str
    
    
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

class ChatResponse(BaseModel):
    reply: str
    timestamp: str

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
