"""Admin user model - for admin panel login."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func

from app.db.base import Base


class AdminUser(Base):
    """Admin user - can log in to admin panel with username and password."""

    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
