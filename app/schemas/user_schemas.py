"""Pydantic schemas for user authentication and management."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re


class UserSignup(BaseModel):
    """Schema for user registration."""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=4)


class UserLogin(BaseModel):
    """Schema for user login."""

    username: str
    password: str


class UserDelete(BaseModel):
    """Schema for user deletion."""

    username: str
    password: str


class TokensResponse(BaseModel):
    """Schema for tokens balance response."""

    tokens: int


class AddTokensRequest(BaseModel):
    """Schema for adding tokens to user account (JWT authenticated)."""

    credit_card: str = Field(..., description="Credit card number in format: XXXX-XXXX-XXXX-XXXX")
    amount: int = Field(..., gt=0, description="Number of tokens to add (must be positive)")

    @field_validator('credit_card')
    @classmethod
    def validate_credit_card(cls, v: str) -> str:
        """Validate credit card format: XXXX-XXXX-XXXX-XXXX."""
        # Remove spaces if any
        v = v.replace(" ", "")

        # Check format with dashes
        pattern = r'^\d{4}-\d{4}-\d{4}-\d{4}$'
        if not re.match(pattern, v):
            raise ValueError('Credit card must be in format: XXXX-XXXX-XXXX-XXXX')

        return v


class AddTokensResponse(BaseModel):
    """Schema for add tokens response."""

    message: str
    username: str
    tokens_added: int
    new_balance: int


class UserResponse(BaseModel):
    """Schema for user information response."""

    username: str
    tokens: int

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Schema for token payload data."""

    username: Optional[str] = None
