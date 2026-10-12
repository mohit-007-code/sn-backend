from datetime import datetime, timezone
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.enums.user import UserRole
from app.modules.admin.repository import AdminRepository
from app.modules.admin.schemas import (
    AdminCommentItem,
    AdminCommentListResponse,
    AdminDashboardAnalytics,
    AdminPostItem,
    AdminPostListResponse,
    AdminStatsSummary,
    AdminUserItem,
    AdminUserListResponse,
    CreateAdminRequest,
    DailyRegistrationItem,
    MonthlyRegistrationItem,
    TopPostItem,
)
from app.modules.auth.models import User
from app.modules.comments.models import Comment
from app.modules.posts.models import Post
from app.modules.users.models import UserProfile


class AdminService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AdminRepository(db)

    async def get_dashboard_analytics(self) -> AdminDashboardAnalytics:
        total_users = await self.repo.get_total_users()
        active_users = await self.repo.get_active_users_count()
        inactive_users = total_users - active_users
        total_posts = await self.repo.get_total_posts()
        total_comments = await self.repo.get_total_comments()
        total_likes = await self.repo.get_total_likes()

        now = datetime.now(timezone.utc)
        today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
        month_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)

        new_today = await self.repo.get_users_registered_since(today_start)
        new_month = await self.repo.get_users_registered_since(month_start)

        summary = AdminStatsSummary(
            total_users=total_users,
            active_users=active_users,
            inactive_users=inactive_users,
            total_posts=total_posts,
            total_comments=total_comments,
            total_likes=total_likes,
            new_users_today=new_today,
            new_users_this_month=new_month,
        )

        daily_rows = await self.repo.get_daily_registrations(days=14)
        daily_items = [
            DailyRegistrationItem(date=str(row[0]), count=row[1]) for row in daily_rows
        ]

        monthly_rows = await self.repo.get_monthly_registrations(months=6)
        monthly_items = [
            MonthlyRegistrationItem(month=str(row[0]), count=row[1])
            for row in monthly_rows
        ]

        top_by_likes_rows = await self.repo.get_top_posts_by_likes(limit=5)
        top_likes = [
            TopPostItem(
                id=row[0].id,
                title=row[0].title,
                caption=row[0].caption,
                image_url=row[0].image_url,
                author_username=row.author_username,
                author_email=row.author_email,
                created_at=row[0].created_at,
                likes_count=row.likes_count or 0,
                comments_count=row.comments_count or 0,
                share_count=row[0].share_count or 0,
            )
            for row in top_by_likes_rows
        ]

        top_by_comments_rows = await self.repo.get_top_posts_by_comments(limit=5)
        top_comments = [
            TopPostItem(
                id=row[0].id,
                title=row[0].title,
                caption=row[0].caption,
                image_url=row[0].image_url,
                author_username=row.author_username,
                author_email=row.author_email,
                created_at=row[0].created_at,
                likes_count=row.likes_count or 0,
                comments_count=row.comments_count or 0,
                share_count=row[0].share_count or 0,
            )
            for row in top_by_comments_rows
        ]

        return AdminDashboardAnalytics(
            summary=summary,
            daily_registrations=daily_items,
            monthly_registrations=monthly_items,
            top_posts_by_likes=top_likes,
            top_posts_by_comments=top_comments,
        )

    async def get_users(
        self, page: int = 1, page_size: int = 20, search: str | None = None
    ) -> AdminUserListResponse:
        rows, total = await self.repo.get_users_list(
            page=page, page_size=page_size, search=search
        )
        items = []
        for row in rows:
            user = row[0]
            items.append(
                AdminUserItem(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    role=user.role.value if hasattr(user.role, "value") else str(user.role),
                    is_active=user.is_active,
                    created_at=user.created_at,
                    posts_count=row.posts_count or 0,
                    comments_count=row.comments_count or 0,
                    likes_count=row.likes_count or 0,
                    profile_photo_url=user.profile.profile_photo_url if user.profile else None,
                    full_name=user.profile.full_name if user.profile else None,
                )
            )

        return AdminUserListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            has_next=(page * page_size) < total,
        )

    async def get_posts(
        self, page: int = 1, page_size: int = 20, search: str | None = None
    ) -> AdminPostListResponse:
        rows, total = await self.repo.get_posts_list(
            page=page, page_size=page_size, search=search
        )
        items = []
        for row in rows:
            post = row[0]
            items.append(
                AdminPostItem(
                    id=post.id,
                    title=post.title,
                    caption=post.caption,
                    image_url=post.image_url,
                    created_at=post.created_at,
                    author_id=post.user_id,
                    author_username=row.author_username,
                    likes_count=row.likes_count or 0,
                    comments_count=row.comments_count or 0,
                    share_count=post.share_count or 0,
                )
            )

        return AdminPostListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            has_next=(page * page_size) < total,
        )

    async def get_comments(
        self, page: int = 1, page_size: int = 20, search: str | None = None
    ) -> AdminCommentListResponse:
        rows, total = await self.repo.get_comments_list(
            page=page, page_size=page_size, search=search
        )
        items = []
        for row in rows:
            comment = row[0]
            items.append(
                AdminCommentItem(
                    id=comment.id,
                    text=comment.text,
                    created_at=comment.created_at,
                    post_id=comment.post_id,
                    post_title=row.post_title,
                    author_id=comment.user_id,
                    author_username=row.author_username,
                )
            )

        return AdminCommentListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            has_next=(page * page_size) < total,
        )

    async def delete_user(self, user_id: UUID, current_admin_id: UUID) -> None:
        if user_id == current_admin_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admin cannot delete their own account.",
            )
        user = await self.db.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        await self.repo.delete_user(user)

    async def delete_post(self, post_id: UUID) -> None:
        post = await self.db.get(Post, post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found",
            )
        await self.repo.delete_post(post)

    async def delete_comment(self, comment_id: UUID) -> None:
        comment = await self.db.get(Comment, comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found",
            )
        await self.repo.delete_comment(comment)

    async def create_admin(self, data: CreateAdminRequest) -> User:
        username = data.username.strip().lower()
        email = data.email.strip().lower()

        # Check existing
        from app.modules.auth.repository import UserRepository
        auth_repo = UserRepository(self.db)
        if await auth_repo.get_by_username(username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists",
            )
        if await auth_repo.get_by_email(email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists",
            )

        new_admin = User(
            username=username,
            email=email,
            hashed_password=hash_password(data.password),
            role=UserRole.ADMIN,
            is_active=True,
        )
        new_admin.profile = UserProfile()
        await auth_repo.create(new_admin)
        await self.db.commit()
        await self.db.refresh(new_admin)
        return new_admin
