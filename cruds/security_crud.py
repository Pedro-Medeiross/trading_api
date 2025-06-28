import os
import secrets
import pytz
import re
import jwt
from typing import Optional
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, HTTPBasicCredentials, HTTPBasic
from dotenv import load_dotenv
from jwt import InvalidTokenError
from connection import SessionLocal
from cruds import user_crud as crud_user
from schemas import token_data as schemas_token


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 6

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

security = HTTPBasic()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db: Session, username: str, password: str):
    email_regex = r'^[\w\.\+\-]+\@[a-zA-Z0-9\-]+\.[a-zA-Z0-9\-\.]+$|^[\w]+$'
    if re.match(email_regex, username):
        if '@' in username:
            user = crud_user.get_user_by_email(db=db, email=username)
            if user and verify_password(password, user.password):
                return user
            else:
                raise HTTPException(status_code=400, detail="E-mail ou senha incorretos")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=6)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Não autenticado/Logado!",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas_token.TokenData(email=email)
    except InvalidTokenError:
        raise credentials_exception
    user = crud_user.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


def get_basic_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, os.getenv('API_USER'))
    correct_password = secrets.compare_digest(credentials.password, os.getenv('API_PASS'))
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_refresh_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Refresh token inválido")
        return email
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expirado")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Erro ao verificar o refresh token")
    

def activate_user(db: Session = Depends(get_db), user_id: int = 0):
    brasilia_tz = pytz.timezone('America/Sao_Paulo')
    now_brasilia = datetime.now(brasilia_tz)
    user = crud_user.get_user_by_id(db, user_id)
    
    if user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    if user.is_active:
        raise HTTPException(status_code=400, detail="Usuário já está ativado")
    
    user.is_active = True
    user.activated_at = now_brasilia
    db.commit()
    db.refresh(user)
    return user


def deactivate_user(db: Session = Depends(get_db), user_id: int = 0):
    user = crud_user.get_user_by_id(db, user_id)
    
    if user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Usuário já está desativado")
    
    user.is_active = False
    user.activated_at = None
    db.commit()
    db.refresh(user)
    return user


def verify_user_activation_to_login(db: Session = Depends(get_db), user_id: int = 0):
    brasilia_tz = pytz.timezone('America/Sao_Paulo')
    now_brasilia = datetime.now(brasilia_tz)

    user = crud_user.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if user.is_superuser:
        return user

    if user.activated_at and user.current_plan:
        plan_days = {
            'diario': 1,
            'semanal': 7,
            'mensal': 30
        }
        dias_ativos = plan_days.get(user.current_plan, 0)
        if dias_ativos > 0 and now_brasilia > user.activated_at + timedelta(days=dias_ativos):
            user.is_active = False
            db.commit()
            raise HTTPException(status_code=403, detail="Plano expirado. Renove sua assinatura.")

    return user


def activate_user_by_email(db: Session, email: str, plan_type: str):
    brasilia_tz = pytz.timezone('America/Sao_Paulo')
    now_brasilia = datetime.now(brasilia_tz)

    user = crud_user.get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    user.is_active = True
    user.activated_at = now_brasilia
    user.current_plan = plan_type

    db.commit()
    db.refresh(user)
    return user