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
        order_type=trade_order_info.order_type,
        quantity=trade_order_info.quantity,
        price=trade_order_info.price,
        status=trade_order_info.status,
        date_time=datetime.now(timezone.utc),
        brokerage_id=trade_order_info.brokerage_id,
    )
    db.add(db_trade_order_info)
    db.commit()
    db.refresh(db_trade_order_info)
    return db_trade_order_info


def get_trade_order_info_by_user_id_today(db: Session, user_id: int, brokerage_id: int) -> list[trade_order_info_model]:
    today = datetime.now(timezone.utc).date()
    return db.query(trade_order_info_model).filter(
        trade_order_info_model.user_id == user_id,
        trade_order_info_model.date_time >= today,
        trade_order_info_model.brokerage_id == brokerage_id
    ).all()


def update_trade_order_info_by_id(db: Session, trade_order_info: trade_order_info_schema.TradeOrderInfoUpdate) -> Optional[trade_order_info_model]:
    db_trade_order_info = db.query(trade_order_info_model).filter(
        trade_order_info_model.id == trade_order_info.order_id and trade_order_info_model.user_id == trade_order_info.user_id
    ).first()
    
    if not db_trade_order_info:
        raise HTTPException(status_code=404, detail="Trade order info not found")
    
    if trade_order_info.status is not None:
        db_trade_order_info.status = trade_order_info.status
    
    db.commit()
    db.refresh(db_trade_order_info)
    return db_trade_order_info