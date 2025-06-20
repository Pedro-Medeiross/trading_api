from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float
from connection import Base


class UserBrokerages(Base):
    __tablename__ = "user_brokerages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    brokerage_id = Column(Integer, nullable=False)
    api_key = Column(nullable=True)
    brokerage_username = Column(nullable=True)
    brokerage_password = Column(nullable=True)