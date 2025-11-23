"""User management endpoints for authentication and token operations."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user_schemas import (
    UserSignup,
    UserLogin,
    UserDelete,
    TokensResponse,
    AddTokensRequest,
    AddTokensResponse,
    UserResponse,
    Token,
)
from app.services.user_service import user_service
from app.utils.jwt import create_access_token
from app.utils.dependencies import get_current_user
from app.models.user import User
from app.utils.logger import log_info, log_warning, log_error

router = APIRouter(prefix="", tags=["User Management"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserSignup,
    db: Session = Depends(get_db),
):
    """
    Register a new user.

    Args:
        user_data: Username and password
        db: Database session

    Returns:
        Created user information with token balance (0)
    """
    try:
        user = user_service.create_user(
            db=db,
            username=user_data.username,
            password=user_data.password,
        )
        log_info(f"New user registered", username=user_data.username, tokens=0)
        return UserResponse(username=user.username, tokens=user.tokens)
    except ValueError as e:
        log_warning(f"User registration failed", username=user_data.username, reason=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        log_error(f"User registration error", username=user_data.username, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    db: Session = Depends(get_db),
):
    """
    Login and receive a JWT access token.

    Args:
        user_data: Username and password
        db: Database session

    Returns:
        JWT access token
    """
    # Authenticate user
    user = user_service.authenticate_user(db, user_data.username, user_data.password)

    if not user:
        log_warning(f"Failed login attempt", username=user_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create JWT token
    access_token = create_access_token(data={"sub": user.username})
    log_info(f"User logged in successfully", username=user.username)

    return Token(access_token=access_token, token_type="bearer")


@router.delete("/remove_user", status_code=status.HTTP_200_OK)
async def remove_user(
    user_data: UserDelete,
    db: Session = Depends(get_db),
):
    """
    Delete a user account.

    Args:
        user_data: Username and password for verification
        db: Database session

    Returns:
        Success message
    """
    try:
        user_service.delete_user(
            db=db,
            username=user_data.username,
            password=user_data.password,
        )
        log_info(f"User account deleted", username=user_data.username)
        return {"message": f"User '{user_data.username}' deleted successfully"}
    except ValueError as e:
        log_warning(f"User deletion failed", username=user_data.username, reason=str(e))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        log_error(f"User deletion error", username=user_data.username, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )


@router.get("/tokens", response_model=TokensResponse)
async def get_tokens(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get token balance for the authenticated user (JWT required).

    Args:
        current_user: Authenticated user from JWT token
        db: Database session

    Returns:
        Token balance
    """
    log_info(f"Token balance checked", username=current_user.username, balance=current_user.tokens)
    return TokensResponse(tokens=current_user.tokens)


@router.post("/add_tokens", response_model=AddTokensResponse)
async def add_tokens(
    request: AddTokensRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Add tokens to the authenticated user's account (simulated payment, JWT required).

    Args:
        request: Credit card and amount
        current_user: Authenticated user from JWT token
        db: Database session

    Returns:
        Confirmation with new token balance
    """
    try:
        tokens_added, new_balance = user_service.add_tokens(
            db=db,
            username=current_user.username,
            amount=request.amount,
            credit_card=request.credit_card,
        )

        log_info(f"Tokens purchased", username=current_user.username, amount=tokens_added, new_balance=new_balance, credit_card_last4=request.credit_card[-4:])

        return AddTokensResponse(
            message="Tokens added successfully",
            username=current_user.username,
            tokens_added=tokens_added,
            new_balance=new_balance,
        )
    except ValueError as e:
        log_error(f"Token purchase failed", username=current_user.username, amount=request.amount, reason=str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        log_error(f"Token purchase error", username=current_user.username, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add tokens: {str(e)}"
        )
