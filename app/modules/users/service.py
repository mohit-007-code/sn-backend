from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.repository import UserRepository


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = UserRepository(db)

    async def follow_user(self, current_user_id: UUID, target_user_id: UUID) -> dict:
        if current_user_id == target_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot follow yourself",
            )

        target_user = await self.repository.get_by_id(target_user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        existing = await self.repository.get_follow(current_user_id, target_user_id)
        if not existing:
            await self.repository.create_follow(current_user_id, target_user_id)
            await self.db.commit()

        follower_count = await self.repository.count_followers(target_user_id)
        following_count = await self.repository.count_following(target_user_id)

        return {
            "is_following": True,
            "follower_count": follower_count,
            "following_count": following_count,
        }

    async def unfollow_user(self, current_user_id: UUID, target_user_id: UUID) -> dict:
        target_user = await self.repository.get_by_id(target_user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        existing = await self.repository.get_follow(current_user_id, target_user_id)
        if existing:
            await self.repository.delete_follow(existing)
            await self.db.commit()

        follower_count = await self.repository.count_followers(target_user_id)
        following_count = await self.repository.count_following(target_user_id)

        return {
            "is_following": False,
            "follower_count": follower_count,
            "following_count": following_count,
        }

    async def get_followers(self, target_user_id: UUID, page: int, page_size: int) -> dict:
        target_user = await self.repository.get_by_id(target_user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        users, total = await self.repository.get_followers(target_user_id, page, page_size)
        has_next = (page * page_size) < total
        return {
            "items": users,
            "page": page,
            "page_size": page_size,
            "total": total,
            "has_next": has_next,
        }

    async def get_following(self, target_user_id: UUID, page: int, page_size: int) -> dict:
        target_user = await self.repository.get_by_id(target_user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        users, total = await self.repository.get_following(target_user_id, page, page_size)
        has_next = (page * page_size) < total
        return {
            "items": users,
            "page": page,
            "page_size": page_size,
            "total": total,
            "has_next": has_next,
        }
