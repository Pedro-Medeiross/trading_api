import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from schemas import token_data as schemas_token
from sqlalchemy.orm import Session
from connection import get_db
from fastapi.security import HTTPBasicCredentials, OAuth2PasswordRequestForm
from cruds import security_crud as security
from cruds import trade_pairs_crud as crud_trade_pairs
from schemas import trade_pairs as schemas_trade_pairs



# Configure logging
logger = logging.getLogger(__name__)

trade_pairs_router = APIRouter()


@trade_pairs_router.post("/create", response_model=schemas_trade_pairs.TradePair)
async def create_trade_pair(trade_pair: schemas_trade_pairs.TradePairCreate, db: Session = Depends(get_db)):
    return await crud_trade_pairs.create_trade_pair(db, trade_pair)


@trade_pairs_router.get("/all", response_model=List[schemas_trade_pairs.TradePair])
async def get_all_trade_pairs(db: Session = Depends(get_db)):
    return await crud_trade_pairs.get_all_trade_pairs(db)


@trade_pairs_router.get("/{trade_pair_id}", response_model=schemas_trade_pairs.TradePair)
async def get_trade_pair(trade_pair_id: int, db: Session = Depends(get_db)):
    trade_pair = await crud_trade_pairs.get_trade_pair(db, trade_pair_id)
    if not trade_pair:
        raise HTTPException(status_code=404, detail="Trade pair not found")
    return trade_pair


@trade_pairs_router.put("/{trade_pair_id}", response_model=schemas_trade_pairs.TradePair)
async def update_trade_pair(trade_pair_id: int, trade_pair: schemas_trade_pairs.TradePairUpdate, db: Session = Depends(get_db)):
    updated_trade_pair = await crud_trade_pairs.update_trade_pair(db, trade_pair_id, trade_pair)
    if not updated_trade_pair:
        raise HTTPException(status_code=404, detail="Trade pair not found")
    return updated_trade_pair


@trade_pairs_router.delete("/{trade_pair_id}", response_model=schemas_trade_pairs.TradePair)
async def delete_trade_pair(trade_pair_id: int, db: Session = Depends(get_db)):
    deleted_trade_pair = await crud_trade_pairs.delete_trade_pair(db, trade_pair_id)
    if not deleted_trade_pair:
        raise HTTPException(status_code=404, detail="Trade pair not found")
    return deleted_trade_pair


@trade_pairs_router.delete("/delete/{trade_pair_id}", response_model=schemas_trade_pairs.TradePair)
async def delete_trade_pair(trade_pair_id: int, db: Session = Depends(get_db)):
    deleted_trade_pair = await crud_trade_pairs.delete_trade_pair(db, trade_pair_id)
    if not deleted_trade_pair:
        raise HTTPException(status_code=404, detail="Trade pair not found")
    return deleted_trade_pair
