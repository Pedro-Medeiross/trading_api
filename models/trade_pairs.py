from connection import Base
from sqlalchemy import String, Column

class TradePair(Base):
    __tablename__ = "trade_pairs"

    id = Column(String, primary_key=True)
    pair_name = Column(String)