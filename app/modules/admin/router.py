from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_admin
from app.db.session import get_db
from app.modules.admin.schemas import (
    AdminCommentListResponse,
    AdminDashboardAnalytics,
    AdminPostListResponse,
    AdminUserListResponse,
    CreateAdminRequest,
)
from app.modules.admin.service import AdminService
from app.modules.auth.models import User
from app.modules.users.schemas import UserMeResponse

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/analytics", response_model=AdminDashboardAnalytics)
async def get_analytics(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = AdminService(db)
    return await service.get_dashboard_analytics()


@router.get("/users", response_model=AdminUserListResponse)
async def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = AdminService(db)
    return await service.get_users(page=page, page_size=page_size, search=search)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = AdminService(db)
    await service.delete_user(user_id=user_id, current_admin_id=admin.id)


@router.get("/posts", response_model=AdminPostListResponse)
async def get_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = AdminService(db)
    return await service.get_posts(page=page, page_size=page_size, search=search)


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: UUID,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = AdminService(db)
    await service.delete_post(post_id=post_id)


@router.get("/comments", response_model=AdminCommentListResponse)
async def get_comments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = AdminService(db)
    return await service.get_comments(page=page, page_size=page_size, search=search)


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: UUID,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = AdminService(db)
    await service.delete_comment(comment_id=comment_id)


@router.post("/create-admin", response_model=UserMeResponse, status_code=status.HTTP_201_CREATED)
async def create_admin_user(
    data: CreateAdminRequest,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = AdminService(db)
    return await service.create_admin(data)
