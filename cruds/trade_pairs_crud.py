import logging
from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from schemas import trade_pairs as schemas_trade_pairs
from models import trade_pairs as models_trade_pairs



async def create_trade_pair(db: Session, trade_pair: schemas_trade_pairs.TradePairCreate) -> models_trade_pairs.TradePair:
    db_trade_pair = models_trade_pairs.TradePair(**trade_pair.dict())
    db.add(db_trade_pair)
    try:
        db.commit()
        db.refresh(db_trade_pair)
    except SQLAlchemyError as e:
        logging.error(f"Error creating trade pair: {e}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating trade pair")
    return db_trade_pair



async def get_all_trade_pairs(db: Session, skip: int = 0, limit: int = 100) -> List[models_trade_pairs.TradePair]:
    return db.query(models_trade_pairs.TradePair).offset(skip).limit(limit).all()



async def get_trade_pair_by_id(db: Session, trade_pair_id: str) -> Optional[models_trade_pairs.TradePair]:
    return db.query(models_trade_pairs.TradePair).filter(models_trade_pairs.TradePair.id == trade_pair_id).first()


async def update_trade_pair(db: Session, trade_pair_id: str, trade_pair_update: schemas_trade_pairs.TradePairUpdate) -> Optional[models_trade_pairs.TradePair]:
    db_trade_pair = await get_trade_pair_by_id(db, trade_pair_id)
    if not db_trade_pair:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trade pair not found")

    for key, value in trade_pair_update.dict(exclude_unset=True).items():
        setattr(db_trade_pair, key, value)

    db.add(db_trade_pair)
    try:
        db.commit()
        db.refresh(db_trade_pair)
    except SQLAlchemyError as e:
        logging.error(f"Error updating trade pair: {e}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating trade pair")
    return db_trade_pair



async def delete_trade_pair(db: Session, trade_pair_id: str) -> Optional[models_trade_pairs.TradePair]:
    db_trade_pair = await get_trade_pair_by_id(db, trade_pair_id)
    if not db_trade_pair:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trade pair not found")

    db.delete(db_trade_pair)
    try:
        db.commit()
    except SQLAlchemyError as e:
        logging.error(f"Error deleting trade pair: {e}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting trade pair")
    return db_trade_pair