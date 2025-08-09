from typing import Optional
from pydantic import BaseModel, Field, validator


class SiteOptionsBase(BaseModel):
    """Schema for site options."""
    key_name: str = Field(..., description="Name of the site option")
    key_value: str = Field(..., description="Value of the site option")
    type: str = Field(..., description="Type of the site option")
    description: Optional[str] = Field(None, description="Description of the site option")


class SiteOptionsUpdate(BaseModel):
    """Schema for updating site options."""
    key_name: Optional[str] = Field(None, description="Name of the site option")
    key_value: Optional[str] = Field(None, description="Value of the site option")
    type: Optional[str] = Field(None, description="Type of the site option")
    description: Optional[str] = Field(None, description="Description of the site option")


class SiteOptions(SiteOptionsBase):
    """Schema for representing site options."""
    id: int = Field(..., description="Unique identifier for the site options")

    class Config:
        from_attributes = True