from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.modules.auth.models import User
from app.modules.auth.schemas import LoginRequest, RegisterRequest
from app.modules.auth.repository import UserRepository

class AuthService:
    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)

    async def register(self, data: RegisterRequest) -> User:
        username = data.username.strip().lower()
        email = data.email.strip().lower()

        existing_username = await self.repository.get_by_username(username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exist"
            )

        existing_email = await self.repository.get_by_email(email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exist"
            )

        hashed_password = hash_password(data.password)
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password
        )
        create_user = await self.repository.create(user)
        await self.repository.db.commit()
        await self.repository.db.refresh(create_user)

        return create_user

    async def login(self, data: LoginRequest) -> dict:
        login_value  = data.username_or_email.strip().lower()

        user = await self.repository.get_username_or_email(login_value)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username/email or password"
            )
        
        if not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username/email or password",
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive",
            )

        access_token = create_access_token(
            subject=str(user.id)
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }