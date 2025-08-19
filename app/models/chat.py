
from pydantic import BaseModel

class ChatRequest(BaseModel):
    user_id:str
    message:str
    major:str
    grade:int
    school:str
    income_level:int

# 추가
class ChatResponseItem(BaseModel):
    title:str
    link:str
    summary:str

# 적용
class ChatResponse(BaseModel):
    results:list[ChatResponseItem]
    timestamp: str

class User(BaseModel):
    user_id:str
    name:str
    student_number:int
    gender:str
    grade:int
    school:str
    income_level : int
    major: str
    id:int

class Message(BaseModel):
    user_id:str
    message:str
    timestamp: str

class Summary(BaseModel):
    original_message: str
    summary_text: str
    created_at: str

