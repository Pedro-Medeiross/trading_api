from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from connection import Base

class Brokerages(Base):
    """SQLAlchemy model for brokerages table."""
    __tablename__ = "brokerages"

    id = Column(Integer, primary_key=True, index=True)
    brokerage_name = Column(String(250), nullable=False)
    brokerage_route = Column(String(250), nullable=False)
    brokerage_icon = Column(String(250), nullable=False)

    # Relationships
    user_brokerages = relationship("UserBrokerages", back_populates="brokerage", cascade="all, delete-orphan")
    bot_options = relationship("BotOptions", backref="brokerage")
    trade_orders = relationship("TradeOrderInfo", backref="brokerage")

    def __repr__(self):
        """String representation of the Brokerages object."""
        return f"<Brokerages(id={self.id}, name='{self.brokerage_name}')>"
