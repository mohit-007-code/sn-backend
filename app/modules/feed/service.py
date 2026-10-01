from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.feed.repository import FeedRepository


class FeedService:
    def __init__(self, db: AsyncSession):
        self.repository = FeedRepository(db)
        self.db = db

    async def get_feed(
        self, page: int, page_size: int, current_user_id: UUID | None = None
    ) -> dict:
        posts, total = await self.repository.get_feed_posts(
            page=page,
            page_size=page_size,
        )

        enriched_items = await self.repository.enrich_posts_stats(posts, current_user_id)
        has_next = (page * page_size) < total
        return {
            "items": enriched_items,
            "page": page,
            "page_size": page_size,
            "total": total,
            "has_next": has_next,
        }

