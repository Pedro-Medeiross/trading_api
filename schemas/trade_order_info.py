from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TradeOrderInfoBase(BaseModel):
    user_id: int
    order_id: str
    symbol: str
    order_type: str  # e.g., 'buy', 'sell'
    quantity: float
    price: float
    status: str  # e.g., 'open', 'closed', 'canceled'
    date_time: datetime  # ISO 8601 format, e.g., '2023-10-01T12:00:00Z'
    brokerage_id: int  # ID of the brokerage handling the order


class TradeOrderInfoCreate(TradeOrderInfoBase):
    """
    Schema for creating a new trade order.
    Inherits from TradeOrderInfo to ensure all fields are included.
    """
    pass


class TradeOrderInfoUpdate(TradeOrderInfoBase):
    """
    Schema for updating an existing trade order.
    Inherits from TradeOrderInfoBase to include all fields.
    """
    order_id: Optional[str] = None  # Optional to allow updates without changing the order ID
    status: Optional[str] = None  # Optional to allow status updates without changing other fields
    user_id: Optional[int] = None  # Optional to allow updates without changing the user ID



class TradeOrderInfo(TradeOrderInfoBase):
    """
    Schema for representing a trade order.
    Inherits from TradeOrderInfoBase to include all fields.
    """
    id: int

    class Config:
        from_attributes = True  # Allows compatibility with ORM models like SQLAlchemy