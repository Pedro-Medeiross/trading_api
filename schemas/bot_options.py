from pydantic import BaseModel
from typing import Optional

class BotOptionsBase(BaseModel):
    bot_status: Optional[int] = None
    stop_loss: Optional[int] = None
    stop_win: Optional[int] = None
    entry_price: Optional[int] = None
    user_id: Optional[int] = None
    is_demo: Optional[bool] = None
    win_value: Optional[float] = None
    loss_value: Optional[float] = None
    gale_one: Optional[bool] = None
    gale_two: Optional[bool] = None
    brokerage_id: Optional[int] = None


class BotOptionsUpdate(BotOptionsBase):
    pass


class BotOptionsCreate(BotOptionsBase):
    pass


class BotOptions(BotOptionsBase):
    id: int

    class Config:
        from_attributes = True
