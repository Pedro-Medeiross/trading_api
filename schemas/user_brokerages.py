from pydantic import BaseModel
from typing import Optional

class UserBrokeragesBase(BaseModel):
    user_id: int
    brokerage_id: int
    api_key: Optional[str] = None
    brokerage_username: Optional[str] = None
    brokerage_password: Optional[str] = None

class UserBrokeragesCreate(UserBrokeragesBase):
    pass

class UserBrokeragesUpdate(UserBrokeragesBase):
    pass

class Brokerages(UserBrokeragesBase):
    id: int

    class Config:
        from_attributes = True
