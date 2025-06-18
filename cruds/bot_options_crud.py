from models.bot_options import BotOptions
from schemas import bot_options as schemas_bot_options
from models import bot_options as models_bot_options
from sqlalchemy.orm import Session
import base64


def get_bot_options_by_user_id(db: Session, user_id: int) -> BotOptions:
    return db.query(BotOptions).filter(BotOptions.user_id == user_id).first()


def get_api_key_by_user_id(db: Session, user_id: int) -> str:
    bot_options = get_bot_options_by_user_id(db, user_id)
    if not bot_options or not bot_options.api_key:
        raise ValueError("API key not found for the given user ID")
    return bot_options.api_key


def create_bot_options(db: Session, bot_options: schemas_bot_options.BotOptionsCreate) -> BotOptions:
    db_bot_options = models_bot_options.BotOptions(
        user_id=bot_options.user_id,
        bot_status=bot_options.bot_status,
        stop_loss=bot_options.stop_loss,
        stop_win=bot_options.stop_win,
        entry_price=bot_options.entry_price,
        api_key=bot_options.api_key
    )
    db.add(db_bot_options)
    db.commit()
    db.refresh(db_bot_options)
    return db_bot_options


def update_bot_options(db: Session, user_id: int, bot_options: schemas_bot_options.BotOptionsUpdate) -> BotOptions:
    db_bot_options = get_bot_options_by_user_id(db, user_id)
    if not db_bot_options:
        raise ValueError("Bot options not found for the given user ID")
    if bot_options.bot_status is not None:
        db_bot_options.bot_status = bot_options.bot_status
    if bot_options.stop_loss is not None:
        db_bot_options.stop_loss = bot_options.stop_loss
    if bot_options.stop_win is not None:
        db_bot_options.stop_win = bot_options.stop_win
    if bot_options.entry_price is not None:
        db_bot_options.entry_price = bot_options.entry_price
    if bot_options.api_key is not None:
        hashed_api_key = base64.b64encode(bot_options.api_key.encode()).decode()
        db_bot_options.api_key = hashed_api_key
    if bot_options.is_demo is not None:
        db_bot_options.is_demo = bot_options.is_demo
    if bot_options.win_value is not None:
        db_bot_options.win_value = bot_options.win_value
    if bot_options.loss_value is not None:
        db_bot_options.loss_value = bot_options.loss_value
    db.commit()
    db.refresh(db_bot_options)
    return db_bot_options


