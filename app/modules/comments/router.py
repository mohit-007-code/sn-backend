from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.modules.auth.models import User
from app.modules.comments.schemas import (
    CommentCreate,
    CommentListResponse,
    CommentResponse,
)
from app.modules.comments.service import CommentService

router = APIRouter(prefix="/posts", tags=["Comments"])


@router.post(
    "/{post_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    post_id: UUID,
    payload: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CommentService(db)
    return await service.create_comment(
        user_id=current_user.id,
        post_id=post_id,
        text=payload.text,
    )


@router.get("/{post_id}/comments", response_model=CommentListResponse)
async def get_post_comments(
    post_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    service = CommentService(db)
    return await service.get_post_comments(
        post_id=post_id,
        page=page,
        page_size=page_size,
    )
