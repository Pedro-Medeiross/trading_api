import logging
import pytz
from datetime import datetime
from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.user import User
from schemas import user as schemas_user
from cruds import security_crud as crud_security

# Configure logging
logger = logging.getLogger(__name__)

# Define timezone
TIMEZONE = pytz.timezone('America/Sao_Paulo')


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Retrieve a user by ID.

    Args:
        db: Database session
        user_id: ID of the user

    Returns:
        User object if found, None otherwise

    Raises:
        HTTPException: If a database error occurs
    """
    try:
        return db.query(User).filter(User.id == user_id).first()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error retrieving user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar usuário"
        )


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """
    Retrieve a list of users with pagination.

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of User objects

    Raises:
        HTTPException: If a database error occurs
    """
    try:
        return db.query(User).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error retrieving users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar usuários"
        )


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Retrieve a user by email.

    Args:
        db: Database session
        email: Email of the user

    Returns:
        User object if found, None otherwise

    Raises:
        HTTPException: If a database error occurs
    """
    try:
        return db.query(User).filter(User.email == email.lower()).first()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error retrieving user by email {email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar usuário por email"
        )


def create_user(db: Session, user: schemas_user.UserCreate) -> User:
    """
    Create a new user.

    Args:
        db: Database session
        user: User data

    Returns:
        Created User object

    Raises:
        HTTPException: If a database error occurs or email already exists
    """
    try:
        # Check if email already exists
        existing_user = get_user_by_email(db, user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já está em uso"
            )

        # Get current time in the specified timezone
        now_local = datetime.now(TIMEZONE)

        # Create user instance
        db_user = User(
            complete_name=user.complete_name,
            email=user.email.lower(),
            password=crud_security.get_password_hash(user.password),
            is_superuser=user.is_superuser,
            created_at=now_local,
            is_active=False,
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar usuário"
        )


def user_last_login(db: Session, user_id: int) -> User:
    """
    Update the last login timestamp for a user.

    Args:
        db: Database session
        user_id: ID of the user

    Returns:
        Updated User object

    Raises:
        HTTPException: If user not found or database error occurs
    """
    try:
        # Get current time in the specified timezone
        now_local = datetime.now(TIMEZONE)

        # Get user
        db_user = get_user_by_id(db, user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )

        # Update last login timestamp
        db_user.last_login = now_local

        db.commit()
        db.refresh(db_user)
        return db_user
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating last login for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar último login"
        )


def update_user(db: Session, user_id: int, user: schemas_user.UserUpdate) -> User:
    """
    Update an existing user.

    Args:
        db: Database session
        user_id: ID of the user to update
        user: Updated user data

    Returns:
        Updated User object

    Raises:
        HTTPException: If user not found or database error occurs
    """
    try:
        # Get user
        db_user = get_user_by_id(db, user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )

        # Update fields from request data
        update_data = user.dict(exclude_unset=True)

        # Validate password change if any password field is provided
        if user.old_password or user.password:
            # Both fields must be provided for password change
            if not user.old_password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Para alterar a senha, forneça a senha atual no campo old_password"
                )

            if not user.password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Para alterar a senha, forneça a nova senha no campo password"
                )

            # Verify current password is correct
            if not crud_security.verify_password(plain_password=user.old_password, hashed_password=db_user.password):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Senha atual incorreta"
                )

            # Hash the new password before storing
            update_data['password'] = crud_security.get_password_hash(user.password)

        # Remove old_password from update data as it shouldn't be stored
        update_data.pop('old_password', None)

        # If email is being updated, check if it's already in use
        if 'email' in update_data and update_data['email'] != db_user.email:
            existing_user = get_user_by_email(db, update_data['email'])
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email já está em uso"
                )

        # Update fields
        for field, value in update_data.items():
            setattr(db_user, field, value)

        db.commit()
        db.refresh(db_user)
        return db_user
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar usuário"
        )


def delete_user(db: Session, user_id: int) -> bool:
    """
    Delete a user.

    Args:
        db: Database session
        user_id: ID of the user to delete

    Returns:
        True if deleted successfully, False if not found

    Raises:
        HTTPException: If a database error occurs
    """
    try:
        db_user = get_user_by_id(db, user_id)
        if not db_user:
            return False

        db.delete(db_user)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deleting user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao excluir usuário"
        )
