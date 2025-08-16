from typing import Optional
from pydantic import BaseModel, Field, validator


class TradePairBase(BaseModel):
    pair_name: str = Field(..., description="The name of the trade pair")


class TradePairCreate(TradePairBase):
    pass


class TradePairUpdate(TradePairBase):
    pass


class TradePair(TradePairBase):
    id: int = Field(..., description="The unique identifier of the trade pair")

    class Config:
        from_attributes = True