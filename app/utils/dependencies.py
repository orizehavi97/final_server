"""FastAPI dependencies for authentication and rate limiting."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.jwt import verify_token
from app.services.user_service import user_service
from app.models.user import User
from app.utils.rate_limiter import rate_limiter

# HTTP Bearer token authentication scheme
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token.

    Args:
        credentials: HTTP Authorization credentials with Bearer token
        db: Database session

    Returns:
        User object

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials

    # Verify and decode token
    username = verify_token(token)

    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    user = user_service.get_user_by_username(db, username)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_user_with_rate_limit(
    user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get current user and apply rate limiting.

    Args:
        user: Authenticated user

    Returns:
        User object

    Raises:
        HTTPException: If rate limit exceeded
    """
    # Apply rate limiting
    rate_limiter.record_request(user.username)

    return user
