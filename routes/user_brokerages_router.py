from fastapi import APIRouter
from schemas import token_data as schemas_token
from sqlalchemy.orm import Session
from connection import SessionLocal
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasicCredentials, OAuth2PasswordRequestForm
from cruds import security_crud as security
from datetime import timedelta
from cruds import user_brokerages_crud as user_brokerages_crud
from schemas import user_brokerages as user_brokerages_schema

user_brokerages_router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@user_brokerages_router.get("/user_brokerages/{brokerage_id}", response_model=user_brokerages_schema.UserBrokerages, dependencies=[Depends(security.get_current_user)])
def get_user_brokerage(brokerage_id: int, db: Session = Depends(get_db), current_user: schemas_token.Token = Depends(security.get_current_user)):
    """
    Get a user brokerage by user ID and brokerage ID.
    """
    user_id = current_user.id
    return user_brokerages_crud.get_user_brokerage(db, user_id, brokerage_id)


@user_brokerages_router.get("/user_brokerages/{brokerage_id}/{user_id}", response_model=user_brokerages_schema.UserBrokerages)
def get_user_brokerage_bot(brokerage_id: int, user_id: int, db: Session = Depends(get_db), credentials: HTTPBasicCredentials = Depends(security.get_basic_credentials)):
    """
    Get a user brokerage by brokerage ID.
    """
    user_brokerages = user_brokerages_crud.get_user_brokerage(db, user_id, brokerage_id)
    if not user_brokerages:
        raise HTTPException(status_code=404, detail="User Brokerage not found")
    return user_brokerages


@user_brokerages_router.post("/user_brokerages", response_model=user_brokerages_schema.UserBrokerages, dependencies=[Depends(security.get_current_user)])
def create_user_brokerage(user_brokerage: user_brokerages_schema.UserBrokeragesCreate, db: Session = Depends(get_db), current_user: schemas_token.Token = Depends(security.get_current_user)):
    """
    Create a new user brokerage.
    """
    return user_brokerages_crud.create_user_brokerage(db, user_brokerage)

@user_brokerages_router.put("/user_brokerages/{brokerage_id}", response_model=user_brokerages_schema.UserBrokerages, dependencies=[Depends(security.get_current_user)])
def update_user_brokerage(brokerage_id: int, user_brokerage: user_brokerages_schema.UserBrokeragesUpdate, db: Session = Depends(get_db), current_user: schemas_token.Token = Depends(security.get_current_user)):
    """
    Update an existing user brokerage.
    """
    user_id = current_user.id
    return user_brokerages_crud.update_user_brokerage(db, user_id, brokerage_id, user_brokerage)