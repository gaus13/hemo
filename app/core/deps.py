from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.auth import decode_token
from app.database import get_db
from app.models.user import User


# Extracts the JWT from the Authorization: Bearer <token> header
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Returns the currently authenticated user.
    Raises HTTP 401 if the token is invalid or the user doesn't exist.
    """

    # Step 1: Decode JWT -> user_id
    user_id = decode_token(token)

    # Step 2: Fetch user from database
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    # Step 3: User not found
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    # Step 4: Return User object
    return user