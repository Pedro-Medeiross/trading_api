from typing import Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime


class UserBase(BaseModel):
    """Base schema for user data with common fields."""
    complete_name: str = Field(..., description="User's full name")
    email: str = Field(..., description="User's email address")

    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v.lower()


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., description="User's password")
    is_superuser: Optional[bool] = Field(None, description="Whether the user has superuser privileges")


class UserUpdate(BaseModel):
    """Schema for updating an existing user."""
    complete_name: Optional[str] = Field(None, description="User's full name")
    email: Optional[str] = Field(None, description="User's email address")
    phone_number: Optional[str] = Field(None, description="User's phone number")
    password: Optional[str] = Field(None, description="User's password")


class User(UserBase):
    """Schema for representing a user."""
    id: int = Field(..., description="Unique identifier for the user")
    last_login: Optional[datetime] = Field(None, description="Timestamp of the user's last login")
    is_superuser: bool = Field(False, description="Whether the user has superuser privileges")
    is_active: bool = Field(False, description="Whether the user account is active")
    activated_at: Optional[datetime] = Field(None, description="Timestamp when the user account was activated")
    current_plan: Optional[str] = Field(None, description="User's current subscription plan")
    phone_number: Optional[str] = Field(None, description="User's phone number")

    class Config:
        from_attributes = True
