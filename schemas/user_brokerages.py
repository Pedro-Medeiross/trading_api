from pydantic import BaseModel, Field
from typing import Optional

class UserBrokeragesBase(BaseModel):
    """Base schema for user brokerage connections with common fields."""
    user_id: int = Field(..., description="ID of the user")
    brokerage_id: int = Field(..., description="ID of the brokerage")
    api_key: Optional[str] = Field(None, description="API key for the brokerage")
    brokerage_username: Optional[str] = Field(None, description="Username for the brokerage")
    brokerage_password: Optional[str] = Field(None, description="Password for the brokerage")


class UserBrokeragesCreate(UserBrokeragesBase):
    """Schema for creating a new user-brokerage connection."""
    pass


class UserBrokeragesUpdate(BaseModel):
    """Schema for updating an existing user-brokerage connection."""
    user_id: Optional[int] = Field(None, description="ID of the user")
    brokerage_id: Optional[int] = Field(None, description="ID of the brokerage")
    api_key: Optional[str] = Field(None, description="API key for the brokerage")
    brokerage_username: Optional[str] = Field(None, description="Username for the brokerage")
    brokerage_password: Optional[str] = Field(None, description="Password for the brokerage")


class UserBrokerages(UserBrokeragesBase):
    """Schema for representing a user-brokerage connection."""
    id: int = Field(..., description="Unique identifier for the user-brokerage connection")

    class Config:
        from_attributes = True
