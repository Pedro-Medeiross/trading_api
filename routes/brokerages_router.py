from fastapi import APIRouter, Request
from schemas import brokerages as schemas_brokerages
from sqlalchemy.orm import Session
from connection import SessionLocal
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasicCredentials, OAuth2PasswordRequestForm
from cruds import security_crud as security
from cruds import brokerages_crud as crud_brokerages
from schemas import user as schemas_user
from datetime import timedelta
import logging

brokerages_router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@brokerages_router.get("/brokerages", response_model=list[schemas_brokerages.Brokerage], dependencies=[Depends(security.get_current_user)])
async def get_brokerages(db: Session = Depends(get_db), current_user: schemas_user.User = Depends(security.get_current_user)):
    brokerages = crud_brokerages.get_brokerages_by_user_id(db, current_user.id)
    return brokerages


@brokerages_router.post("/brokerages", response_model=schemas_brokerages.Brokerage, dependencies=[Depends(security.get_current_user)])
async def create_brokerage(brokerage: schemas_brokerages.BrokeragesCreate, db: Session = Depends(get_db), current_user: schemas_user.User = Depends(security.get_current_user)):
    brokerage = crud_brokerages.create_brokerage(db, brokerage)
    return brokerage


@brokerages_router.put("/brokerages/{brokerage_id}", response_model=schemas_brokerages.Brokerage, dependencies=[Depends(security.get_current_user)])
async def update_brokerage(brokerage_id: int, brokerage: schemas_brokerages.BrokeragesUpdate, db: Session = Depends(get_db), current_user: schemas_user.User = Depends(security.get_current_user)):
    brokerage = crud_brokerages.update_brokerage(db, brokerage_id, brokerage)
    return brokerage


@brokerages_router.get("/brokerages/{brokerage_id}", response_model=schemas_brokerages.Brokerage, dependencies=[Depends(security.get_current_user)])
async def get_brokerage_by_id(brokerage_id: int, db: Session = Depends(get_db), current_user: schemas_user.User = Depends(security.get_current_user)):
    brokerage = crud_brokerages.get_brokerage_by_id(db, brokerage_id)
    return brokerage


@brokerages_router.get("/brokerages/{user_id}", response_model=list[schemas_brokerages.Brokerage], dependencies=[Depends(security.get_current_user)])
async def get_user_brokerages(user_id: int, db: Session = Depends(get_db), current_user: schemas_user.User = Depends(security.get_current_user)):
    brokerages = crud_brokerages.get_brokerages_by_user_id(db, user_id)
    return brokerages