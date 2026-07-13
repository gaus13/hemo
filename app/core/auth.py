from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from app.config import settings

def create_access_token(data: dict):
# Create a copy so the original dictionary isn't modified
    to_encode = data.copy()

    # Set expiration time
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    # Add the expiration time to the payload
    to_encode.update({"exp": expire})

    # create and sign the jwt 
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def decode_token(token: str):
