from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.likes.repository import LikeRepository
from app.modules.posts.models import Post


class LikeService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = LikeRepository(db)

    async def like_post(self, user_id: UUID, post_id: UUID) -> dict:
        post = await self.db.get(Post, post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found",
            )

        existing = await self.repository.get_like(user_id, post_id)
        if not existing:
            await self.repository.create_like(user_id, post_id)
            await self.db.commit()

        like_count = await self.repository.count_post_likes(post_id)
        return {
            "is_liked": True,
            "like_count": like_count,
        }

    async def unlike_post(self, user_id: UUID, post_id: UUID) -> dict:
        post = await self.db.get(Post, post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found",
            )

        existing = await self.repository.get_like(user_id, post_id)
        if existing:
            await self.repository.delete_like(existing)
            await self.db.commit()

        like_count = await self.repository.count_post_likes(post_id)
        return {
            "is_liked": False,
            "like_count": like_count,
        }

    async def get_post_likes(self, post_id: UUID, page: int, page_size: int) -> dict:
        post = await self.db.get(Post, post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found",
            )

        users, total = await self.repository.get_post_likes(post_id, page, page_size)
        has_next = (page * page_size) < total
        return {
            "items": users,
            "page": page,
            "page_size": page_size,
            "total": total,
            "has_next": has_next,
        }
