from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.site_options import SiteOptions
from schemas import site_options as schemas_site_options



def get_all_site_options(db: Session, skip: int = 0, limit: int = 100) -> List[schemas_site_options.SiteOptions]:
    try:
        return db.query(SiteOptions).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

def get_site_option_by_name(db: Session, name: str) -> Optional[schemas_site_options.SiteOptions]:
    try:
        return db.query(SiteOptions).filter(SiteOptions.key_name == name).first()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

def update_site_option(db: Session, name: str, value: str) -> schemas_site_options.SiteOptions:
    try:
        site_option = db.query(SiteOptions).filter(SiteOptions.key_name == name).first()
        if not site_option:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site option not found")
        
        # troque 'value' por 'key_value'
        site_option.key_value = value
        db.commit()
        db.refresh(site_option)
        return site_option
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))