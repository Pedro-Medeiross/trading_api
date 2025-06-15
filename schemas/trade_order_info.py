from pydantic import BaseModel
from datetime import datetime

class TradeOrderInfoBase(BaseModel):
    user_id: int
    order_id: str
    symbol: str
    order_type: str  # e.g., 'buy', 'sell'
    quantity: float
    price: float
    status: str  # e.g., 'open', 'closed', 'canceled'
    date_time: datetime  # ISO 8601 format, e.g., '2023-10-01T12:00:00Z'


class TradeOrderInfoCreate(TradeOrderInfoBase):
    """
    Schema for creating a new trade order.
    Inherits from TradeOrderInfo to ensure all fields are included.
    """
    pass


class TradeOrderInfoUpdate(TradeOrderInfoBase):
    user_id: int | None
    order_id: str | None
    symbol: str | None
    order_type: str | None  # e.g., 'buy', 'sell'
    quantity: float | None
    price: float | None
    status: str | None  # e.g., 'open', 'closed', 'canceled'



class TradeOrderInfo(TradeOrderInfoBase):
    """
    Schema for representing a trade order.
    Inherits from TradeOrderInfoBase to include all fields.
    """
    id: int

    class Config:
        from_attributes = True  # Allows compatibility with ORM models like SQLAlchemy