from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.auth.models import User
from app.modules.comments.models import Comment


class CommentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, comment: Comment) -> Comment:
        self.db.add(comment)
        await self.db.flush()
        return comment

    async def count_post_comments(self, post_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(Comment).where(Comment.post_id == post_id)
        )
        return result.scalar_one()

    async def get_post_comments(
        self, post_id: UUID, page: int, page_size: int
    ) -> tuple[list[Comment], int]:
        offset = (page - 1) * page_size
        total = await self.count_post_comments(post_id)
        result = await self.db.execute(
            select(Comment)
            .options(
                selectinload(Comment.user).selectinload(User.profile)
            )
            .where(Comment.post_id == post_id)
            .order_by(Comment.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        comments = list(result.scalars().all())
        return comments, total
