from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class UserBase(BaseModel):
    complete_name: str
    email: str


class UserCreate(UserBase):
    password: str
    is_superuser: Optional[bool]


class UserUpdate(UserBase):
    phone_number: Optional[str] = None
    password: Optional[str] = None


class User(UserBase):
    id: int
    last_login: Optional[datetime]
    is_superuser: Optional[bool] = False
    is_active: Optional[bool] = False
    activated_at: Optional[datetime]
    current_plan: Optional[str]
    phone_number: Optional[str]

    class Config:
        from_attributes = True
