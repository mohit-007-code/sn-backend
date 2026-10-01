from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.storage import save_image
from app.db.session import get_db
from app.modules.auth.models import User
from app.modules.users.schemas import (
    FollowResponse,
    FollowUserListResponse,
    UserMeResponse,
    UserProfileUpdate,
)
from app.modules.users.service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserMeResponse)
async def get_me(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return current_user

@router.patch("/me")
async def update_me( full_name: str | None = Form(None),
    bio: str | None = Form(None),
    profile_photo: UploadFile | None = File(None),
    banner_photo: UploadFile | None = File(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    if current_user.profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found",
        )
    
    if full_name is not None:
        current_user.profile.full_name = full_name

    if bio is not None:
        current_user.profile.bio = bio

    if profile_photo is not None:
        current_user.profile.profile_photo_url = await save_image(profile_photo)

    if banner_photo is not None:
        current_user.profile.banner_photo_url = await save_image(banner_photo)

    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.post("/{user_id}/follow", response_model=FollowResponse)
async def follow_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    return await service.follow_user(current_user.id, user_id)


@router.delete("/{user_id}/follow", response_model=FollowResponse)
async def unfollow_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    return await service.unfollow_user(current_user.id, user_id)


@router.get("/{user_id}/followers", response_model=FollowUserListResponse)
async def get_followers(
    user_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    return await service.get_followers(user_id, page, page_size)


@router.get("/{user_id}/following", response_model=FollowUserListResponse)
async def get_following(
    user_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    return await service.get_following(user_id, page, page_size)