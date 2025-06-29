import logging
from fastapi import APIRouter, Depends, HTTPException, status
from schemas import token_data as schemas_token
from schemas import user_brokerages as schemas_user_brokerages
from sqlalchemy.orm import Session
from connection import get_db
from fastapi.security import HTTPBasicCredentials
from cruds import security_crud as security
from cruds import user_brokerages_crud as crud_user_brokerages

# Configure logging
logger = logging.getLogger(__name__)

user_brokerages_router = APIRouter()


@user_brokerages_router.get("/{brokerage_id}", response_model=schemas_user_brokerages.UserBrokerages)
def get_user_brokerage_for_current_user(
    brokerage_id: int, 
    db: Session = Depends(get_db), 
    current_user: schemas_token.Token = Depends(security.get_current_user)
):
    """
    Get a user brokerage for the current user and specified brokerage.

    Args:
        brokerage_id: ID of the brokerage

    Returns:
        User brokerage for the current user

    Raises:
        HTTPException: If user brokerage not found or retrieval fails

    Requires JWT authentication.
    """
    try:
        return crud_user_brokerages.get_user_brokerage(db, current_user.id, brokerage_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user brokerage for brokerage {brokerage_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar corretora do usuário"
        )


@user_brokerages_router.get("", response_model=list[schemas_user_brokerages.UserBrokerages])
def get_user_brokerages_for_current_user(
    db: Session = Depends(get_db), 
    current_user: schemas_token.Token = Depends(security.get_current_user)
):
    """
    Get all user brokerages for the current user.

    Returns:
        List of user brokerages for the current user

    Raises:
        HTTPException: If retrieval fails

    Requires JWT authentication.
    """
    try:
        return crud_user_brokerages.get_user_brokerages_by_user_id(db, current_user.id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user brokerages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar corretoras do usuário"
        )


@user_brokerages_router.post("", response_model=schemas_user_brokerages.UserBrokerages)
def create_user_brokerage(
    user_brokerage: schemas_user_brokerages.UserBrokeragesCreate, 
    db: Session = Depends(get_db), 
    current_user: schemas_token.Token = Depends(security.get_current_user)
):
    """
    Create a new user brokerage.

    Args:
        user_brokerage: User brokerage data

    Returns:
        Created user brokerage

    Raises:
        HTTPException: If creation fails

    Requires JWT authentication.
    """
    try:
        # Set user_id from current user
        user_brokerage_data = user_brokerage.dict()
        user_brokerage_data["user_id"] = current_user.id

        create_data = schemas_user_brokerages.UserBrokeragesCreate(**user_brokerage_data)
        return crud_user_brokerages.create_user_brokerage(db, create_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user brokerage: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar corretora do usuário"
        )


@user_brokerages_router.put("/{brokerage_id}", response_model=schemas_user_brokerages.UserBrokerages)
def update_user_brokerage_for_current_user(
    brokerage_id: int, 
    user_brokerage: schemas_user_brokerages.UserBrokeragesUpdate, 
    db: Session = Depends(get_db), 
    current_user: schemas_token.Token = Depends(security.get_current_user)
):
    """
    Update an existing user brokerage for the current user.

    Args:
        brokerage_id: ID of the brokerage
        user_brokerage: Updated user brokerage data

    Returns:
        Updated user brokerage

    Raises:
        HTTPException: If user brokerage not found or update fails

    Requires JWT authentication.
    """
    try:
        return crud_user_brokerages.update_user_brokerage(
            db, current_user.id, brokerage_id, user_brokerage
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user brokerage for brokerage {brokerage_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar corretora do usuário"
        )


@user_brokerages_router.delete("/{brokerage_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_brokerage_for_current_user(
    brokerage_id: int, 
    db: Session = Depends(get_db), 
    current_user: schemas_token.Token = Depends(security.get_current_user)
):
    """
    Delete a user brokerage for the current user.

    Args:
        brokerage_id: ID of the brokerage

    Returns:
        No content

    Raises:
        HTTPException: If user brokerage not found or deletion fails

    Requires JWT authentication.
    """
    try:
        result = crud_user_brokerages.delete_user_brokerage(db, current_user.id, brokerage_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Corretora do usuário não encontrada"
            )
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user brokerage for brokerage {brokerage_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao excluir corretora do usuário"
        )


@user_brokerages_router.get("/admin/{user_id}/{brokerage_id}", response_model=schemas_user_brokerages.UserBrokerages)
def get_user_brokerage_admin(
    user_id: int, 
    brokerage_id: int, 
    db: Session = Depends(get_db), 
    credentials: HTTPBasicCredentials = Depends(security.get_basic_credentials)
):
    """
    Get a user brokerage for a specific user and brokerage (admin access).

    Args:
        user_id: ID of the user
        brokerage_id: ID of the brokerage

    Returns:
        User brokerage for the specified user

    Raises:
        HTTPException: If user brokerage not found or retrieval fails

    Requires basic authentication.
    """
    try:
        return crud_user_brokerages.get_user_brokerage(db, user_id, brokerage_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user brokerage for user {user_id} and brokerage {brokerage_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar corretora do usuário"
        )
