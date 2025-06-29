from pydantic import BaseModel, Field
from typing import Optional


class Token(BaseModel):
    """Schema for authentication tokens."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(..., description="Type of token (e.g., 'bearer')")


class TokenData(BaseModel):
    """Schema for token payload data."""
    email: Optional[str] = Field(None, description="Email address of the authenticated user")
