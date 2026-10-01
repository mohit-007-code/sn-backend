from math import ceil
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.storage import save_image

from app.modules.posts.models import Post
from app.modules.posts.repository import PostRepository


class PostService:
    def __init__(self, db: AsyncSession):
        self.repository = PostRepository(db)
        self.db = db

    async def create_post(
        self,
        user_id: UUID,
        title: str,
        caption: str | None,
        image: UploadFile | None,
    ) -> dict:

        image_url = None
        if image is not None:
            image_url = await save_image(image, "posts")

        post = Post(
            user_id=user_id,
            title=title,
            caption=caption,
            image_url=image_url,
        )

        created_post = await self.repository.create(post)
        await self.db.commit()
        await self.db.refresh(created_post)

        return await self.repository.enrich_single_post_stats(created_post, user_id)

    async def get_post(self, post_id: UUID, current_user_id: UUID | None = None) -> dict:
        post = await self.repository.get_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found",
            )

        return await self.repository.enrich_single_post_stats(post, current_user_id)

    async def get_user_posts(
        self, user_id: UUID, page: int, page_size: int, current_user_id: UUID | None = None
    ) -> dict:
        posts, total = await self.repository.get_by_user_id(
            user_id=user_id,
            page=page,
            page_size=page_size,
        )

        enriched_items = await self.repository.enrich_posts_stats(posts, current_user_id)
        pages = ceil(total / page_size) if total else 0
        return {
            "items": enriched_items,
            "page": page,
            "page_size": page_size,
            "total": total,
            "pages": pages,
        }

    async def update_post(
        self,
        post_id: UUID,
        user_id: UUID,
        title: str | None,
        caption: str | None,
        image: UploadFile | None,
        remove_image: bool,
    ) -> dict:

        post = await self.repository.get_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found",
            )

        if post.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own post",
            )

        if remove_image and image is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot upload and remove image at the same time",
            )

        if title is not None:
            post.title = title

        if caption is not None:
            post.caption = caption

        if remove_image:
            post.image_url = None

        elif image is not None:
            post.image_url = await save_image(
                image,
                "posts",
            )
        await self.db.commit()
        await self.db.refresh(post)
        return await self.repository.enrich_single_post_stats(post, user_id)

    async def share_post(self, post_id: UUID) -> dict:
        post = await self.repository.get_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found",
            )
        post.share_count += 1
        await self.db.commit()
        return {
            "message": "Post shared successfully",
            "share_count": post.share_count,
        }

    async def delete_post(self, post_id: UUID, user_id: UUID) -> None:
        post = await self.repository.get_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found",
            )

        if post.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own post",
            )
        await self.repository.delete(post)
        await self.db.commit()