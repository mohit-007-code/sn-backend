from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.comments.models import Comment
from app.modules.likes.models import Like
from app.modules.posts.models import Post


class FeedRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_feed_posts(
        self,
        page: int,
        page_size: int,
    ) -> tuple[list[Post], int]:
        offset = (page - 1) * page_size

        result = await self.db.execute(
            select(Post)
            .order_by(Post.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )

        posts = list(result.scalars().all())

        total_result = await self.db.execute(
            select(func.count()).select_from(Post)
        )

        total = total_result.scalar_one()

        return posts, total

    async def enrich_posts_stats(
        self, posts: list[Post], current_user_id: UUID | None = None
    ) -> list[dict]:
        if not posts:
            return []

        post_ids = [p.id for p in posts]

        like_res = await self.db.execute(
            select(Like.post_id, func.count(Like.id))
            .where(Like.post_id.in_(post_ids))
            .group_by(Like.post_id)
        )
        like_counts = dict(like_res.all())

        comment_res = await self.db.execute(
            select(Comment.post_id, func.count(Comment.id))
            .where(Comment.post_id.in_(post_ids))
            .group_by(Comment.post_id)
        )
        comment_counts = dict(comment_res.all())

        liked_post_ids = set()
        if current_user_id:
            user_likes_res = await self.db.execute(
                select(Like.post_id)
                .where(Like.user_id == current_user_id, Like.post_id.in_(post_ids))
            )
            liked_post_ids = set(user_likes_res.scalars().all())

        return [
            {
                "id": p.id,
                "user_id": p.user_id,
                "title": p.title,
                "caption": p.caption,
                "image_url": p.image_url,
                "share_count": p.share_count,
                "like_count": like_counts.get(p.id, 0),
                "comment_count": comment_counts.get(p.id, 0),
                "is_liked": p.id in liked_post_ids,
                "created_at": p.created_at,
                "updated_at": p.updated_at,
            }
            for p in posts
        ]

