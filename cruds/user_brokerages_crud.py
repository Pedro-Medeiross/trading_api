import base64
from datetime import datetime
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.user_brokerages import UserBrokerages as UserBrokeragesModel
from schemas import user_brokerages as user_brokerages_schema
from datetime import timezone


def get_user_brokerage(db: Session, user_id: int, brokerage_id: int) -> Optional[UserBrokeragesModel]:
    db_user_brokerage = db.query(UserBrokeragesModel).filter(
        UserBrokeragesModel.user_id == user_id,
        UserBrokeragesModel.brokerage_id == brokerage_id
    ).first()
    if not db_user_brokerage:
        raise HTTPException(status_code=404, detail="User Brokerage not found")
    return db_user_brokerage


def create_user_brokerage(db: Session, user_brokerage: user_brokerages_schema.UserBrokeragesCreate) -> UserBrokeragesModel:
    db_user_brokerage = UserBrokeragesModel(
        user_id=user_brokerage.user_id,
        brokerage_id=user_brokerage.brokerage_id,
        api_key=user_brokerage.api_key,
        brokerage_username=user_brokerage.brokerage_username,
        brokerage_password=user_brokerage.brokerage_password, )
    db.add(db_user_brokerage)
    db.commit()
    db.refresh(db_user_brokerage)
    return db_user_brokerage


def update_user_brokerage(db: Session, user_id: int, brokerage_id: int, user_brokerage: user_brokerages_schema.UserBrokeragesUpdate) -> UserBrokeragesModel:
    db_user_brokerage = get_user_brokerage(db, user_id, brokerage_id)
    if user_brokerage.api_key is not None:
        db_user_brokerage.api_key = user_brokerage.api_key
    if user_brokerage.brokerage_username is not None:
        db_user_brokerage.brokerage_username = user_brokerage.brokerage_username
    if user_brokerage.brokerage_password is not None:
        hashed_brokerage_password = base64.b64encode(user_brokerage.brokerage_password.encode()).decode()
        db_user_brokerage.brokerage_password = hashed_brokerage_password
    db.commit()
    db.refresh(db_user_brokerage)
    return db_user_brokerage
