from sqlalchemy import Boolean, Column, Integer, String, DateTime
from connection import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    brokerage_name = Column(String(250))
    brokerage_route = Column(String(250))
    brokerage_icon = Column(String(250))