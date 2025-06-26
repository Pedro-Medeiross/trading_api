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
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    activated_at = Column(DateTime, nullable=True)

