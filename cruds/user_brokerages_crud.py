import base64
import logging
import secrets
from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.user_brokerages import UserBrokerages
from schemas import user_brokerages as schemas_user_brokerages

# Configure logging
logger = logging.getLogger(__name__)


def get_user_brokerage(db: Session, user_id: int, brokerage_id: int) -> Optional[UserBrokerages]:
    """
    Retrieve a user brokerage by user ID and brokerage ID.

    Args:
        db: Database session
        user_id: ID of the user
        brokerage_id: ID of the brokerage

    Returns:
        UserBrokerages object if found

    Raises:
        HTTPException: If user brokerage not found or database error occurs
    """
    try:
        db_user_brokerage = db.query(UserBrokerages).filter(
            UserBrokerages.user_id == user_id,
            UserBrokerages.brokerage_id == brokerage_id
        ).first()

        if not db_user_brokerage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Corretora do usuário não encontrada"
            )

        return db_user_brokerage
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error retrieving user brokerage for user {user_id} and brokerage {brokerage_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar corretora do usuário"
        )


def get_user_brokerages_by_user_id(db: Session, user_id: int) -> List[UserBrokerages]:
    """
    Retrieve all brokerages for a specific user.

    Args:
        db: Database session
        user_id: ID of the user

    Returns:
        List of UserBrokerages objects

    Raises:
        HTTPException: If database error occurs
    """
    try:
        return db.query(UserBrokerages).filter(
            UserBrokerages.user_id == user_id
        ).all()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error retrieving user brokerages for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar corretoras do usuário"
        )


def create_user_brokerage(
    db: Session, 
    user_brokerage: schemas_user_brokerages.UserBrokeragesCreate
) -> UserBrokerages:
    """
    Create a new user brokerage.

    Args:
        db: Database session
        user_brokerage: User brokerage data

    Returns:
        Created UserBrokerages object

    Raises:
        HTTPException: If database error occurs
    """
    try:
        # Securely handle sensitive data
        api_key = user_brokerage.api_key
        brokerage_password = user_brokerage.brokerage_password

        # Create model instance
        db_user_brokerage = UserBrokerages(
            user_id=user_brokerage.user_id,
            brokerage_id=user_brokerage.brokerage_id,
            api_key=api_key,
            brokerage_username=user_brokerage.brokerage_username,
            brokerage_password=brokerage_password
        )

        db.add(db_user_brokerage)
        db.commit()
        db.refresh(db_user_brokerage)
        return db_user_brokerage
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating user brokerage: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar corretora do usuário"
        )


def update_user_brokerage(
    db: Session,
    user_id: int,
    brokerage_id: int,
    user_brokerage: schemas_user_brokerages.UserBrokeragesUpdate
) -> UserBrokerages:
    """
    Update an existing user brokerage.

    Args:
        db: Database session
        user_id: ID of the user
        brokerage_id: ID of the brokerage
        user_brokerage: Updated user brokerage data

    Returns:
        Updated UserBrokerages object

    Raises:
        HTTPException: If user brokerage not found or database error occurs
    """
    try:
        # Get existing user brokerage
        db_user_brokerage = get_user_brokerage(db, user_id, brokerage_id)

        # Update API key if provided and different
        if user_brokerage.api_key is not None:
            if user_brokerage.api_key != (db_user_brokerage.api_key or ""):
                db_user_brokerage.api_key = user_brokerage.api_key

        # Update username if provided
        if user_brokerage.brokerage_username is not None:
            db_user_brokerage.brokerage_username = user_brokerage.brokerage_username

        # Update password if provided and different
        if user_brokerage.brokerage_password is not None:
            if user_brokerage.brokerage_password != (db_user_brokerage.brokerage_password or ""):
                db_user_brokerage.brokerage_password = user_brokerage.brokerage_password

        db.commit()
        db.refresh(db_user_brokerage)
        return db_user_brokerage
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating user brokerage for user {user_id} and brokerage {brokerage_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar corretora do usuário"
        )


def delete_user_brokerage(db: Session, user_id: int, brokerage_id: int) -> bool:
    """
    Delete a user brokerage.

    Args:
        db: Database session
        user_id: ID of the user
        brokerage_id: ID of the brokerage

    Returns:
        True if deleted successfully, False if not found

    Raises:
        HTTPException: If database error occurs
    """
    try:
        # Try to get the user brokerage without raising an exception if not found
        db_user_brokerage = db.query(UserBrokerages).filter(
            UserBrokerages.user_id == user_id,
            UserBrokerages.brokerage_id == brokerage_id
        ).first()

        if not db_user_brokerage:
            return False

        db.delete(db_user_brokerage)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deleting user brokerage for user {user_id} and brokerage {brokerage_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao excluir corretora do usuário"
        )
