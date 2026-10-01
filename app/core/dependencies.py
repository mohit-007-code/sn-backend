from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.core.security import verify_access_token
from app.modules.auth.models import User

security = HTTPBearer()
security_optional = HTTPBearer(auto_error=False)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: AsyncSession = Depends(get_db)):
    token = credentials.credentials

    try:
        payload = verify_access_token(token)
        user_id = UUID(payload["sub"])

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    result = await db.execute(
    select(User)
    .options(selectinload(User.profile))
    .where(User.id == user_id)
    )

    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    return user


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_optional),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    if not credentials:
        return None

    try:
        payload = verify_access_token(credentials.credentials)
        user_id = UUID(payload["sub"])
    except Exception:
        return None

    result = await db.execute(
        select(User)
        .options(selectinload(User.profile))
        .where(User.id == user_id)
    )

    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        return None

    return user

