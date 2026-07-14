from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.auth import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    AuthResponse
)
from app.core.security import (
    hash_password,
    verify_password
)
from app.core.auth import create_access_token
from app.database import get_db
from app.models import User

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED
)

def register(request: RegisterRequest, db: Session = Depends(get_db)):

    # 1. Check if the email is already registered
    existing_user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    # hashed the password using the hash function written in security.py
    hashed_password = hash_password(request.password)

    user = User(
        email = request.email,
        password_hash = hashed_password,
        is_active = True
    )
    # 4. Save the user to the database
    db.add(user)
    db.commit()
    db.refresh(user)

    # creating jwt token for the new added user
    access_token = create_access_token(
        subject = str(user.id)
    )

    return AuthResponse(
        message="Account created successfully.",
        access_token = access_token,
        token_type = "bearer"
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK
)

def login(request: LoginRequest, db: Session = Depends(get_db)):
    # find user my email
    user = (
        db.query(User)
        .filter(User.email == request.email)
        .filter()
    )

    # Check if user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # verify password
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # checking if the account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your Account is not active "
        )
    
    # Generate jwt
    access_token = create_access_token(subject = str(user.id))

    # Return response 
    return AuthResponse(
        message="Login successful",
        access_token=access_token,
        token_type="bearer"
    )