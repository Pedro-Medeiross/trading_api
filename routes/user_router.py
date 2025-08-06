import logging
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from schemas import user as schemas_user
from schemas import token_data as schemas_token
from sqlalchemy.orm import Session
from connection import get_db
from fastapi.security import HTTPBasicCredentials, OAuth2PasswordRequestForm
from cruds import security_crud as security
from cruds import user_crud as crud_user

# Configure logging
logger = logging.getLogger(__name__)

user_router = APIRouter()


@user_router.get("/me", response_model=schemas_user.User)
def get_current_user(
    current_user: schemas_user.User = Depends(security.get_current_user)
):
    """
    Get the current authenticated user.

    Returns:
        Current user information

    Requires JWT authentication.
    """
    return current_user


@user_router.post("/login", response_model=schemas_token.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    """
    Authenticate a user and return access and refresh tokens.

    Args:
        form_data: Username and password

    Returns:
        Access token, refresh token, and token type

    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Authenticate user
        user = security.authenticate_user(db, form_data.username, form_data.password)

        # Verify user activation
        user = security.verify_user_activation_to_login(db, user.id)

        # Generate tokens
        access_token_expires = timedelta(hours=12)
        access_token = security.create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )

        refresh_token_expires = timedelta(days=30)
        refresh_token = security.create_refresh_token(
            data={"sub": user.email}, expires_delta=refresh_token_expires
        )

        # Update last login timestamp
        crud_user.user_last_login(db, user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar login"
        )


@user_router.post("/refresh", response_model=schemas_token.Token)
def refresh_access_token(
    refresh_token: str = Depends(security.oauth2_scheme)
):
    """
    Use a refresh token to generate a new access token.

    Returns:
        New access token, refresh token, and token type
    """
    try:
        username = security.verify_refresh_token(refresh_token)

        access_token_expires = timedelta(hours=6)
        access_token = security.create_access_token(
            data={"sub": username}, expires_delta=access_token_expires
        )

        # ✅ Retorna os 3 campos exigidos pelo schemas_token.Token
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar token"
        )


@user_router.post("", response_model=schemas_user.User)
def create_user(
    user: schemas_user.UserCreate, 
    db: Session = Depends(get_db), 
    credentials: HTTPBasicCredentials = Depends(security.get_basic_credentials)
):
    """
    Create a new user.

    Args:
        user: User data

    Returns:
        Created user

    Raises:
        HTTPException: If email already exists or creation fails

    Requires basic authentication.
    """
    try:
        return crud_user.create_user(db=db, user=user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar usuário"
        )


@user_router.put("/me", response_model=schemas_user.User)
def update_current_user(
    user: schemas_user.UserUpdate, 
    db: Session = Depends(get_db), 
    current_user: schemas_user.User = Depends(security.get_current_user)
):
    """
    Update the current user.

    Args:
        user: Updated user data

    Returns:
        Updated user

    Raises:
        HTTPException: If update fails

    Requires JWT authentication.
    """
    try:
        return crud_user.update_user(db, user_id=current_user.id, user=user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar usuário"
        )


@user_router.get("", response_model=list[schemas_user.User])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db), 
    current_user: schemas_user.User = Depends(security.get_current_user)
):
    """
    Get all users with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of users

    Raises:
        HTTPException: If retrieval fails or user is not authorized

    Requires JWT authentication and superuser privileges.
    """
    try:
        # Check if user is superuser
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso restrito a administradores"
            )

        return crud_user.get_users(db=db, skip=skip, limit=limit)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar usuários"
        )


@user_router.get("/{user_id}", response_model=schemas_user.User)
def get_user(
    user_id: int,
    db: Session = Depends(get_db), 
    current_user: schemas_user.User = Depends(security.get_current_user)
):
    """
    Get a user by ID.

    Args:
        user_id: ID of the user

    Returns:
        User with the specified ID

    Raises:
        HTTPException: If user not found, retrieval fails, or current user is not authorized

    Requires JWT authentication and either superuser privileges or be the requested user.
    """
    try:
        # Check if user is superuser or the requested user
        if not current_user.is_superuser and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Não autorizado a acessar este usuário"
            )

        user = crud_user.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )

        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar usuário"
        )


@user_router.put("/{user_id}", response_model=schemas_user.User)
def update_user_by_id(
    user_id: int,
    user: schemas_user.UserUpdate,
    db: Session = Depends(get_db), 
    current_user: schemas_user.User = Depends(security.get_current_user)
):
    """
    Update a user by ID.

    Args:
        user_id: ID of the user to update
        user: Updated user data

    Returns:
        Updated user

    Raises:
        HTTPException: If user not found, update fails, or current user is not authorized

    Requires JWT authentication and superuser privileges.
    """
    try:
        # Check if user is superuser
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso restrito a administradores"
            )

        return crud_user.update_user(db, user_id=user_id, user=user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar usuário"
        )


@user_router.post("/activate/{user_id}/{days}", response_model=schemas_user.User)
def activate_user_by_id(
    user_id: int,
    days: int,
    db: Session = Depends(get_db), 
    current_user: schemas_user.User = Depends(security.get_current_user)
):
    """
    Activate a user.

    Args:
        user_id: ID of the user to activate
        days: Days to activate user

    Returns:
        Activated user

    Raises:
        HTTPException: If user not found, activation fails, or current user is not authorized

    Requires JWT authentication and superuser privileges.
    """
    try:
        # Check if user is superuser
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso restrito a administradores"
            )

        return security.activate_user(db=db, user_id=user_id, days=days)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao ativar usuário"
        )


@user_router.post("/deactivate/{user_id}", response_model=schemas_user.User)
def deactivate_user_by_id(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_user: schemas_user.User = Depends(security.get_current_user)
):
    """
    Deactivate a user.

    Args:
        user_id: ID of the user to deactivate

    Returns:
        Deactivated user

    Raises:
        HTTPException: If user not found, deactivation fails, or current user is not authorized

    Requires JWT authentication and superuser privileges.
    """
    try:
        # Check if user is superuser
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso restrito a administradores"
            )

        return security.deactivate_user(db=db, user_id=user_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao desativar usuário"
        )


@user_router.post("/webhook/kirvano")
async def webhook_kirvano(
    request: Request, 
    db: Session = Depends(get_db)
):
    """
    Handle webhook from Kirvano payment system.

    Args:
        request: HTTP request with webhook data

    Returns:
        Confirmation of receipt

    Raises:
        HTTPException: If webhook processing fails
    """
    try:
        # Extract data from request
        body = await request.json()
        query_params = dict(request.query_params)

        logger.info(f"Webhook Kirvano received: body={body}, query_params={query_params}")

        # Process approved payments
        if body.get("status") == "APPROVED":
            email = body.get("customer", {}).get("email")
            payment_type = body.get("type")

            # Determine plan type based on payment
            if payment_type == "ONE_TIME":
                plan = "diario"
            elif payment_type == "RECURRING":
                charge_freq = body.get("plan", {}).get("charge_frequency", "").lower()
                if charge_freq == "weekly":
                    plan = "semanal"
                elif charge_freq == "monthly":
                    plan = "mensal"
                elif charge_freq == "annually":
                    plan = "anual"
                else:
                    plan = "mensal"  # Default fallback
            else:
                plan = "mensal"  # Default fallback

            # Activate user if email is provided
            if email:
                security.activate_user_by_email(db=db, email=email, plan_type=plan)
                logger.info(f"User activated: {email} with plan {plan}")
            else:
                logger.warning("Email not found in webhook body")

        return {"received": True}
    except Exception as e:
        logger.error(f"Error processing Kirvano webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar webhook"
        )


@user_router.get("/webhook/polarium")
async def webhook_polarium(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # Pega dados da URL
        query_params = dict(request.query_params)
        logger.info(f"✅ Webhook polarium recebido com sucesso: {query_params}")

        clickid = query_params.get("clickid", "")
        trader_id = query_params.get("trader_id")

        if not clickid or not trader_id:
            raise HTTPException(status_code=400, detail="ClickID ou trader_id ausente")

        if not clickid.startswith("uid"):
            raise HTTPException(status_code=400, detail="ClickID inválido")

        user_id = int(clickid.replace("uid", ""))

        # Atualiza campo no usuário
        update_schema = schemas_user.UserUpdate(polarium_registered=True)  # ou trader_id=trader_id
        crud_user.update_user(db=db, user_id=user_id, user=update_schema)

        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error processing polarium webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar webhook"
        )
    

@user_router.get("/webhook/avalon")
async def webhook_avalon(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # Pega dados da URL
        query_params = dict(request.query_params)
        logger.info(f"✅ Webhook avalon recebido com sucesso: {query_params}")

        clickid = query_params.get("clickid", "")
        trader_id = query_params.get("trader_id")

        if not clickid or not trader_id:
            raise HTTPException(status_code=400, detail="ClickID ou trader_id ausente")

        if not clickid.startswith("uid"):
            raise HTTPException(status_code=400, detail="ClickID inválido")

        user_id = int(clickid.replace("uid", ""))

        # Atualiza campo no usuário
        update_schema = schemas_user.UserUpdate(avalon_registered=True)  # ou trader_id=trader_id
        crud_user.update_user(db=db, user_id=user_id, user=update_schema)

        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error processing avalon webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar webhook"
        )