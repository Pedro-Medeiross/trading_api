from connection import Base
from sqlalchemy import String, Column, Integer

class TradePair(Base):
    __tablename__ = "trade_pairs"

    id = Column(Integer, primary_key=True, index=True)
    pair_name = Column(String)