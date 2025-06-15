from datetime import datetime
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.trade_order_info import TradeOrderInfo as trade_order_info_model
from schemas import trade_order_info as trade_order_info_schema
from datetime import timezone

def create_trade_order_info(db: Session, trade_order_info: trade_order_info_schema.TradeOrderInfoCreate) -> trade_order_info_model:
    db_trade_order_info = trade_order_info_model(
        order_id=trade_order_info.order_id,
        symbol=trade_order_info.symbol,
        price=trade_order_info.price,
        quantity=trade_order_info.quantity,
        side=trade_order_info.side,
        status=trade_order_info.status,
        date_time=datetime.now(timezone.utc)
    )
    db.add(db_trade_order_info)
    db.commit()
    db.refresh(db_trade_order_info)
    return db_trade_order_info


def get_trade_order_info_by_user_id_today(db: Session, user_id: int) -> list[trade_order_info_model]:
    today = datetime.now(timezone.utc).date()
    return db.query(trade_order_info_model).filter(
        trade_order_info_model.user_id == user_id,
        trade_order_info_model.date_time >= today
    ).all()