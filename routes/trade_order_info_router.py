import logging
from fastapi import APIRouter, Depends, HTTPException, status
from schemas import token_data as schemas_token
from sqlalchemy.orm import Session
from connection import get_db
from fastapi.security import HTTPBasicCredentials
from cruds import security_crud as security
from cruds import trade_order_info_crud as trade_order_info_crud
from schemas import trade_order_info as trade_order_info_schema

# Configure logging
logger = logging.getLogger(__name__)

trade_order_info_router = APIRouter()


@trade_order_info_router.post("", response_model=trade_order_info_schema.TradeOrderInfo)
def create_trade_order_info(
        trade_order_info: trade_order_info_schema.TradeOrderInfoCreate,
        db: Session = Depends(get_db),
        credentials: HTTPBasicCredentials = Depends(security.get_basic_credentials)
):
    """
    Create a new trade order.

    Requires basic authentication.
    """
    try:
        return trade_order_info_crud.create_trade_order_info(db, trade_order_info)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating trade order info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar informação de ordem de negociação"
        )


@trade_order_info_router.get(path='/all/{brokerage_id}', response_model=list[trade_order_info_schema.TradeOrderInfo])
def get_trade_order_infos_by_user_and_brokerage(
        brokerage_id: int,
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: schemas_token.Token = Depends(security.get_current_user)
):
    """
        Get all trade orders for the current user and brokerage with pagination.

        Args:
            brokerage_id: Brokerage ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Requires JWT authentication.
        """


    try:
        trade_orders = trade_order_info_crud.get_trade_order_infos_by_user_and_brokerage(db, current_user.id, brokerage_id, skip, limit)
        if not trade_orders:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nenhuma ordem de negociação encontrada."
            )
        return trade_orders
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving all trade orders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar ordens de negociação"
        )


@trade_order_info_router.get("/today/{brokerage_id}", response_model=list[trade_order_info_schema.TradeOrderInfo])
def get_trade_order_info_by_user_id_today(
        brokerage_id: int,
        db: Session = Depends(get_db),
        current_user: schemas_token.Token = Depends(security.get_current_user)
):
    """
    Get all trade orders for the current user for today.

    Args:
        brokerage_id: ID of the brokerage

    Requires JWT authentication.
    """
    try:
        trade_orders = trade_order_info_crud.get_trade_order_info_by_user_id_today(db, current_user.id, brokerage_id)
        if not trade_orders:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nenhuma ordem de negociação encontrada para hoje."
            )
        return trade_orders
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving trade orders for today: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar ordens de negociação"
        )


@trade_order_info_router.get("/all", response_model=list[trade_order_info_schema.TradeOrderInfo])
def get_trade_order_infos_by_user(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: schemas_token.Token = Depends(security.get_current_user)
):
    """
    Get all trade orders for the current user with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return

    Requires JWT authentication.
    """
    try:
        trade_orders = trade_order_info_crud.get_trade_order_infos_by_user(db, current_user.id, skip, limit)
        if not trade_orders:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nenhuma ordem de negociação encontrada."
            )
        return trade_orders
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving all trade orders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar ordens de negociação"
        )


@trade_order_info_router.put("/{order_id}", response_model=trade_order_info_schema.TradeOrderInfo)
def update_trade_order_info(
        order_id: str,
        trade_order_info: trade_order_info_schema.TradeOrderInfoUpdate,
        db: Session = Depends(get_db),
        credentials: HTTPBasicCredentials = Depends(security.get_basic_credentials)
):
    """
    Update an existing trade order.

    Args:
        order_id: ID of the order to update

    Requires basic authentication.
    """
    try:
        # Ensure order_id in path matches the one in the request body
        if order_id != trade_order_info.order_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID da ordem na URL não corresponde ao ID no corpo da requisição"
            )

        return trade_order_info_crud.update_trade_order_info_by_id(db, trade_order_info)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating trade order {order_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar informação de ordem de negociação"
        )
