from fastapi import APIRouter
from schemas import bot_options as schemas_bot_options
from schemas import token_data as schemas_token
from sqlalchemy.orm import Session
from connection import SessionLocal
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasicCredentials, OAuth2PasswordRequestForm
from cruds import security_crud as security
from cruds import bot_options_crud as crud_bot_options
from datetime import timedelta

bot_options_router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@bot_options_router.get("/bot-options", response_model=schemas_bot_options.BotOptions, dependencies=[Depends(security.get_current_user)])
async def read_bot_options(current_user: schemas_token.Token = Depends(security.get_current_user), db: Session = Depends(get_db)):
    """
    Retorna as opções do bot para o usuário logado através do token JWT.
    Se as opções não existirem, retorna um erro 404.
    """
    bot_options = crud_bot_options.get_bot_options_by_user_id(db, current_user.id)
    if not bot_options:
        raise HTTPException(status_code=404, detail="Bot options not found")
    return bot_options

@bot_options_router.put("/bot-options", response_model=schemas_bot_options.BotOptions, dependencies=[Depends(security.get_current_user)])
async def update_bot_options(bot_options: schemas_bot_options.BotOptionsUpdate, current_user: schemas_token.Token = Depends(security.get_current_user), db: Session = Depends(get_db)):
    """
    Atualiza as opções do bot para o usuário logado através do token JWT.
    Se as opções não existirem, retorna um erro 404.
    """
    return crud_bot_options.update_bot_options(db, current_user.id, bot_options)