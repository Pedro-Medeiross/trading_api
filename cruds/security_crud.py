import os
import secrets
import pytz
import re
import jwt
import logging
from typing import Optional, Dict, Any, Union
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi.security import OAuth2PasswordBearer, HTTPBasicCredentials, HTTPBasic
from dotenv import load_dotenv
from jwt import InvalidTokenError, PyJWTError, ExpiredSignatureError
from connection import get_db
from cruds import user_crud as crud_user
from schemas import token_data as schemas_token
from models.user import User

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    logger.warning("SECRET_KEY not found in environment variables. Using a default value for development.")
    SECRET_KEY = "development_secret_key"  # Default for development only

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 6
REFRESH_TOKEN_EXPIRE_DAYS = 30

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/login")

# HTTP Basic authentication
security = HTTPBasic()

# Plan duration mapping
PLAN_DURATIONS = {
    'diario': 1,
    'semanal': 7,
    'mensal': 30,
}


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Authenticate a user by username/email and password.

    Args:
        db: Database session
        username: Username or email
        password: Plain text password

    Returns:
        User object if authentication successful

    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Validate email format
        email_regex = r'^[\w\.\+\-]+\@[a-zA-Z0-9\-]+\.[a-zA-Z0-9\-\.]+$|^[\w]+$'
        if not re.match(email_regex, username):
            raise HTTPException(status_code=400, detail="Formato de e-mail inválido")

        # Check if username is an email
        if '@' in username:
            user = crud_user.get_user_by_email(db=db, email=username)
            if not user:
                raise HTTPException(status_code=400, detail="E-mail ou senha incorretos")

            if not verify_password(password, user.password):
                raise HTTPException(status_code=400, detail="E-mail ou senha incorretos")

            return user
        else:
            # If username authentication is needed, add it here
            raise HTTPException(status_code=400, detail="Autenticação por nome de usuário não suportada")
    except SQLAlchemyError as e:
        logger.error(f"Database error during authentication: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS))
    to_encode.update({"exp": expire, "type": "access"})

    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except PyJWTError as e:
        logger.error(f"Error creating access token: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao criar token de acesso")


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT refresh token.

    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire, "type": "refresh"})

    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except PyJWTError as e:
        logger.error(f"Error creating refresh token: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao criar token de atualização")


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    """
    Get the current user from a JWT token.

    Args:
        db: Database session
        token: JWT token

    Returns:
        User object

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não autenticado/Logado!",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Extract email from token
        email: str = payload.get("sub")
        if not email:
            raise credentials_exception

        # Check token type
        token_type = payload.get("type")
        if token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido para esta operação",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token_data = schemas_token.TokenData(email=email)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenError:
        raise credentials_exception

    # Get user from database
    user = crud_user.get_user_by_email(db, email=token_data.email)
    if not user:
        raise credentials_exception

    return user


def get_basic_credentials(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """
    Validate HTTP Basic authentication credentials.

    Args:
        credentials: HTTP Basic credentials

    Returns:
        Username if authentication successful

    Raises:
        HTTPException: If authentication fails
    """
    api_user = os.getenv('API_USER')
    api_pass = os.getenv('API_PASS')

    if not api_user or not api_pass:
        logger.error("API_USER or API_PASS not set in environment variables")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Configuração de autenticação incompleta",
        )

    correct_username = secrets.compare_digest(credentials.username, api_user)
    correct_password = secrets.compare_digest(credentials.password, api_pass)

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username


def verify_refresh_token(token: str) -> str:
    """
    Verify a refresh token and return the user email.

    Args:
        token: JWT refresh token

    Returns:
        User email

    Raises:
        HTTPException: If token is invalid
    """
    try:
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Extract email from token
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Refresh token inválido")

        # Check token type
        token_type = payload.get("type")
        if token_type != "refresh":
            raise HTTPException(status_code=401, detail="Token inválido para esta operação")

        return email
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expirado")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Erro ao verificar o refresh token")


def activate_user(db: Session, user_id: int, days: int) -> User:
    """
    Activate a user account.

    Args:
        db: Database session
        user_id: User ID
        days: Days to activate

    Returns:
        Updated user object

    Raises:
        HTTPException: If user not found or already active
    """
    try:
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        now_brasilia = datetime.now(brasilia_tz)

        user = crud_user.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        if user.is_active:
            raise HTTPException(status_code=400, detail="Usuário já está ativado")

        if days == 1:
            user.current_plan = 'diario'
        elif days == 7:
            user.current_plan = 'semanal'
        elif days == 30:
            user.current_plan = 'mensal'

        user.is_active = True
        user.activated_at = now_brasilia

        db.commit()
        db.refresh(user)

        return user
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error activating user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao ativar usuário")


def deactivate_user(db: Session, user_id: int) -> User:
    """
    Deactivate a user account.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Updated user object

    Raises:
        HTTPException: If user not found or already inactive
    """
    try:
        user = crud_user.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        if not user.is_active:
            raise HTTPException(status_code=400, detail="Usuário já está desativado")

        user.is_active = False
        user.activated_at = None
        user.current_plan = None

        db.commit()
        db.refresh(user)

        return user
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deactivating user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao desativar usuário")


def verify_user_activation_to_login(db: Session, user_id: int) -> User:
    """
    Verifica se o usuário está ativo e se seu plano ainda é válido.
    Desativa a conta automaticamente se o plano tiver expirado.
    """
    try:
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        now_brasilia = datetime.now(brasilia_tz)

        user = crud_user.get_user_by_id(db, user_id)
        if not user:
            print("❌ Usuário não encontrado no banco de dados.")
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        print(f"🔍 Verificando ativação do usuário: {user.email} (ID: {user.id})")

        if user.is_superuser:
            print("👑 Usuário é superusuário. Ignorando verificação de plano.")
            return user

        if user.activated_at and user.current_plan:
            # Garante que a data de ativação tenha timezone
            activated_at = user.activated_at
            if activated_at.tzinfo is None:
                activated_at = brasilia_tz.localize(activated_at)
            else:
                activated_at = activated_at.astimezone(brasilia_tz)

            dias_ativos = PLAN_DURATIONS.get(user.current_plan.lower())
            if dias_ativos:
                data_expiracao = activated_at + timedelta(days=dias_ativos)
                print(f"📅 Ativado em: {activated_at}")
                print(f"📆 Expira em: {data_expiracao}")
                print(f"🕓 Agora: {now_brasilia}")

                if now_brasilia > data_expiracao:
                    user.is_active = False
                    user.activated_at = None
                    user.current_plan = None
                    db.commit()
                    print("⛔ Plano expirado. Usuário desativado.")
                    raise HTTPException(status_code=403, detail="Plano expirado. Renove sua assinatura.")
            else:
                print(f"⚠️ Plano '{user.current_plan}' não está registrado em PLAN_DURATIONS.")
        else:
            print("⚠️ Usuário sem plano ou data de ativação definida.")

        return user

    except SQLAlchemyError as e:
        db.rollback()
        print(f"❌ Erro de banco ao verificar ativação do usuário: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao verificar ativação do usuário")


def activate_user_by_email(db: Session, email: str, plan_type: str) -> User:
    """
    Activate a user by email and set their plan type.

    Args:
        db: Database session
        email: User email
        plan_type: Plan type (diario, semanal, mensal, anual)

    Returns:
        Updated user object

    Raises:
        HTTPException: If user not found
    """
    try:
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        now_brasilia = datetime.now(brasilia_tz)

        user = crud_user.get_user_by_email(db, email=email)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        # Validate plan type
        if plan_type not in PLAN_DURATIONS:
            logger.warning(f"Invalid plan type: {plan_type}. Defaulting to 'mensal'.")
            plan_type = 'mensal'

        user.is_active = True
        user.activated_at = now_brasilia
        user.current_plan = plan_type

        db.commit()
        db.refresh(user)

        return user
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error activating user by email {email}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao ativar usuário")
