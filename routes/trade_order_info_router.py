import logging
import os
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.orm import Session

from schemas import token_data as schemas_token
from connection import get_db
from cruds import security_crud as security
from cruds import trade_order_info_crud as trade_order_info_crud
from schemas import trade_order_info as trade_order_info_schema

# ---- Telegram (python-telegram-bot) ----
# pip install python-telegram-bot>=21.0
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError

logger = logging.getLogger(__name__)

trade_order_info_router = APIRouter()

# ======================
# Config / Helpers TG
# ======================

AVALON_TOKEN = os.getenv("AVALON_TOKEN")
AVALON_CHANNEL = os.getenv("AVALON_CHANNEL")

POLARIUM_TOKEN = os.getenv("POLARIUM_TOKEN")
POLARIUM_CHANNEL = os.getenv("POLARIUM_CHANNEL")

# Cria os bots (assíncronos). Se faltar token, mantém None e loga warning.
BOT_MAP: dict[str, Bot | None] = {
    "avalon": Bot(AVALON_TOKEN) if AVALON_TOKEN else None,
    "polarium": Bot(POLARIUM_TOKEN) if POLARIUM_TOKEN else None,
}

if not AVALON_TOKEN or not AVALON_CHANNEL:
    logger.warning("[Telegram] Variáveis de ambiente faltando para AVALON (token e/ou channel).")
if not POLARIUM_TOKEN or not POLARIUM_CHANNEL:
    logger.warning("[Telegram] Variáveis de ambiente faltando para POLARIUM (token e/ou channel).")

CHANNEL_MAP: dict[str, str | int | None] = {
    # Aceita -100... como int/str ou @username como str
    "avalon": AVALON_CHANNEL,
    "polarium": POLARIUM_CHANNEL,
}

def _parse_chat_id(raw: str | None) -> str | int | None:
    """Converte '-100123...' em int quando aplicável; mantém '@canal' como str."""
    if raw is None:
        return None
    s = str(raw).strip()
    if s.lstrip("-").isdigit():
        try:
            return int(s)
        except ValueError:
            return s
    return s  # pode ser @username

def _resolve_brokers(broker_raw: str) -> List[str]:
    """
    Retorna lista com 'avalon', 'polarium' ou ambos, aceitando:
    'Avalon', 'Polarium', 'Avalon e Polarium', 'Avalon, Polarium', etc.
    """
    if not broker_raw:
        return []

    b = broker_raw.strip().lower()
    # Normaliza separadores
    for sep in [" e ", ",", ";", "|", "/"]:
        b = b.replace(sep, " ")

    parts = [p for p in b.split() if p]
    out = set()
    for p in parts:
        if p.startswith("avalon"):
            out.add("avalon")
        if p.startswith("polarium"):
            out.add("polarium")

    # Frases conhecidas
    if "avalon" in b and "polarium" in b:
        out.update(["avalon", "polarium"])
    return list(out)

async def _tg_send(bot: Bot | None, chat_id: str | int | None, text: str) -> None:
    """Envia mensagem com PTB; loga erros e não interrompe a request."""
    if bot is None or chat_id is None:
        logger.error("[Telegram] Bot ou chat_id não configurados.")
        return
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
    except TelegramError as e:
        # Erros comuns:
        # - Chat not found: bot não foi adicionado ao canal, ID errado ou bot diferente do canal
        # - Forbidden: bot não é admin ou não tem permissão para postar
        logger.error(f"[Telegram] Falha ao enviar: {e!s}")

# Mensagens
def _msg_open(open_data: trade_order_info_schema.OpenTradeOffer) -> str:
    return (
        "🚀 <b>NOVA ENTRADA</b>\n"
        f"• Par: <b>{open_data.trade_pair}</b>\n"
        f"• Timeframe: <b>{open_data.timeframe}</b>\n"
        f"• Direção: <b>{open_data.direction}</b>"
    )

def _msg_close(close_data: trade_order_info_schema.CloseTradeOffer) -> str:
    result_clean = str(close_data.result).strip()
    emoji = "✅" if result_clean.upper() == "WIN" else "❌"
    return f"{emoji} <b>RESULTADO</b>: <b>{result_clean}</b>"

# ======================
# Endpoints CRUD
# ======================

@trade_order_info_router.post("", response_model=trade_order_info_schema.TradeOrderInfo)
def create_trade_order_info(
    trade_order_info: trade_order_info_schema.TradeOrderInfoCreate,
    db: Session = Depends(get_db),
    credentials: HTTPBasicCredentials = Depends(security.get_basic_credentials),
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
            detail="Erro ao criar informação de ordem de negociação",
        )

