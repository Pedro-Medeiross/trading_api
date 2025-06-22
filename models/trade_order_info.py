from connection import Base
from sqlalchemy import Column, Integer, String, DateTime, Float

class TradeOrderInfo(Base):
    __tablename__ = "trade_order_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    order_id = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    order_type = Column(String, nullable=False)  # e.g., 'buy', 'sell'
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    status = Column(String, nullable=False)  # e.g., 'open', 'closed', 'canceled'
    date_time = Column(DateTime(timezone=True), nullable=False)
    brokerage_id = Column(Integer, nullable=False)