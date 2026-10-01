from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.modules.auth.models import User
from app.modules.likes.schemas import LikeToggleResponse, PostLikesListResponse
from app.modules.likes.service import LikeService

router = APIRouter(prefix="/posts", tags=["Likes"])


@router.post("/{post_id}/like", response_model=LikeToggleResponse)
async def like_post(
    post_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = LikeService(db)
    return await service.like_post(current_user.id, post_id)


@router.delete("/{post_id}/like", response_model=LikeToggleResponse)
async def unlike_post(
    post_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = LikeService(db)
    return await service.unlike_post(current_user.id, post_id)


@router.get("/{post_id}/likes", response_model=PostLikesListResponse)
async def get_post_likes(
    post_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    service = LikeService(db)
    return await service.get_post_likes(post_id, page, page_size)
