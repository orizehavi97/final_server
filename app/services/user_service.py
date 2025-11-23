"""User service for user management and authentication."""
from sqlalchemy.orm import Session
from typing import Optional

from app.models.user import User
from app.utils.auth import hash_password, verify_password


class UserService:
    """Service for user management operations."""

    def create_user(self, db: Session, username: str, password: str) -> User:
        """
        Create a new user with hashed password.

        Args:
            db: Database session
            username: Username
            password: Plain text password

        Returns:
            Created user object

        Raises:
            ValueError: If username already exists
        """
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            raise ValueError(f"Username '{username}' already exists")

        # Create new user with hashed password
        hashed_password = hash_password(password)
        new_user = User(
            username=username,
            hashed_password=hashed_password,
            tokens=0  # Start with 0 tokens
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    def authenticate_user(self, db: Session, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user by username and password.

        Args:
            db: Database session
            username: Username
            password: Plain text password

        Returns:
            User object if authentication successful, None otherwise
        """
        user = db.query(User).filter(User.username == username).first()

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user

    def delete_user(self, db: Session, username: str, password: str) -> bool:
        """
        Delete a user after verifying password.

        Args:
            db: Database session
            username: Username
            password: Plain text password

        Returns:
            True if user deleted, False if authentication failed

        Raises:
            ValueError: If user not found
        """
        user = self.authenticate_user(db, username, password)

        if not user:
            raise ValueError("Invalid username or password")

        db.delete(user)
        db.commit()

        return True

    def get_user_tokens(self, db: Session, username: str) -> int:
        """
        Get the token balance for a user.

        Args:
            db: Database session
            username: Username

        Returns:
            Number of tokens

        Raises:
            ValueError: If user not found
        """
        user = db.query(User).filter(User.username == username).first()

        if not user:
            raise ValueError(f"User '{username}' not found")

        return user.tokens

    def add_tokens(
        self,
        db: Session,
        username: str,
        amount: int,
        credit_card: str
    ) -> tuple[int, int]:
        """
        Add tokens to a user's account.

        Args:
            db: Database session
            username: Username
            amount: Number of tokens to add
            credit_card: Credit card number (validated format)

        Returns:
            Tuple of (tokens_added, new_balance)

        Raises:
            ValueError: If user not found
        """
        user = db.query(User).filter(User.username == username).first()

        if not user:
            raise ValueError(f"User '{username}' not found")

        # In a real system I would implement credit card logic here

        # Add tokens
        user.tokens += amount
        db.commit()
        db.refresh(user)

        return amount, user.tokens

    def deduct_tokens(self, db: Session, username: str, amount: int) -> bool:
        """
        Deduct tokens from a user's account.

        Args:
            db: Database session
            username: Username
            amount: Number of tokens to deduct

        Returns:
            True if tokens deducted successfully

        Raises:
            ValueError: If user not found or insufficient tokens
        """
        user = db.query(User).filter(User.username == username).first()

        if not user:
            raise ValueError(f"User '{username}' not found")

        if user.tokens < amount:
            raise ValueError(f"Insufficient tokens. Required: {amount}, Available: {user.tokens}")

        user.tokens -= amount
        db.commit()

        return True

    def get_user_by_username(self, db: Session, username: str) -> Optional[User]:
        """
        Get user by username.

        Args:
            db: Database session
            username: Username

        Returns:
            User object if found, None otherwise
        """
        return db.query(User).filter(User.username == username).first()


# Singleton instance
user_service = UserService()
