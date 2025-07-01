from connection import Base
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Index
from sqlalchemy.orm import relationship

class TradeOrderInfo(Base):
    """SQLAlchemy model for trade_order_info table."""
    __tablename__ = "trade_order_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    order_id = Column(String, nullable=False, index=True)
    symbol = Column(String, nullable=False, index=True)
    order_type = Column(String, nullable=False)  # e.g., 'buy', 'sell'
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    status = Column(String, nullable=False, index=True)  # e.g., 'open', 'closed', 'canceled'
    date_time = Column(DateTime(timezone=True), nullable=False, index=True)
    brokerage_id = Column(Integer, ForeignKey("brokerages.id", ondelete="CASCADE"), nullable=False, index=True)
    pnl = Column(Float, nullable=True)

    # Create a composite index for common query patterns
    __table_args__ = (
        Index('idx_trade_user_status', 'user_id', 'status'),
        Index('idx_trade_user_date', 'user_id', 'date_time'),
    )

    def __repr__(self):
        """String representation of the TradeOrderInfo object."""
        return f"<TradeOrderInfo(id={self.id}, order_id='{self.order_id}', symbol='{self.symbol}', status='{self.status}')>"
