from pydantic import BaseModel
from typing import Optional

class BotOptionsBase(BaseModel):
    bot_status: Optional[bool]
    stop_loss: Optional[int]
    stop_win: Optional[int]
    entry_price: Optional[int]
    user_id: Optional[int]
    is_demo: Optional[bool]
    win_value: Optional[float]
    loss_value: Optional[float]
    gale_one: Optional[bool]
    gale_two: Optional[bool]


class BotOptionsUpdate(BotOptionsBase):
    pass


class BotOptionsCreate(BotOptionsBase):
    pass


class BotOptions(BotOptionsBase):
    id: int

    class Config:
        from_attributes = True
