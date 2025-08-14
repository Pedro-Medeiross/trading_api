from pydantic import BaseModel, Field
from typing import Optional

class BotOptionsBase(BaseModel):
    """Base schema for bot options with common fields."""
    bot_status: Optional[int] = Field(None, description="Status of the bot (0=inactive, 1=active)")
    stop_loss: Optional[int] = Field(None, description="Stop loss value in points")
    stop_win: Optional[int] = Field(None, description="Stop win value in points")
    entry_price: Optional[int] = Field(None, description="Entry price for the bot")
    user_id: Optional[int] = Field(None, description="ID of the user who owns this bot")
    is_demo: Optional[bool] = Field(None, description="Whether this bot is running in demo mode")
    win_value: Optional[float] = Field(None, description="Win value for profit calculation")
    loss_value: Optional[float] = Field(None, description="Loss value for loss calculation")
    gale_one: Optional[bool] = Field(None, description="Whether first gale is enabled")
    gale_two: Optional[bool] = Field(None, description="Whether second gale is enabled")
    brokerage_id: Optional[int] = Field(None, description="ID of the brokerage used by this bot")
    gale_one_value: Optional[float] = Field(None, description="Value for first gale")
    gale_two_value: Optional[float] = Field(None, description="Value for second gale")


class BotOptionsCreate(BotOptionsBase):
    """Schema for creating new bot options."""
    user_id: int = Field(..., description="ID of the user who owns this bot")


class BotOptionsUpdate(BaseModel):
    """Schema for updating existing bot options."""
    bot_status: Optional[int] = Field(None, description="Status of the bot (0=inactive, 1=active)")
    stop_loss: Optional[int] = Field(None, description="Stop loss value in points")
    stop_win: Optional[int] = Field(None, description="Stop win value in points")
    entry_price: Optional[int] = Field(None, description="Entry price for the bot")
    is_demo: Optional[bool] = Field(None, description="Whether this bot is running in demo mode")
    win_value: Optional[float] = Field(None, description="Win value for profit calculation")
    loss_value: Optional[float] = Field(None, description="Loss value for loss calculation")
    gale_one: Optional[bool] = Field(None, description="Whether first gale is enabled")
    gale_two: Optional[bool] = Field(None, description="Whether second gale is enabled")
    brokerage_id: Optional[int] = Field(None, description="ID of the brokerage used by this bot")
    gale_one_value: Optional[float] = Field(None, description="Value for first gale")
    gale_two_value: Optional[float] = Field(None, description="Value for second gale")


class BotOptions(BotOptionsBase):
    """Schema for representing bot options."""
    id: int = Field(..., description="Unique identifier for the bot options")

    class Config:
        from_attributes = True
