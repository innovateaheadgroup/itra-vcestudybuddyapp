from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def _create_token(data: dict[str, Any], expires_delta: timedelta, secret_key: str) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(subject: str) -> str:
    return _create_token(
        data={"sub": subject, "type": "access"},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        secret_key=settings.jwt_secret_key,
    )


def create_refresh_token(subject: str) -> str:
    return _create_token(
        data={"sub": subject, "type": "refresh"},
        expires_delta=timedelta(minutes=settings.refresh_token_expire_minutes),
        secret_key=settings.jwt_refresh_secret_key,
    )


def decode_token(token: str, refresh: bool = False) -> dict[str, Any]:
    secret_key = settings.jwt_refresh_secret_key if refresh else settings.jwt_secret_key
    try:
        return jwt.decode(token, secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:  # pragma: no cover - exercised by auth flow
        raise ValueError("Invalid token") from exc
