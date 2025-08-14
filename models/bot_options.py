from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from connection import Base

class BotOptions(Base):
    """SQLAlchemy model for bot_options table."""
    __tablename__ = "bot_options"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    bot_status = Column(Integer, default=0, nullable=False)
    stop_loss = Column(Integer, default=0, nullable=False)
    stop_win = Column(Integer, default=0, nullable=False)
    entry_price = Column(Integer, default=0, nullable=False)
    is_demo = Column(Boolean, default=False, nullable=False)
    win_value = Column(Float, default=0.0, nullable=False)
    loss_value = Column(Float, default=0.0, nullable=False)
    gale_one = Column(Boolean, default=True, nullable=False)
    gale_two = Column(Boolean, default=True, nullable=False)
    brokerage_id = Column(Integer, ForeignKey("brokerages.id", ondelete="SET NULL"), nullable=True, index=True)
    gale_one_value = Column(Float, default=0.0, nullable=False)
    gale_two_value = Column(Float, default=0.0, nullable=False)

    def __repr__(self):
        """String representation of the BotOptions object."""
        return f"<BotOptions(id={self.id}, user_id={self.user_id}, status={self.bot_status})>"
