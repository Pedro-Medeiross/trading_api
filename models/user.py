from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from connection import Base

class User(Base):
    """SQLAlchemy model for users table."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    complete_name = Column(String(250), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(150), nullable=False)
    is_superuser = Column(Boolean(), default=False, nullable=False)
    is_active = Column(Boolean(), default=False, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    activated_at = Column(DateTime(timezone=True), nullable=True)
    current_plan = Column(String(100), nullable=True)
    phone_number = Column(String(100), nullable=True)
    polarium_registered = Column(Boolean(), default=False, nullable=False)

    # Relationships
    brokerages = relationship("UserBrokerages", back_populates="user", cascade="all, delete-orphan")
    bot_options = relationship("BotOptions", backref="user", cascade="all, delete-orphan")
    trade_orders = relationship("TradeOrderInfo", backref="user", cascade="all, delete-orphan")

    def __repr__(self):
        """String representation of the User object."""
        return f"<User(id={self.id}, email='{self.email}', name='{self.complete_name}')>"
