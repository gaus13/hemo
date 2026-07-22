from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    AuthResponse,
)
from app.core.security import (
    hash_password,
    verify_password,
)
from app.core.auth import create_access_token


def register(
    db: Session,
    request: RegisterRequest,
):

    existing_user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    hashed_password = hash_password(request.password)

    user = User(
        email=request.email,
        password_hash=hashed_password,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(
        # data={"sub": str(user.id)}
    )

    return AuthResponse(
        message="Account created successfully.",
        access_token=access_token,
        token_type="bearer",
    )


def login(
    db: Session,
    request: LoginRequest,
):

    user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(
        request.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is not active.",
        )

    access_token = create_access_token(
        data={"sub": str(user.id)}
    )

    return AuthResponse(
        message="Login successful.",
        access_token=access_token,
        token_type="bearer",
    )