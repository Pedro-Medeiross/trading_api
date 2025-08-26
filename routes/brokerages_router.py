import logging
import os
import base64
import aiohttp
from typing import Literal, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from schemas import brokerages as schemas_brokerages
from schemas import user as schemas_user
from sqlalchemy.orm import Session
from connection import get_db
from cruds import security_crud as security
from cruds import brokerages_crud as crud_brokerages

# Configure logging
logger = logging.getLogger(__name__)

brokerages_router = APIRouter()

HB_LOGIN_URL  = "https://bot-account-manager-api.homebroker.com/v3/login"
HB_WALLET_URL = "https://bot-wallet-api.homebroker.com/balance/"

# >>> credenciais do APP via ambiente (OBRIGATÓRIO)
APP_LOGIN    = os.getenv("HB_APP_LOGIN")
APP_PASSWORD = os.getenv("HB_APP_PASSWORD")


def _require_app_creds():
    if not APP_LOGIN or not APP_PASSWORD:
        raise RuntimeError("As credenciais HB_APP_LOGIN / HB_APP_PASSWORD não foram definidas no .env")

def _basic_header(login: str, password: str) -> str:
    token = base64.b64encode(f"{login}:{password}".encode()).decode()
    return f"Basic {token}"

async def hb_login(session: aiohttp.ClientSession, username: str, password: str) -> str:
    """
    Faz login no HomeBroker usando Basic do APP + credenciais do usuário.
    Retorna access_token.
    """
    _require_app_creds()
    headers = {
        "Content-Type": "application/json",
        "Authorization": _basic_header(APP_LOGIN, APP_PASSWORD),
    }
    payload = {"username": username, "password": password, "role": "hbb"}

    async with session.post(HB_LOGIN_URL, json=payload, headers=headers) as resp:
        if resp.status != 200:
            text = await resp.text()
            raise HTTPException(status_code=resp.status, detail=text)
        data = await resp.json()
        token = data.get("access_token") or data.get("accessToken")
        if not token:
            raise HTTPException(status_code=500, detail="Token não encontrado na resposta")
        return token

async def hb_get_balance(
    session: aiohttp.ClientSession,
    access_token: str,
    account_type: Literal["demo", "real"] = "demo",
) -> Optional[int]:
    headers = {"Authorization": f"Bearer {access_token}"}
    async with session.get(HB_WALLET_URL, headers=headers) as resp:
        if resp.status != 200:
            text = await resp.text()
            raise HTTPException(status_code=resp.status, detail=text)
        data = await resp.json()
        wallet = data.get(account_type) or {}
        return wallet.get("balance")


@brokerages_router.get("", response_model=list[schemas_brokerages.Brokerages])
def get_brokerages_for_current_user(
    db: Session = Depends(get_db), 
    current_user: schemas_user.User = Depends(security.get_current_user)
):
    """
    Get all brokerages for the current user.

    Returns:
        List of brokerages for the current user

    Raises:
        HTTPException: If retrieval fails

    Requires JWT authentication.
    """
    try:
        return crud_brokerages.get_brokerages(db)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving brokerages for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar corretoras"
        )


@brokerages_router.post("", response_model=schemas_brokerages.Brokerages)
def create_brokerage(
    brokerage: schemas_brokerages.BrokeragesCreate, 
    db: Session = Depends(get_db), 
    current_user: schemas_user.User = Depends(security.get_current_user)
):
    """
    Create a new brokerage.

    Args:
        brokerage: Brokerage data

    Returns:
        Created brokerage

    Raises:
        HTTPException: If creation fails

    Requires JWT authentication.
    """
    try:
        return crud_brokerages.create_brokerage(db, brokerage)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating brokerage: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar corretora"
        )


@brokerages_router.get("/{brokerage_id}", response_model=schemas_brokerages.Brokerages)
def get_brokerage_by_id(
    brokerage_id: int, 
    db: Session = Depends(get_db), 
    current_user: schemas_user.User = Depends(security.get_current_user)
):
    """
    Get a brokerage by ID.

    Args:
        brokerage_id: ID of the brokerage

    Returns:
        Brokerage with the specified ID

    Raises:
        HTTPException: If brokerage not found or retrieval fails

    Requires JWT authentication.
    """
    try:
        brokerage = crud_brokerages.get_brokerage_by_id(db, brokerage_id)
        if not brokerage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Corretora não encontrada"
            )
        return brokerage
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving brokerage {brokerage_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar corretora"
        )


@brokerages_router.put("/{brokerage_id}", response_model=schemas_brokerages.Brokerages)
def update_brokerage(
    brokerage_id: int, 
    brokerage: schemas_brokerages.BrokeragesUpdate, 
    db: Session = Depends(get_db), 
    current_user: schemas_user.User = Depends(security.get_current_user)
):
    """
    Update a brokerage.

    Args:
        brokerage_id: ID of the brokerage to update
        brokerage: Updated brokerage data

    Returns:
        Updated brokerage

    Raises:
        HTTPException: If brokerage not found or update fails

    Requires JWT authentication.
    """
    try:
        return crud_brokerages.update_brokerage(db, brokerage_id, brokerage)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating brokerage {brokerage_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar corretora"
        )


@brokerages_router.delete("/{brokerage_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_brokerage(
    brokerage_id: int, 
    db: Session = Depends(get_db), 
    current_user: schemas_user.User = Depends(security.get_current_user)
):
    """
    Delete a brokerage.

    Args:
        brokerage_id: ID of the brokerage to delete

    Returns:
        No content

    Raises:
        HTTPException: If brokerage not found or deletion fails

    Requires JWT authentication.
    """
    try:
        result = crud_brokerages.delete_brokerage(db, brokerage_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Corretora não encontrada"
            )
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting brokerage {brokerage_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao excluir corretora"
        )


@brokerages_router.get("/user/{user_id}", response_model=list[schemas_brokerages.Brokerages])
def get_brokerages_by_user_id(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_user: schemas_user.User = Depends(security.get_current_user)
):
    """
    Get all brokerages for a specific user.

    Args:
        user_id: ID of the user

    Returns:
        List of brokerages for the specified user

    Raises:
        HTTPException: If retrieval fails

    Requires JWT authentication.
    """
    try:
        # Check if current user is admin or the requested user
        if not current_user.is_superuser and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Não autorizado a acessar corretoras de outro usuário"
            )

        return crud_brokerages.get_brokerages_by_user_id(db, user_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving brokerages for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar corretoras do usuário"
        )


# ----------------- ROTAS -----------------

@brokerages_router.post("/login")
async def login(user_email: str, user_password: str):
    """
    Faz login no broker e retorna o access_token
    """
    async with aiohttp.ClientSession() as session:
        token = await hb_login(session, user_email, user_password)
        return {"access_token": token}

@brokerages_router.get("/balance")
async def get_balance(user_email: str, user_password: str, account_type: Literal["demo","real"]="demo"):
    """
    Faz login e retorna apenas o saldo da conta demo ou real
    """
    async with aiohttp.ClientSession() as session:
        token = await hb_login(session, user_email, user_password)
        balance = await hb_get_balance(session, token, account_type)
        return {"account_type": account_type, "balance": balance}