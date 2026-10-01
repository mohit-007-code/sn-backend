from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_current_user_optional
from app.db.session import get_db
from app.modules.auth.models import User
from app.modules.posts.schemas import PostListResponse, PostResponse, ShareResponse
from app.modules.posts.service import PostService

router = APIRouter(
    prefix="/posts",
    tags=["Posts"],
)


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    title: str = Form(...),
    caption: str | None = Form(None),
    image: UploadFile | None = File(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = PostService(db)
    return await service.create_post(
        user_id=current_user.id,
        title=title,
        caption=caption,
        image=image,
    )


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: UUID,
    current_user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    service = PostService(db)
    return await service.get_post(
        post_id=post_id,
        current_user_id=current_user.id if current_user else None,
    )


@router.get("/user/{user_id}", response_model=PostListResponse)
async def get_user_posts(
    user_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    service = PostService(db)
    return await service.get_user_posts(
        user_id=user_id,
        page=page,
        page_size=page_size,
        current_user_id=current_user.id if current_user else None,
    )


@router.post("/{post_id}/share", response_model=ShareResponse)
async def share_post(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = PostService(db)
    return await service.share_post(post_id)


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: UUID,
    title: str | None = Form(None),
    caption: str | None = Form(None),
    image: UploadFile | None = File(None),
    remove_image: bool = Form(False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = PostService(db)
    return await service.update_post(
        post_id=post_id,
        user_id=current_user.id,
        title=title,
        caption=caption,
        image=image,
        remove_image=remove_image,
    )


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = PostService(db)
    await service.delete_post(
        post_id=post_id,
        user_id=current_user.id,
    )