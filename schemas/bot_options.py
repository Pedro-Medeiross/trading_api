from pydantic import BaseModel
from typing import Optional

class BotOptionsBase(BaseModel):
    bot_status: Optional[bool] = False
    stop_loss: Optional[int] = 0
    stop_win: Optional[int] = 0
    entry_price: Optional[int] = 0
    user_id: Optional[int] = None
    api_key: Optional[str] = None
    is_demo: Optional[bool] = False


class BotOptionsUpdate(BotOptionsBase):
    pass


class BotOptionsCreate(BotOptionsBase):
    pass


class BotOptions(BotOptionsBase):
    id: int

    class Config:
        from_attributes = True
