from fastapi import APIRouter
from schemas import user as schemas_user
from schemas import token_data as schemas_token
from sqlalchemy.orm import Session
from connection import SessionLocal
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasicCredentials, OAuth2PasswordRequestForm
from cruds import security_crud as security
from cruds import user_crud as crud_user
from datetime import timedelta

user_router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@user_router.get("/me", response_model=schemas_user.User, dependencies=[Depends(security.get_current_user)])
async def read_users_me(current_user: schemas_user.User = Depends(security.get_current_user)):
    """Retorna o usuário logado através do token JWT."""
    return current_user


@user_router.post("/login", response_model=schemas_token.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Loga o usuário e retorna um token JWT e refresh token."""
    user = security.authenticate_user(db, form_data.email, form_data.password)
    if user:
        access_token_expires = timedelta(hours=12)
        access_token = security.create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        refresh_token_expires = timedelta(days=30)
        refresh_token = security.create_refresh_token(
            data={"sub": user.email}, expires_delta=refresh_token_expires
        )
        crud_user.user_last_login(db, user.id)
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    
    
@user_router.post("/refresh", response_model=schemas_token.Token)
async def refresh_access_token(refresh_token: str = Depends(security.oauth2_scheme)):
    """Usa o refresh token para gerar um novo access token."""
    username = security.verify_refresh_token(refresh_token)
    access_token_expires = timedelta(hours=6)
    access_token = security.create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@user_router.post("/create", response_model=schemas_user.User)
async def create_user(user: schemas_user.UserCreate, db: Session = Depends(get_db), credentials: HTTPBasicCredentials = Depends(security.get_basic_credentials)):
    """Cria um novo usuário."""
    db_user = crud_user.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Funcionário com este email já existe")
    return crud_user.create_user(db=db, user=user)