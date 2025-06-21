from pydantic import BaseModel
from typing import Optional

class BotOptionsBase(BaseModel):
    bot_status: Optional[bool] = False
    stop_loss: Optional[int] = 0
    stop_win: Optional[int] = 0
    entry_price: Optional[int] = 0
    user_id: Optional[int] = None
    is_demo: Optional[bool] = False
    win_value: Optional[float] = 0.0
    loss_value: Optional[float] = 0.0
    gale_one: Optional[bool] = True
    gale_two: Optional[bool] = True


class BotOptionsUpdate(BotOptionsBase):
    pass


class BotOptionsCreate(BotOptionsBase):
    pass


class BotOptions(BotOptionsBase):
    id: int

    class Config:
        from_attributes = True
