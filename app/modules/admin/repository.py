from datetime import datetime, timedelta, timezone
from typing import List, Tuple
from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.enums.user import UserRole
from app.modules.auth.models import User
from app.modules.comments.models import Comment
from app.modules.likes.models import Like
from app.modules.posts.models import Post
from app.modules.users.models import UserProfile


class AdminRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_total_users(self) -> int:
        result = await self.db.execute(select(func.count(User.id)))
        return result.scalar() or 0

    async def get_active_users_count(self) -> int:
        result = await self.db.execute(
            select(func.count(User.id)).where(User.is_active == True)
        )
        return result.scalar() or 0

    async def get_total_posts(self) -> int:
        result = await self.db.execute(select(func.count(Post.id)))
        return result.scalar() or 0

    async def get_total_comments(self) -> int:
        result = await self.db.execute(select(func.count(Comment.id)))
        return result.scalar() or 0

    async def get_total_likes(self) -> int:
        result = await self.db.execute(select(func.count(Like.id)))
        return result.scalar() or 0

    async def get_users_registered_since(self, since_date: datetime) -> int:
        result = await self.db.execute(
            select(func.count(User.id)).where(User.created_at >= since_date)
        )
        return result.scalar() or 0

    async def get_daily_registrations(self, days: int = 14) -> List[Tuple[str, int]]:
        now = datetime.now(timezone.utc)
        since_date = now - timedelta(days=days)
        
        # Group by date(created_at)
        date_col = func.to_char(User.created_at, "YYYY-MM-DD")
        stmt = (
            select(date_col.label("reg_date"), func.count(User.id))
            .where(User.created_at >= since_date)
            .group_by("reg_date")
            .order_by("reg_date")
        )
        result = await self.db.execute(stmt)
        return result.all()

    async def get_monthly_registrations(self, months: int = 6) -> List[Tuple[str, int]]:
        now = datetime.now(timezone.utc)
        since_date = now - timedelta(days=months * 31)
        
        month_col = func.to_char(User.created_at, "YYYY-MM")
        stmt = (
            select(month_col.label("reg_month"), func.count(User.id))
            .where(User.created_at >= since_date)
            .group_by("reg_month")
            .order_by("reg_month")
        )
        result = await self.db.execute(stmt)
        return result.all()

    async def get_top_posts_by_likes(self, limit: int = 5):
        likes_count_subq = (
            select(func.count(Like.id))
            .where(Like.post_id == Post.id)
            .scalar_subquery()
        )
        comments_count_subq = (
            select(func.count(Comment.id))
            .where(Comment.post_id == Post.id)
            .scalar_subquery()
        )

        stmt = (
            select(
                Post,
                User.username.label("author_username"),
                User.email.label("author_email"),
                likes_count_subq.label("likes_count"),
                comments_count_subq.label("comments_count"),
            )
            .join(User, Post.user_id == User.id)
            .order_by(desc("likes_count"))
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.all()

    async def get_top_posts_by_comments(self, limit: int = 5):
        likes_count_subq = (
            select(func.count(Like.id))
            .where(Like.post_id == Post.id)
            .scalar_subquery()
        )
        comments_count_subq = (
            select(func.count(Comment.id))
            .where(Comment.post_id == Post.id)
            .scalar_subquery()
        )

        stmt = (
            select(
                Post,
                User.username.label("author_username"),
                User.email.label("author_email"),
                likes_count_subq.label("likes_count"),
                comments_count_subq.label("comments_count"),
            )
            .join(User, Post.user_id == User.id)
            .order_by(desc("comments_count"))
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.all()

    async def get_users_list(self, page: int = 1, page_size: int = 20, search: str | None = None):
        offset = (page - 1) * page_size
        
        post_count_subq = (
            select(func.count(Post.id)).where(Post.user_id == User.id).scalar_subquery()
        )
        comment_count_subq = (
            select(func.count(Comment.id)).where(Comment.user_id == User.id).scalar_subquery()
        )
        like_count_subq = (
            select(func.count(Like.id)).where(Like.user_id == User.id).scalar_subquery()
        )

        query = (
            select(
                User,
                post_count_subq.label("posts_count"),
                comment_count_subq.label("comments_count"),
                like_count_subq.label("likes_count"),
            )
            .options(selectinload(User.profile))
            .order_by(desc(User.created_at))
        )

        count_query = select(func.count(User.id))

        if search:
            search_pattern = f"%{search.strip().lower()}%"
            filter_cond = (
                func.lower(User.username).like(search_pattern)
                | func.lower(User.email).like(search_pattern)
            )
            query = query.where(filter_cond)
            count_query = count_query.where(filter_cond)

        total_res = await self.db.execute(count_query)
        total = total_res.scalar() or 0

        res = await self.db.execute(query.offset(offset).limit(page_size))
        rows = res.all()
        return rows, total

    async def get_posts_list(self, page: int = 1, page_size: int = 20, search: str | None = None):
        offset = (page - 1) * page_size
        
        likes_count_subq = (
            select(func.count(Like.id)).where(Like.post_id == Post.id).scalar_subquery()
        )
        comments_count_subq = (
            select(func.count(Comment.id)).where(Comment.post_id == Post.id).scalar_subquery()
        )

        query = (
            select(
                Post,
                User.username.label("author_username"),
                likes_count_subq.label("likes_count"),
                comments_count_subq.label("comments_count"),
            )
            .join(User, Post.user_id == User.id)
            .order_by(desc(Post.created_at))
        )

        count_query = select(func.count(Post.id))

        if search:
            search_pattern = f"%{search.strip().lower()}%"
            filter_cond = func.lower(Post.title).like(search_pattern)
            query = query.where(filter_cond)
            count_query = count_query.where(filter_cond)

        total_res = await self.db.execute(count_query)
        total = total_res.scalar() or 0

        res = await self.db.execute(query.offset(offset).limit(page_size))
        rows = res.all()
        return rows, total

    async def get_comments_list(self, page: int = 1, page_size: int = 20, search: str | None = None):
        offset = (page - 1) * page_size

        query = (
            select(
                Comment,
                User.username.label("author_username"),
                Post.title.label("post_title"),
            )
            .join(User, Comment.user_id == User.id)
            .join(Post, Comment.post_id == Post.id)
            .order_by(desc(Comment.created_at))
        )

        count_query = select(func.count(Comment.id))

        if search:
            search_pattern = f"%{search.strip().lower()}%"
            filter_cond = func.lower(Comment.text).like(search_pattern)
            query = query.where(filter_cond)
            count_query = count_query.where(filter_cond)

        total_res = await self.db.execute(count_query)
        total = total_res.scalar() or 0

        res = await self.db.execute(query.offset(offset).limit(page_size))
        rows = res.all()
        return rows, total

    async def delete_user(self, user: User) -> None:
        await self.db.delete(user)
        await self.db.commit()

    async def delete_post(self, post: Post) -> None:
        await self.db.delete(post)
        await self.db.commit()

    async def delete_comment(self, comment: Comment) -> None:
        await self.db.delete(comment)
        await self.db.commit()