@trade_order_info_router.get(path="/all/{brokerage_id}", response_model=list[trade_order_info_schema.TradeOrderInfo])
def get_trade_order_infos_by_user_and_brokerage(
    brokerage_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas_token.Token = Depends(security.get_current_user),
):
    """
    Get all trade orders for the current user and brokerage with pagination.

    Requires JWT authentication.
    """
    try:
        trade_orders = trade_order_info_crud.get_trade_order_infos_by_user_and_brokerage(
            db, current_user.id, brokerage_id, skip, limit
        )
        if not trade_orders:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nenhuma ordem de negociação encontrada.",
            )
        return trade_orders
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving all trade orders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar ordens de negociação",
        )

@trade_order_info_router.get("/today/{brokerage_id}", response_model=list[trade_order_info_schema.TradeOrderInfo])
def get_trade_order_info_by_user_id_today(
    brokerage_id: int,
    db: Session = Depends(get_db),
    current_user: schemas_token.Token = Depends(security.get_current_user),
):
    """
    Get all trade orders for the current user for today.

    Requires JWT authentication.
    """
    try:
        trade_orders = trade_order_info_crud.get_trade_order_info_by_user_id_today(
            db, current_user.id, brokerage_id
        )
        if not trade_orders:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nenhuma ordem de negociação encontrada para hoje.",
            )
        return trade_orders
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving trade orders for today: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar ordens de negociação",
        )

@trade_order_info_router.get("/all", response_model=list[trade_order_info_schema.TradeOrderInfo])
def get_trade_order_infos_by_user(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas_token.Token = Depends(security.get_current_user),
):
    """
    Get all trade orders for the current user with pagination.

    Requires JWT authentication.
    """
    try:
        trade_orders = trade_order_info_crud.get_trade_order_infos_by_user(
            db, current_user.id, skip, limit
        )
        if not trade_orders:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nenhuma ordem de negociação encontrada.",
            )
        return trade_orders
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving all trade orders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar ordens de negociação",
        )

@trade_order_info_router.put("/{order_id}", response_model=trade_order_info_schema.TradeOrderInfo)
def update_trade_order_info(
    order_id: str,
    trade_order_info: trade_order_info_schema.TradeOrderInfoUpdate,
    db: Session = Depends(get_db),
    credentials: HTTPBasicCredentials = Depends(security.get_basic_credentials),
):
    """
    Update an existing trade order.

    Requires basic authentication.
    """
    try:
        if order_id != trade_order_info.order_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID da ordem na URL não corresponde ao ID no corpo da requisição",
            )
        return trade_order_info_crud.update_trade_order_info_by_id(db, trade_order_info)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating trade order {order_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar informação de ordem de negociação",
        )

# ======================
# Endpoints Telegram
# ======================

@trade_order_info_router.post("/open", response_model=str)
async def open_trade_offer(
    open_trade_offer: trade_order_info_schema.OpenTradeOffer,
    db: Session = Depends(get_db),
    current_user: schemas_token.Token = Depends(security.get_current_user),
):
    """
    Open a new trade offer and notify Telegram channels according to 'broker'.
    """
    logger.info(f"[OPEN] Recebido: {open_trade_offer}")
    try:
        brokers = _resolve_brokers(open_trade_offer.broker)
        if not brokers:
            logger.warning(f"[OPEN] Broker inválido: '{open_trade_offer.broker}'")
            return Response(content="ok", status_code=status.HTTP_201_CREATED)

        text = _msg_open(open_trade_offer)

        # Envia para cada broker resolvido
        for b in brokers:
            bot = BOT_MAP.get(b)
            chat_id = _parse_chat_id(CHANNEL_MAP.get(b))
            await _tg_send(bot, chat_id, text)

        return Response(content="ok", status_code=status.HTTP_201_CREATED)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erro ao processar /open: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao enviar mensagem de abertura para o Telegram",
        )

@trade_order_info_router.post("/close", response_model=str)
async def close_trade_offer(
    close_trade_offer: trade_order_info_schema.CloseTradeOffer,
    db: Session = Depends(get_db),
    current_user: schemas_token.Token = Depends(security.get_current_user),
):
    """
    Close an existing trade offer and notify Telegram channels according to 'broker'.
    """
    logger.info(f"[CLOSE] Recebido: {close_trade_offer}")
    try:
        brokers = _resolve_brokers(close_trade_offer.broker)
        if not brokers:
            logger.warning(f"[CLOSE] Broker inválido: '{close_trade_offer.broker}'")
            return Response(content="ok", status_code=status.HTTP_201_CREATED)

        text = _msg_close(close_trade_offer)

        for b in brokers:
            bot = BOT_MAP.get(b)
            chat_id = _parse_chat_id(CHANNEL_MAP.get(b))
            await _tg_send(bot, chat_id, text)

        return Response(content="ok", status_code=status.HTTP_201_CREATED)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erro ao processar /close: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao enviar mensagem de resultado para o Telegram",
        )
