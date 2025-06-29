import logging
from fastapi import APIRouter, Depends, HTTPException, status
from schemas import bot_options as schemas_bot_options
from schemas import token_data as schemas_token
from sqlalchemy.orm import Session
from connection import get_db
from fastapi.security import HTTPBasicCredentials
from cruds import security_crud as security
from cruds import bot_options_crud as crud_bot_options

# Configure logging
logger = logging.getLogger(__name__)

bot_options_router = APIRouter()


@bot_options_router.get("/{brokerage_id}", response_model=schemas_bot_options.BotOptions)
def get_bot_options_for_current_user(
    brokerage_id: int, 
    db: Session = Depends(get_db),
    current_user: schemas_token.Token = Depends(security.get_current_user)
):
    """
    Get bot options for the current user and specified brokerage.

    Args:
        brokerage_id: ID of the brokerage

    Returns:
        Bot options for the current user

    Raises:
        HTTPException: If bot options not found

    Requires JWT authentication.
    """
    try:
        bot_options = crud_bot_options.get_bot_options_by_user_id_and_brokerage_id(
            db, current_user.id, brokerage_id
        )
        if not bot_options:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Opções do bot não encontradas"
            )
        return bot_options
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving bot options for brokerage {brokerage_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar opções do bot"
        )


@bot_options_router.put("/{brokerage_id}", response_model=schemas_bot_options.BotOptions)
def update_bot_options_for_current_user(
    brokerage_id: int,
    bot_options: schemas_bot_options.BotOptionsUpdate, 
    db: Session = Depends(get_db),
    current_user: schemas_token.Token = Depends(security.get_current_user)
):
    """
    Update bot options for the current user and specified brokerage.

    Args:
        brokerage_id: ID of the brokerage
        bot_options: Updated bot options data

    Returns:
        Updated bot options

    Raises:
        HTTPException: If bot options not found or update fails

    Requires JWT authentication.
    """
    try:
        return crud_bot_options.update_bot_options(
            db, current_user.id, brokerage_id, bot_options
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating bot options for brokerage {brokerage_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar opções do bot"
        )


@bot_options_router.post("/{brokerage_id}", response_model=schemas_bot_options.BotOptions)
def create_bot_options_for_current_user(
    brokerage_id: int,
    bot_options: schemas_bot_options.BotOptionsCreate, 
    db: Session = Depends(get_db),
    current_user: schemas_token.Token = Depends(security.get_current_user)
):
    """
    Create bot options for the current user and specified brokerage.

    Args:
        brokerage_id: ID of the brokerage
        bot_options: Bot options data

    Returns:
        Created bot options

    Raises:
        HTTPException: If creation fails

    Requires JWT authentication.
    """
    try:
        # Set user_id and brokerage_id from path and current user
        bot_options_data = bot_options.dict()
        bot_options_data["user_id"] = current_user.id
        bot_options_data["brokerage_id"] = brokerage_id

        create_data = schemas_bot_options.BotOptionsCreate(**bot_options_data)
        return crud_bot_options.create_bot_options(db, create_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating bot options for brokerage {brokerage_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar opções do bot"
        )


@bot_options_router.get("/admin/{user_id}/{brokerage_id}", response_model=schemas_bot_options.BotOptions)
def get_bot_options_admin(
    user_id: int, 
    brokerage_id: int, 
    db: Session = Depends(get_db), 
    credentials: HTTPBasicCredentials = Depends(security.get_basic_credentials)
):
    """
    Get bot options for a specific user and brokerage (admin access).

    Args:
        user_id: ID of the user
        brokerage_id: ID of the brokerage

    Returns:
        Bot options for the specified user

    Raises:
        HTTPException: If bot options not found

    Requires basic authentication.
    """
    try:
        bot_options = crud_bot_options.get_bot_options_by_user_id_and_brokerage_id(
            db, user_id, brokerage_id
        )
        if not bot_options:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Opções do bot não encontradas"
            )
        return bot_options
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving bot options for user {user_id} and brokerage {brokerage_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar opções do bot"
        )


@bot_options_router.put("/admin/{user_id}/{brokerage_id}", response_model=schemas_bot_options.BotOptions)
def update_bot_options_admin(
    user_id: int,
    brokerage_id: int,
    bot_options: schemas_bot_options.BotOptionsUpdate,
    db: Session = Depends(get_db),
    credentials: HTTPBasicCredentials = Depends(security.get_basic_credentials)
):
    """
    Update bot options for a specific user and brokerage (admin access).

    Args:
        user_id: ID of the user
        brokerage_id: ID of the brokerage
        bot_options: Updated bot options data

    Returns:
        Updated bot options

    Raises:
        HTTPException: If bot options not found or update fails

    Requires basic authentication.
    """
    try:
        return crud_bot_options.update_bot_options(
            db, user_id, brokerage_id, bot_options
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating bot options for user {user_id} and brokerage {brokerage_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar opções do bot"
        )
