from connection import Base
from sqlalchemy import Boolean, Column, Integer, String


class SiteOptions(Base):
    """Model for site options."""
    __tablename__ = 'site_options'

    id = Column(Integer, primary_key=True, index=True)
    key_name = Column(String, unique=True, index=True, nullable=False)
    key_value = Column(String, nullable=False)
    type = Column(String, nullable=False)  # e.g., 'string', 'integer', 'boolean'
    description = Column(String, nullable=True)