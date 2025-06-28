from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class BrokeragesBase(BaseModel):
    brokerage_name: str
    brokerage_route: str
    brokerage_icon: str


class UserCreate(BrokeragesBase):
    pass


class UserUpdate(BrokeragesBase):
    pass


class User(BrokeragesBase):
    id: int

    class Config:
        from_attributes = True
