from fastapi import APIRouter, Depends, HTTPException, status, Request
from schemas import site_options as schemas_site_options
from schemas import token_data as schemas_token
from sqlalchemy.orm import Session
from connection import get_db
from fastapi.security import HTTPBasicCredentials, OAuth2PasswordRequestForm
from cruds import security_crud as security
from cruds import site_options_crud as cruds_site_options
from typing import List, Optional
from schemas import user as schemas_user

site_options_router = APIRouter()


@site_options_router.get("/all", response_model=List[schemas_site_options.SiteOptions])
def get_all_site_options(db: Session = Depends(get_db), skip: int = 0, limit: int = 100, current_user: schemas_user.User = Depends(security.get_current_user)):
    """
    Get all site options.
    """
    try:
        return cruds_site_options.get_all_site_options(db, skip=skip, limit=limit)
    except HTTPException as e:
        raise e

@site_options_router.get("/{name}", response_model=schemas_site_options.SiteOptions)
def get_site_option_by_name(name: str, db: Session = Depends(get_db), current_user: schemas_user.User = Depends(security.get_current_user)):
    """
    Get a site option by its name.
    
    Args:
        name: The name of the site option.
    
    Returns:
        The site option if found, raises HTTPException if not found or on error.
    """
    try:
        site_option = cruds_site_options.get_site_option_by_name(db, name)
        if not site_option:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site option not found")
        return site_option
    except HTTPException as e:
        raise e
    

@site_options_router.put("/{name}", response_model=schemas_site_options.SiteOptions)
def update_site_option(name: str, value: str, db: Session = Depends(get_db), current_user: schemas_user.User = Depends(security.get_current_user)):
    """
    Update a site option by its name.
    
    Args:
        name: The name of the site option.
        value: The new value for the site option.
    
    Returns:
        The updated site option if successful, raises HTTPException on error.
    """
    try:
        return cruds_site_options.update_site_option(db, name, value)
    except HTTPException as e:
        raise e

