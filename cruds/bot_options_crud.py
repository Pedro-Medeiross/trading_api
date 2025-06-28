from models.bot_options import BotOptions
from schemas import bot_options as schemas_bot_options
from models import bot_options as models_bot_options
from sqlalchemy.orm import Session


def get_bot_options_by_user_id(db: Session, user_id: int, brokerage_id: int) -> BotOptions:
    return db.query(BotOptions).filter(BotOptions.user_id == user_id).first()


def get_bot_options_by_user_id_and_brokerage_id(db: Session, user_id: int, brokerage_id: int) -> BotOptions:
    return db.query(BotOptions).filter(BotOptions.user_id == user_id, BotOptions.brokerage_id == brokerage_id).first()


def create_bot_options(db: Session, bot_options: schemas_bot_options.BotOptionsCreate) -> BotOptions:
    db_bot_options = models_bot_options.BotOptions(
        user_id=bot_options.user_id,
        bot_status=bot_options.bot_status,
        stop_loss=bot_options.stop_loss,
        stop_win=bot_options.stop_win,
        entry_price=bot_options.entry_price,
        is_demo=bot_options.is_demo,
        win_value=bot_options.win_value,
        loss_value=bot_options.loss_value,
        gale_one=bot_options.gale_one,
        gale_two=bot_options.gale_two,    
        )
    db.add(db_bot_options)
    db.commit()
    db.refresh(db_bot_options)
    return db_bot_options


def update_bot_options(db: Session, user_id: int, brokerage_id:int, bot_options: schemas_bot_options.BotOptionsUpdate) -> BotOptions:
    db_bot_options = get_bot_options_by_user_id_and_brokerage_id(db, user_id, brokerage_id)
    if not db_bot_options:
        raise ValueError("Bot options not found for the given user ID")
    
    update_data = bot_options.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_bot_options, field, value)
    
    db.commit()
    db.refresh(db_bot_options)
    return db_bot_options


