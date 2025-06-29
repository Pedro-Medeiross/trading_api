import logging
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from models.bot_options import BotOptions
from schemas import bot_options as schemas_bot_options

# Configure logging
logger = logging.getLogger(__name__)


def get_bot_options_by_user_id(db: Session, user_id: int) -> Optional[BotOptions]:
    """
    Retrieve bot options for a specific user.

    Args:
        db: Database session
        user_id: ID of the user

    Returns:
        BotOptions object if found, None otherwise

    Raises:
        HTTPException: If a database error occurs
    """
    try:
        return db.query(BotOptions).filter(BotOptions.user_id == user_id).first()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error retrieving bot options for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar opções do bot"
        )


def get_bot_options_by_user_id_and_brokerage_id(
    db: Session, 
    user_id: int, 
    brokerage_id: int
) -> Optional[BotOptions]:
    """
    Retrieve bot options for a specific user and brokerage.

    Args:
        db: Database session
        user_id: ID of the user
        brokerage_id: ID of the brokerage

    Returns:
        BotOptions object if found, None otherwise

    Raises:
        HTTPException: If a database error occurs
    """
    try:
        return db.query(BotOptions).filter(
            BotOptions.user_id == user_id,
            BotOptions.brokerage_id == brokerage_id
        ).first()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error retrieving bot options for user {user_id} and brokerage {brokerage_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar opções do bot"
        )


def create_bot_options(db: Session, bot_options: schemas_bot_options.BotOptionsCreate) -> BotOptions:
    """
    Create new bot options.

    Args:
        db: Database session
        bot_options: Bot options data

    Returns:
        Created BotOptions object

    Raises:
        HTTPException: If a database error occurs
    """
    try:
        # Create model instance with data from schema
        db_bot_options = BotOptions(
            user_id=bot_options.user_id,
            bot_status=bot_options.bot_status,
            stop_loss=bot_options.stop_loss,
            stop_win=bot_options.stop_win,
            entry_price=bot_options.entry_price,
            is_demo=bot_options.is_demo,
            win_value=bot_options.win_value,
            loss_value=bot_options.loss_value,
            gale_one=bot_options.gale_one,
            gale_two=bot_options.gale_two,
            brokerage_id=bot_options.brokerage_id
        )

        # Add to database and commit
        db.add(db_bot_options)
        db.commit()
        db.refresh(db_bot_options)
        return db_bot_options
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating bot options: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar opções do bot"
        )


def update_bot_options(
    db: Session, 
    user_id: int, 
    brokerage_id: int, 
    bot_options: schemas_bot_options.BotOptionsUpdate
) -> BotOptions:
    """
    Update existing bot options.

    Args:
        db: Database session
        user_id: ID of the user
        brokerage_id: ID of the brokerage
        bot_options: Updated bot options data

    Returns:
        Updated BotOptions object

    Raises:
        HTTPException: If bot options not found or database error occurs
    """
    try:
        # Get existing bot options
        db_bot_options = get_bot_options_by_user_id_and_brokerage_id(db, user_id, brokerage_id)
        if not db_bot_options:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Opções do bot não encontradas para o usuário {user_id} e corretora {brokerage_id}"
            )

        # Update fields from request data
        update_data = bot_options.dict(exclude_unset=True)
        if not update_data:
            return db_bot_options  # No changes needed

        for field, value in update_data.items():
            setattr(db_bot_options, field, value)

        # Commit changes
        db.commit()
        db.refresh(db_bot_options)
        return db_bot_options
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating bot options: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar opções do bot"
        )


def delete_bot_options(db: Session, user_id: int, brokerage_id: int) -> bool:
    """
    Delete bot options for a specific user and brokerage.

    Args:
        db: Database session
        user_id: ID of the user
        brokerage_id: ID of the brokerage

    Returns:
        True if deleted successfully, False if not found

    Raises:
        HTTPException: If a database error occurs
    """
    try:
        db_bot_options = get_bot_options_by_user_id_and_brokerage_id(db, user_id, brokerage_id)
        if not db_bot_options:
            return False

        db.delete(db_bot_options)
        db.commit()
        return True
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deleting bot options: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao excluir opções do bot"
        )
