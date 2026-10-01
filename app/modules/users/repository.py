from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.auth.models import User
from app.modules.users.models import Follow


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.profile))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_follow(self, follower_id: UUID, following_id: UUID) -> Follow | None:
        result = await self.db.execute(
            select(Follow).where(
                Follow.follower_id == follower_id,
                Follow.following_id == following_id,
            )
        )
        return result.scalar_one_or_none()

    async def create_follow(self, follower_id: UUID, following_id: UUID) -> Follow:
        follow = Follow(follower_id=follower_id, following_id=following_id)
        self.db.add(follow)
        await self.db.flush()
        return follow

    async def delete_follow(self, follow: Follow) -> None:
        await self.db.delete(follow)

    async def count_followers(self, user_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(Follow).where(Follow.following_id == user_id)
        )
        return result.scalar_one()

    async def count_following(self, user_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(Follow).where(Follow.follower_id == user_id)
        )
        return result.scalar_one()

    async def get_followers(
        self, user_id: UUID, page: int, page_size: int
    ) -> tuple[list[User], int]:
        offset = (page - 1) * page_size
        total = await self.count_followers(user_id)
        result = await self.db.execute(
            select(User)
            .join(Follow, Follow.follower_id == User.id)
            .options(selectinload(User.profile))
            .where(Follow.following_id == user_id)
            .order_by(Follow.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        users = list(result.scalars().all())
        return users, total

    async def get_following(
        self, user_id: UUID, page: int, page_size: int
    ) -> tuple[list[User], int]:
        offset = (page - 1) * page_size
        total = await self.count_following(user_id)
        result = await self.db.execute(
            select(User)
            .join(Follow, Follow.following_id == User.id)
            .options(selectinload(User.profile))
            .where(Follow.follower_id == user_id)
            .order_by(Follow.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        users = list(result.scalars().all())
        return users, total
