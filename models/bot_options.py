from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float
from connection import Base

class BotOptions(Base):
    __tablename__ = "bot_options"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    bot_status = Column(Boolean, default=True)
    stop_loss = Column(Integer, default=0)
    stop_win = Column(Integer, default=0)
    entry_price = Column(Integer, default=0)
    api_key = Column(String, nullable=True)
    is_demo = Column(Boolean, default=False)
    win_value = Column(Float, default=0.0)
    loss_value = Column(Float, default=0.0)
    