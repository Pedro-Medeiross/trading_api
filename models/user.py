from sqlalchemy import Boolean, Column, Integer, String, DateTime
from connection import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    complete_name = Column(String(250))
    email = Column(String(100), unique=True, index=True)
    password = Column(String(150))
    is_superuser = Column(Boolean(), default=False)
    is_active = Column(Boolean(), default=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    activated_at = Column(DateTime(timezone=True), nullable=True)
    current_plan = Column(String(100), nullable=True)
