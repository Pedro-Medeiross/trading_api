from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from connection import Base


class UserBrokerages(Base):
    """SQLAlchemy model for user_brokerages table."""
    __tablename__ = "user_brokerages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    brokerage_id = Column(Integer, ForeignKey("brokerages.id", ondelete="CASCADE"), nullable=False, index=True)
    api_key = Column(String, nullable=True)
    brokerage_username = Column(String, nullable=True)
    brokerage_password = Column(String, nullable=True)

    # Relationships
    user = relationship("User", back_populates="brokerages")
    brokerage = relationship("Brokerages", back_populates="user_brokerages")

    # Ensure a user can only connect to a brokerage once
    __table_args__ = (
        UniqueConstraint('user_id', 'brokerage_id', name='uq_user_brokerage'),
    )

    def __repr__(self):
        """String representation of the UserBrokerages object."""
        return f"<UserBrokerages(id={self.id}, user_id={self.user_id}, brokerage_id={self.brokerage_id})>"
