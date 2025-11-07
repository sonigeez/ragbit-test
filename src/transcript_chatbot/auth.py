"""
Authentication and authorization utilities.
"""
from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config.settings import settings
from src.transcript_chatbot.logger import logger
from src.transcript_chatbot.models import User


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bearer token security
security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        user_id: The user ID to encode in the token
        expires_delta: Optional expiration time delta

    Returns:
        Encoded JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )

    to_encode = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    logger.info(f"Created access token for user {user_id}")
    return encoded_jwt


def decode_access_token(token: str) -> str:
    """
    Decode and verify a JWT access token.

    Args:
        token: The JWT token to decode

    Returns:
        The user ID from the token

    Raises:
        HTTPException: If the token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        return user_id
    except jwt.ExpiredSignatureError:
        logger.warning("Expired token received")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> str:
    """
    Get the current user from the authorization header.

    Args:
        credentials: The HTTP authorization credentials

    Returns:
        The user ID

    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    user_id = decode_access_token(token)
    return user_id


# In-memory user store (replace with database in production)
_users_db: dict[str, dict] = {}


def create_user(email: str, username: str, password: str) -> User:
    """
    Create a new user.

    Args:
        email: User email
        username: Username
        password: Plain text password (will be hashed)

    Returns:
        Created user

    Raises:
        ValueError: If user already exists
    """
    if email in _users_db:
        raise ValueError(f"User with email {email} already exists")

    user = User(email=email, username=username)
    _users_db[email] = {
        "user": user,
        "hashed_password": hash_password(password),
    }

    logger.info(f"Created new user: {username} ({email})")
    return user


def authenticate_user(email: str, password: str) -> Optional[User]:
    """
    Authenticate a user.

    Args:
        email: User email
        password: Plain text password

    Returns:
        User if authentication succeeds, None otherwise
    """
    user_data = _users_db.get(email)
    if not user_data:
        return None

    if not verify_password(password, user_data["hashed_password"]):
        return None

    logger.info(f"User authenticated: {email}")
    return user_data["user"]


def get_user_by_id(user_id: str) -> Optional[User]:
    """
    Get a user by their ID.

    Args:
        user_id: The user ID

    Returns:
        User if found, None otherwise
    """
    for user_data in _users_db.values():
        if user_data["user"].id == user_id:
            return user_data["user"]
    return None
