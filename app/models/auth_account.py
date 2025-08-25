# app/models/auth_account.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

class AuthAccount(Base):
    __tablename__ = "auth_accounts"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    user_id = Column(String(64), index=True, nullable=False)  # users.user_id 매핑
    created_at = Column(DateTime(timezone=True), server_default=func.now())
