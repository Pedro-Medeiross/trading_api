import logging
from typing import List, Optional, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.brokerages import Brokerages
from schemas import brokerages as schemas_brokerages

# Configure logging
logger = logging.getLogger(__name__)


def get_brokerage_by_id(db: Session, brokerage_id: int) -> Optional[Brokerages]:
    """
    Retrieve a brokerage by its ID.

    Args:
        db: Database session
        brokerage_id: ID of the brokerage to retrieve

    Returns:
        The brokerage if found, None otherwise

    Raises:
        HTTPException: If a database error occurs
    """
    try:
        return db.query(Brokerages).filter(Brokerages.id == brokerage_id).first()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error retrieving brokerage {brokerage_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar corretora"
        )


def get_brokerages(db: Session, skip: int = 0, limit: int = 100) -> list[type[Brokerages]]:
    """
    Retrieve a list of brokerages with pagination.

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of brokerages

    Raises:
        HTTPException: If a database error occurs
    """
    try:
        return db.query(Brokerages).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error retrieving brokerages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar corretoras"
        )


def get_brokerages_by_user_id(db: Session, user_id: int) -> List[Brokerages]:
    """
    Retrieve brokerages associated with a specific user.

    Args:
        db: Database session
        user_id: ID of the user

    Returns:
        List of brokerages associated with the user

    Raises:
        HTTPException: If a database error occurs
    """
    try:
        return db.query(Brokerages).filter(Brokerages.user_id == user_id).all()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error retrieving brokerages for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar corretoras do usuário"
        )


def create_brokerage(db: Session, brokerage: schemas_brokerages.BrokeragesCreate) -> Brokerages:
    """
    Create a new brokerage.

    Args:
        db: Database session
        brokerage: Brokerage data

    Returns:
        The created brokerage

    Raises:
        HTTPException: If a database error occurs
    """
    try:
        db_brokerage = Brokerages(
            brokerage_name=brokerage.brokerage_name,
            brokerage_route=brokerage.brokerage_route,
            brokerage_icon=brokerage.brokerage_icon,
            brokerage_login_url=brokerage.brokerage_login_url,
            brokerage_register_url=brokerage.brokerage_register_url,
            brokerage_traderoom_url=brokerage.brokerage_traderoom_url,
            brokerage_withdraw_url=brokerage.brokerage_withdraw_url,
            brokerage_deposit_url=brokerage.brokerage_deposit_url,
        )
        db.add(db_brokerage)
        db.commit()
        db.refresh(db_brokerage)
        return db_brokerage
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating brokerage: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar corretora"
        )


def update_brokerage(
    db: Session, 
    brokerage_id: int, 
    brokerage: schemas_brokerages.BrokeragesUpdate
) -> Brokerages:
    """
    Update an existing brokerage.

    Args:
        db: Database session
        brokerage_id: ID of the brokerage to update
        brokerage: Updated brokerage data

    Returns:
        The updated brokerage

    Raises:
        HTTPException: If the brokerage is not found or a database error occurs
    """
    try:
        db_brokerage = get_brokerage_by_id(db, brokerage_id)
        if not db_brokerage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Corretora não encontrada"
            )

        update_data = brokerage.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_brokerage, field, value)

        db.commit()
        db.refresh(db_brokerage)
        return db_brokerage
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating brokerage {brokerage_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar corretora"
        )


def delete_brokerage(db: Session, brokerage_id: int) -> bool:
    """
    Delete a brokerage by its ID.

    Args:
        db: Database session
        brokerage_id: ID of the brokerage to delete

    Returns:
        True if deleted successfully, False if not found

    Raises:
        HTTPException: If a database error occurs
    """
    try:
        db_brokerage = get_brokerage_by_id(db, brokerage_id)
        if not db_brokerage:
            return False

        db.delete(db_brokerage)
        db.commit()
        return True
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deleting brokerage {brokerage_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao excluir corretora"
        )
