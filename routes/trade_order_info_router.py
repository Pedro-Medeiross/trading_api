import logging
import os
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import requests

from schemas import token_data as schemas_token
from connection import get_db
from cruds import security_crud as security
from cruds import trade_order_info_crud as trade_order_info_crud
from schemas import trade_order_info as trade_order_info_schema

# -------------------------------------------------------
# Configurações e inicialização
# -------------------------------------------------------
logger = logging.getLogger(__name__)

# Carrega variáveis do .env (se já estiverem no ambiente, não há problema)
load_dotenv()

trade_order_info_router = APIRouter()

# Mapa de configuração de bots/canais do Telegram
TELEGRAM_CONFIG = {
    "avalon": {
        "token": os.getenv("AVALON_TOKEN"),
        "channel": os.getenv("AVALON_CHANNEL"),
    },
    "polarium": {
        "token": os.getenv("POLARIUM_TOKEN"),
        "channel": os.getenv("POLARIUM_CHANNEL"),
    },
}

# Validação simples (apenas loga warning se faltando)
for k, v in TELEGRAM_CONFIG.items():
    if not v.get("token") or not v.get("channel"):
        logger.warning(
            f"[Telegram] Variáveis ausentes para {k}. "
            f"token={'OK' if v.get('token') else 'FALTA'} "
            f"channel={'OK' if v.get('channel') else 'FALTA'}"
        )

# -------------------------------------------------------
# Utilitários de envio Telegram
# -------------------------------------------------------
def _send_telegram_message(token: str, chat_id: str, text: str, parse_mode: str = "HTML") -> None:
    """
    Envia mensagem para um canal/grupo do Telegram via Bot API.
    Requer que o bot seja admin do canal/grupo.
    """
    if not token or not chat_id:
        logger.error("[Telegram] Token ou chat_id ausentes.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True,
    }
    try:
        r = requests.post(url, data=payload, timeout=10)
        if r.status_code != 200:
            logger.error(f"[Telegram] Falha ao enviar (status {r.status_code}): {r.text}")
    except Exception as e:
        logger.exception(f"[Telegram] Exceção ao enviar mensagem: {e}")

def _resolve_brokers(broker_raw: str) -> list[str]:
    """
    Normaliza o campo 'broker' para uma lista com 'avalon', 'polarium' ou ambos.
    Aceita formatos como: "Avalon", "Polarium", "Avalon e Polarium", "Avalon, Polarium", etc.
    """
    if not broker_raw:
        return []

    b = broker_raw.strip().lower()

    # Normaliza separadores comuns para espaço
    for sep in [" e ", ",", ";", "|", "/"]:
        b = b.replace(sep, " ")

    parts = [p for p in b.split() if p]
    normalized = set()

    # Matching flexível
    for p in parts:
        if p.startswith("avalon"):
            normalized.add("avalon")
        if p.startswith("polarium"):
            normalized.add("polarium")

    # Strings conhecidas
    if broker_raw.strip().lower() in ["avalon e polarium", "polarium e avalon"]:
        normalized.update(["avalon", "polarium"])

    # Caso contenha as duas palavras em qualquer ordem
    if "avalon" in b and "polarium" in b:
        normalized.update(["avalon", "polarium"])

    return list(normalized)

def _send_open_to_brokers(open_data: trade_order_info_schema.OpenTradeOffer):
    """
    Monta e envia a mensagem de 'abertura' de trade para os brokers selecionados.
    """
    msg = (
        "🚀 <b>NOVA ENTRADA</b>\n"
        f"• Par: <b>{open_data.trade_pair}</b>\n"
        f"• Timeframe: <b>{open_data.timeframe}</b>\n"
        f"• Direção: <b>{open_data.direction}</b>"
    )

    brokers = _resolve_brokers(open_data.broker)
    if not brokers:
        logger.warning(f"[Telegram] Nenhum broker válido em '{open_data.broker}'")
        return

    for b in brokers:
        cfg = TELEGRAM_CONFIG.get(b)
        if not cfg or not cfg.get("token") or not cfg.get("channel"):
            logger.error(f"[Telegram] Config ausente/inválida para broker '{b}'.")
            continue
        _send_telegram_message(cfg["token"], cfg["channel"], msg)

def _send_close_to_brokers(close_data: trade_order_info_schema.CloseTradeOffer):
    """
    Monta e envia a mensagem de 'resultado' de trade para os brokers selecionados.
    """
    result_clean = str(close_data.result).strip()
    emoji = "✅" if result_clean.upper() == "WIN" else "❌"
    msg = f"{emoji} <b>RESULTADO</b>: <b>{result_clean}</b>"

    brokers = _resolve_brokers(close_data.broker)
    if not brokers:
        logger.warning(f"[Telegram] Nenhum broker válido em '{close_data.broker}'")
        return

    for b in brokers:
        cfg = TELEGRAM_CONFIG.get(b)
        if not cfg or not cfg.get("token") or not cfg.get("channel"):
            logger.error(f"[Telegram] Config ausente/inválida para broker '{b}'.")
            continue
        _send_telegram_message(cfg["token"], cfg["channel"], msg)

# -------------------------------------------------------
# Endpoints existentes (CRUD)
# -------------------------------------------------------
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

    Args:
        brokerage_id: Brokerage ID
        skip: Number of records to skip
        limit: Maximum number of records to return

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

    Args:
        brokerage_id: ID of the brokerage

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

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return

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

    Args:
        order_id: ID of the order to update

    Requires basic authentication.
    """
    try:
        # Garante que o ID do path é o mesmo do corpo
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

# -------------------------------------------------------
# Endpoints de integração com Telegram
# -------------------------------------------------------
@trade_order_info_router.post("/open", response_model=str)
def open_trade_offer(
    open_trade_offer: trade_order_info_schema.OpenTradeOffer,
    db: Session = Depends(get_db),
    current_user: schemas_token.Token = Depends(security.get_current_user),
):
    """
    Open a new trade offer.

    Args:
        open_trade_offer: The trade offer details

    Requires JWT authentication.
    """
    try:
        logger.info(f"[OPEN] Recebido: {open_trade_offer}")
        _send_open_to_brokers(open_trade_offer)
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
def close_trade_offer(
    close_trade_offer: trade_order_info_schema.CloseTradeOffer,
    db: Session = Depends(get_db),
    current_user: schemas_token.Token = Depends(security.get_current_user),
):
    """
    Close an existing trade offer.

    Args:
        close_trade_offer: The trade offer details

    Requires JWT authentication.
    """
    try:
        logger.info(f"[CLOSE] Recebido: {close_trade_offer}")
        _send_close_to_brokers(close_trade_offer)
        return Response(content="ok", status_code=status.HTTP_201_CREATED)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erro ao processar /close: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao enviar mensagem de resultado para o Telegram",
        )
