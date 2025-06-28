from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class BrokeragesBase(BaseModel):
    brokerage_name: str
    brokerage_route: str
    brokerage_icon: str


class BrokeragesCreate(BrokeragesBase):
    pass


class BrokeragesUpdate(BrokeragesBase):
    pass


class Brokerage(BrokeragesBase):
    id: int

    class Config:
        from_attributes = True
