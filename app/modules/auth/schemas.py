from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(... ,min_length=8, max_length=128)

class LoginRequest(BaseModel):
    username_or_email: str = Field(..., min_length=3, max_length=255, description="Username or email address")
    password: str = Field(..., min_length=8, max_length=128)

class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"