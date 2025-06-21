from pydantic import BaseModel
from typing import Optional

class UserBrokeragesBase(BaseModel):
    user_id: int
    brokerage_id: int
    api_key: Optional[str]
    brokerage_username: Optional[str]
    brokerage_password: Optional[str]

class UserBrokeragesCreate(UserBrokeragesBase):
    pass

class UserBrokeragesUpdate(UserBrokeragesBase):
    pass

class UserBrokerages(UserBrokeragesBase):
    id: int

    class Config:
        from_attributes = True
