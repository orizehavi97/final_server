"""User model for authentication and token management."""
from sqlalchemy import Column, Integer, String
from app.database import Base


class User(Base):
    """User table for authentication and token tracking."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    tokens = Column(Integer, default=0)
