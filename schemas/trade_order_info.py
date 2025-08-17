from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal

class TradeOrderInfoBase(BaseModel):
    """Base schema for trade order information with common fields."""
    user_id: int = Field(..., description="ID of the user who placed the order")
    order_id: str = Field(..., description="Unique order identifier from the brokerage")
    symbol: Optional[str] = Field(None, description="Trading symbol (e.g., 'BTCUSD', 'ETHUSD')")
    order_type: Optional[str] = Field(None, description="Type of order (e.g., 'buy', 'sell')")
    quantity: Optional[float] = Field(None, description="Quantity of the asset being traded")
    price: Optional[float] = Field(None, description="Price at which the order was executed")
    status: Optional[str] = Field(None, description="Status of the order (e.g., 'open', 'closed', 'canceled')")
    date_time: Optional[datetime] = Field(None, description="Date and time when the order was placed")
    brokerage_id: Optional[int] = Field(None, description="ID of the brokerage handling the order")
    pnl: Optional[float] = Field(None, description="Price at which the order was executed")


class TradeOrderInfoCreate(TradeOrderInfoBase):
    """
    Schema for creating a new trade order.
    Inherits from TradeOrderInfoBase to ensure all required fields are included.
    """
    pass


class TradeOrderInfoUpdate(BaseModel):
    """
    Schema for updating an existing trade order.
    Only includes fields that can be updated.
    """
    order_id: Optional[str] = Field(None, description="Unique order identifier from the brokerage")
    status: Optional[str] = Field(None, description="Status of the order (e.g., 'open', 'closed', 'canceled')")
    user_id: Optional[int] = Field(None, description="ID of the user who placed the order")
    symbol: Optional[str] = Field(None, description="Trading symbol (e.g., 'BTCUSD', 'ETHUSD')")
    order_type: Optional[str] = Field(None, description="Type of order (e.g., 'buy', 'sell')")
    quantity: Optional[float] = Field(None, description="Quantity of the asset being traded")
    price: Optional[float] = Field(None, description="Price at which the order was executed")
    date_time: Optional[datetime] = Field(None, description="Date and time when the order was placed")
    brokerage_id: Optional[int] = Field(None, description="ID of the brokerage handling the order")
    pnl: Optional[float] = Field(None, description="Price at which the order was executed")


class OpenTradeOffer(BaseModel):
    """
    Schema for representing an open trade offer.
    """
    trade_pair: str = Field(..., description="Trading pair for the open offer")
    timeframe: str = Field(..., description="Timeframe for the open offer (e.g., '1m', '5m', '1h')")
    direction: str = Field(..., description="Direction of the trade (e.g., 'buy', 'sell')")
    broker: str = Field(..., description="Broker associated with the trade offer")



class CloseTradeOffer(BaseModel):
    """
    Schema for representing a close trade offer.
    """
    result: str = Field(..., description="Result of the close trade offer (e.g., 'success', 'failure')")
    broker: str = Field(..., description="Broker associated with the trade offer")


class TradeOrderInfo(TradeOrderInfoBase):
    """
    Schema for representing a trade order.
    Inherits from TradeOrderInfoBase and adds the database ID.
    """
    id: int = Field(..., description="Unique identifier for the trade order in the database")

    class Config:
        from_attributes = True  # Allows compatibility with ORM models like SQLAlchemy
