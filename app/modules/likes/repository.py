from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.auth.models import User
from app.modules.likes.models import Like


class LikeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_like(self, user_id: UUID, post_id: UUID) -> Like | None:
        result = await self.db.execute(
            select(Like).where(Like.user_id == user_id, Like.post_id == post_id)
        )
        return result.scalar_one_or_none()

    async def create_like(self, user_id: UUID, post_id: UUID) -> Like:
        like = Like(user_id=user_id, post_id=post_id)
        self.db.add(like)
        await self.db.flush()
        return like

    async def delete_like(self, like: Like) -> None:
        await self.db.delete(like)

    async def count_post_likes(self, post_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(Like).where(Like.post_id == post_id)
        )
        return result.scalar_one()

    async def get_post_likes(
        self, post_id: UUID, page: int, page_size: int
    ) -> tuple[list[User], int]:
        offset = (page - 1) * page_size
        total = await self.count_post_likes(post_id)
        result = await self.db.execute(
            select(User)
            .join(Like, Like.user_id == User.id)
            .options(selectinload(User.profile))
            .where(Like.post_id == post_id)
            .order_by(Like.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        users = list(result.scalars().all())
        return users, total
