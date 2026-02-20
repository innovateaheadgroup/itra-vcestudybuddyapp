from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.models.models import PasswordResetToken, User
from app.schemas import (
    AuthTokenPair,
    LoginRequest,
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    RefreshRequest,
    RegisterRequest,
    UserOut,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthTokenPair, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> AuthTokenPair:
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email, password_hash=get_password_hash(payload.password), role=payload.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return AuthTokenPair(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.post("/login", response_model=AuthTokenPair)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthTokenPair:
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return AuthTokenPair(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.post("/refresh", response_model=AuthTokenPair)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> AuthTokenPair:
    try:
        decoded = decode_token(payload.refresh_token, refresh=True)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid refresh token") from exc

    if decoded.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = decoded.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token subject")
    user = db.scalar(select(User).where(User.id == int(user_id)))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return AuthTokenPair(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.post("/password-reset/request")
def request_password_reset(payload: PasswordResetRequest, db: Session = Depends(get_db)) -> dict:
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user:
        return {"message": "If the account exists, a reset email has been sent."}

    token = str(uuid4())
    reset = PasswordResetToken(
        user_id=user.id,
        token=token,
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    db.add(reset)
    db.commit()

    # Email stub for MVP.
    return {
        "message": "Password reset link generated (email provider stubbed).",
        "reset_token_stub": token,
    }


@router.post("/password-reset/confirm")
def confirm_password_reset(
    payload: PasswordResetConfirmRequest, db: Session = Depends(get_db)
) -> dict:
    token = db.scalar(select(PasswordResetToken).where(PasswordResetToken.token == payload.token))
    if not token:
        raise HTTPException(status_code=404, detail="Reset token not found")
    if token.used_at:
        raise HTTPException(status_code=400, detail="Reset token already used")
    if token.expires_at < datetime.now(UTC):
        raise HTTPException(status_code=400, detail="Reset token expired")

    user = db.scalar(select(User).where(User.id == token.user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.password_hash = get_password_hash(payload.new_password)
    token.used_at = datetime.now(UTC)
    db.commit()
    return {"message": "Password updated successfully"}


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(current_user)
