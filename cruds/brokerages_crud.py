from datetime import datetime
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import brokerages as models_brokerages
from schemas import brokerages as schemas_brokerages
import pytz


def get_brokerage_by_id(db: Session, brokerage_id: int):
    return db.query(models_brokerages.Brokerages).filter(models_brokerages.Brokerages.id == brokerage_id).first()


def get_brokerages(db: Session, skip: int = 0, limit: int = 1000000):
    return db.query(models_brokerages.Brokerages).offset(skip).limit(limit).all()


def get_brokerages_by_user_id(db: Session, user_id: int):
    return db.query(models_brokerages.Brokerages).filter(models_brokerages.Brokerages.user_id == user_id).all()


def create_brokerage(db: Session, brokerage: schemas_brokerages.BrokeragesCreate):
    db_brokerage = models_brokerages.Brokerages(
        brokerage_name=brokerage.brokerage_name,
        brokerage_route=brokerage.brokerage_route,
        brokerage_icon=brokerage.brokerage_icon,
    )
    db.add(db_brokerage)
    db.commit()
    db.refresh(db_brokerage)
    return db_brokerage


def update_brokerage(db: Session, brokerage_id: int, brokerage: schemas_brokerages.BrokeragesUpdate):
    db_brokerage = get_brokerage_by_id(db, brokerage_id)
    if not db_brokerage:
        raise HTTPException(status_code=404, detail="Corretora não encontrada")
    
    update_data = brokerage.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_brokerage, field, value)

    db.commit()
    db.refresh(db_brokerage)
    return db_brokerage



