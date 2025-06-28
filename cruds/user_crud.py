from datetime import datetime
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import user as models_user
from schemas import user as schemas_user
from schemas import bot_options as schemas_bot_options
from cruds import security_crud as crud_security
import pytz

def get_user_by_id(db: Session, user_id: int):
    return db.query(models_user.User).filter(models_user.User.id == user_id).first()


def get_users(db: Session, skip: int = 0, limit: int = 1000000):
    return db.query(models_user.User).offset(skip).limit(limit).all()


def get_user_by_email(db: Session, email: str) -> Optional[models_user.User]:
    return db.query(models_user.User).filter(models_user.User.email == email.lower()).first()


def create_user(db: Session, user: schemas_user.UserCreate) -> models_user.User:
    brasilia_tz = pytz.timezone('America/Sao_Paulo')
    now_brasilia = datetime.now(brasilia_tz)
    db_user = models_user.User(
        complete_name=user.complete_name,
        email=user.email.lower(),
        password=crud_security.get_password_hash(user.password),
        is_superuser=user.is_superuser,
        created_at= now_brasilia,
        is_active=False,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def user_last_login(db: Session, user_id: int) -> models_user.User:
    brasilia_tz = pytz.timezone('America/Sao_Paulo')
    now_brasilia = datetime.now(brasilia_tz)
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    db_user.last_login = now_brasilia
    db.commit()
    return db_user


def update_user(db: Session, user_id: int, user: schemas_user.UserUpdate) -> models_user.User:
    db_user = get_user_by_id(db, user_id)

    update_data = user.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user