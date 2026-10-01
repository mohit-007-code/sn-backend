from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.auth.models import User
from app.modules.comments.models import Comment
from app.modules.comments.repository import CommentRepository
from app.modules.posts.models import Post


class CommentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = CommentRepository(db)

    async def create_comment(
        self, user_id: UUID, post_id: UUID, text: str
    ) -> Comment:
        post = await self.db.get(Post, post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found",
            )

        comment = Comment(
            post_id=post_id,
            user_id=user_id,
            text=text.strip(),
        )
        created = await self.repository.create(comment)
        await self.db.commit()

        res = await self.db.execute(
            select(Comment)
            .options(selectinload(Comment.user).selectinload(User.profile))
            .where(Comment.id == created.id)
        )
        return res.scalar_one()

    async def get_post_comments(
        self, post_id: UUID, page: int, page_size: int
    ) -> dict:
        post = await self.db.get(Post, post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found",
            )

        comments, total = await self.repository.get_post_comments(
            post_id, page, page_size
        )
        has_next = (page * page_size) < total
        return {
            "items": comments,
            "page": page,
            "page_size": page_size,
            "total": total,
            "has_next": has_next,
        }
