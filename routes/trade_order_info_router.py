from fastapi import APIRouter
from schemas import token_data as schemas_token
from sqlalchemy.orm import Session
from connection import SessionLocal
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasicCredentials, OAuth2PasswordRequestForm
from cruds import security_crud as security
from datetime import timedelta
from cruds import trade_order_info_crud as trade_order_info_crud
from schemas import trade_order_info as trade_order_info_schema

trade_order_info_router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@trade_order_info_router.post("/trade_order_info/create", response_model=trade_order_info_schema.TradeOrderInfo)
def create_trade_order_info(
    trade_order_info: trade_order_info_schema.TradeOrderInfoCreate,
    db: Session = Depends(get_db),
    credentials: HTTPBasicCredentials = Depends(security.get_basic_credentials)
):
    """
    Create a new trade order.
    Requires authentication.
    """
    return trade_order_info_crud.create_trade_order_info(db, trade_order_info)


@trade_order_info_router.get("/trade_order_info/today/{brokerage_id}", response_model=list[trade_order_info_schema.TradeOrderInfo])
def get_trade_order_info_by_user_id_today(
    brokerage_id: int,
    db: Session = Depends(get_db),
    current_user: schemas_token.Token = Depends(security.get_current_user)
):
    """
    Get all trade orders for a user for today.
    Requires authentication.
    """
    trade_orders = trade_order_info_crud.get_trade_order_info_by_user_id_today(db, current_user.id, brokerage_id)
    if not trade_orders:
        raise HTTPException(status_code=404, detail="No trade orders found for today.")
    return trade_orders


@trade_order_info_router.get("/trade_order_info/all}", response_model=list[trade_order_info_schema.TradeOrderInfo])
def get_trade_order_infos_by_user_id_today(db: Session = Depends(get_db), current_user: schemas_token.Token = Depends(security.get_current_user)):
    trade_orders = trade_order_info_crud.get_trade_order_infos_by_user(db, current_user.id)
    if not trade_orders:
        raise HTTPException(status_code=404, detail="No trade orders found for today.")
    return trade_orders
                                           

@trade_order_info_router.put("/trade_order_info/update", response_model=trade_order_info_schema.TradeOrderInfo)
def update_trade_order_info_by_id(
    trade_order_info: trade_order_info_schema.TradeOrderInfoUpdate,
    db: Session = Depends(get_db),
    credentials: HTTPBasicCredentials = Depends(security.get_basic_credentials)
):
    """
    Update an existing trade order.
    Requires authentication.
    """
    updated_trade_order = trade_order_info_crud.update_trade_order_info_by_id(db, trade_order_info)
    if not updated_trade_order:
        raise HTTPException(status_code=404, detail="Trade order info not found.")
    return updated_trade_order