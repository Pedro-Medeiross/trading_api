from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class BrokeragesBase(BaseModel):
    """Base schema for brokerage data with common fields."""
    brokerage_name: str = Field(..., description="Name of the brokerage")
    brokerage_route: str = Field(..., description="API route or endpoint for the brokerage")
    brokerage_icon: str = Field(..., description="URL or path to the brokerage's icon")


class BrokeragesCreate(BrokeragesBase):
    """Schema for creating a new brokerage."""
    pass


class BrokeragesUpdate(BaseModel):
    """Schema for updating an existing brokerage."""
    brokerage_name: Optional[str] = Field(None, description="Name of the brokerage")
    brokerage_route: Optional[str] = Field(None, description="API route or endpoint for the brokerage")
    brokerage_icon: Optional[str] = Field(None, description="URL or path to the brokerage's icon")


class Brokerages(BrokeragesBase):
    """Schema for representing a brokerage."""
    id: int = Field(..., description="Unique identifier for the brokerage")

    class Config:
        from_attributes = True
