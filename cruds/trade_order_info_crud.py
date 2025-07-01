import logging
import pytz
from datetime import datetime, time
from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.trade_order_info import TradeOrderInfo
from schemas import trade_order_info as schemas_trade_order_info

# Configure logging
logger = logging.getLogger(__name__)

# Define timezone
TIMEZONE = pytz.timezone('America/Sao_Paulo')


def create_trade_order_info(
        db: Session,
        trade_order_info: schemas_trade_order_info.TradeOrderInfoCreate
) -> TradeOrderInfo:
    """
    Create a new trade order information record.

    Args:
        db: Database session
        trade_order_info: Trade order information data

    Returns:
        Created TradeOrderInfo object

    Raises:
        HTTPException: If a database error occurs
    """
    try:
        db_trade_order_info = TradeOrderInfo(
            user_id=trade_order_info.user_id,
            order_id=trade_order_info.order_id,
            symbol=trade_order_info.symbol,
            order_type=trade_order_info.order_type,
            quantity=trade_order_info.quantity,
            price=trade_order_info.price,
            status=trade_order_info.status,
            date_time=trade_order_info.date_time,
            brokerage_id=trade_order_info.brokerage_id,
        )
        db.add(db_trade_order_info)
        db.commit()
        db.refresh(db_trade_order_info)
        return db_trade_order_info
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating trade order info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar informação de ordem de negociação"
        )


def get_trade_order_info_by_user_id_today(
        db: Session,
        user_id: int,
        brokerage_id: int
) -> List[TradeOrderInfo]:
    """
    Retrieve trade order information for a specific user and brokerage for today.

    Args:
        db: Database session
        user_id: ID of the user
        brokerage_id: ID of the brokerage

    Returns:
        List of TradeOrderInfo objects for today

    Raises:
        HTTPException: If a database error occurs
    """
    try:
        # Get current date in the specified timezone
        now_local = datetime.now(TIMEZONE)
        today = now_local.date()

        # Create start and end of day timestamps
        start_of_day = TIMEZONE.localize(datetime.combine(today, time.min))
        end_of_day = TIMEZONE.localize(datetime.combine(today, time.max))

        # Query database
        return db.query(TradeOrderInfo).filter(
            TradeOrderInfo.user_id == user_id,
            TradeOrderInfo.brokerage_id == brokerage_id,
            TradeOrderInfo.date_time >= start_of_day,
            TradeOrderInfo.date_time <= end_of_day
        ).all()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            f"Database error retrieving trade orders for user {user_id} and brokerage {brokerage_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar informações de ordens de negociação"
        )


def get_trade_order_infos_by_user(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 1000
) -> List[TradeOrderInfo]:
    """
    Retrieve all trade order information for a specific user with pagination.

    Args:
        db: Database session
        user_id: ID of the user
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of TradeOrderInfo objects

    Raises:
        HTTPException: If a database error occurs
    """
    try:
        return db.query(TradeOrderInfo).filter(
            TradeOrderInfo.user_id == user_id
        ).order_by(
            TradeOrderInfo.date_time.desc()
        ).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error retrieving trade orders for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar informações de ordens de negociação"
        )


def get_trade_order_infos_by_user_and_brokerage(
        db: Session,
        user_id: int,
        brokerage_id: int,
        skip: int = 0,
        limit: int = 1000
) -> List[TradeOrderInfo]:
    """
    Retrieve all trade order information for a specific user with pagination.

    Args:
        db: Database session
        user_id: ID of the user
        user_id: ID of the brokerage
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of TradeOrderInfo objects

    Raises:
        HTTPException: If a database error occurs
    """
    try:
        return db.query(TradeOrderInfo).filter(
            TradeOrderInfo.user_id == user_id,
            TradeOrderInfo.brokerage_id == brokerage_id
        ).order_by(
            TradeOrderInfo.date_time.desc()
        ).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error retrieving trade orders for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar informações de ordens de negociação"
        )


def get_trade_order_info_by_order_id(
        db: Session,
        order_id: str,
        user_id: int
) -> Optional[TradeOrderInfo]:
    """
    Retrieve trade order information by order ID and user ID.

    Args:
        db: Database session
        order_id: ID of the order
        user_id: ID of the user

    Returns:
        TradeOrderInfo object if found, None otherwise

    Raises:
        HTTPException: If a database error occurs
    """
    try:
        return db.query(TradeOrderInfo).filter(
            TradeOrderInfo.order_id == order_id,
            TradeOrderInfo.user_id == user_id
        ).first()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error retrieving trade order {order_id} for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar informação de ordem de negociação"
        )


def update_trade_order_info_by_id(
        db: Session,
        trade_order_info: schemas_trade_order_info.TradeOrderInfoUpdate
) -> TradeOrderInfo:
    """
    Update an existing trade order information record.

    Args:
        db: Database session
        trade_order_info: Updated trade order information data

    Returns:
        Updated TradeOrderInfo object

    Raises:
        HTTPException: If the trade order information is not found or a database error occurs
    """
    try:
        # Get existing trade order info
        db_trade_order_info = get_trade_order_info_by_order_id(
            db,
            trade_order_info.order_id,
            trade_order_info.user_id
        )

        if not db_trade_order_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Informação de ordem de negociação não encontrada"
            )

        # Update status if provided
        if trade_order_info.status is not None:
            db_trade_order_info.status = trade_order_info.status

        # Update other fields if needed in the future
        # ...

        db.commit()
        db.refresh(db_trade_order_info)
        return db_trade_order_info
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating trade order {trade_order_info.order_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar informação de ordem de negociação"
        )


def delete_trade_order_info(db: Session, order_id: str, user_id: int) -> bool:
    """
    Delete a trade order information record.

    Args:
        db: Database session
        order_id: ID of the order
        user_id: ID of the user

    Returns:
        True if deleted successfully, False if not found

    Raises:
        HTTPException: If a database error occurs
    """
    try:
        db_trade_order_info = get_trade_order_info_by_order_id(db, order_id, user_id)
        if not db_trade_order_info:
            return False

        db.delete(db_trade_order_info)
        db.commit()
        return True
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deleting trade order {order_id} for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao excluir informação de ordem de negociação"
        )
