# we will create this three schemas here RegisterRequest, RegisterResponse TokenResponse

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, str
from datetime import datetime

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)  # for now we leave this as string later we will add things like min 8 char and upper case etc


class AuthResponse(BaseModel):
    
   # we would have kept only messg and user_id in case of old method when users have to relogin after registration 
   # but in modern api we keep the user logged in after account creating and no extra login req 
   # user_id: int 
    message: str
    access_token: str
    token_type: str

# Since both /register and /login return almost the same data, 
# we can reuse the same response schema(AuthResponse), else we had two separate 1) RegisterResponse 2) TokenResponse

class LoginRequest(BaseModel):
    email: EmailStr
    password: str    