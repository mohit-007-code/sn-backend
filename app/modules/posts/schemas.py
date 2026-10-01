from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PostCreate(BaseModel):
    title: str
    caption: str | None = None
    image_url: str | None = None


class PostUpdate(BaseModel):
    title: str | None = None
    caption: str | None = None
    image_url: str | None = None


class PostResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    caption: str | None = None
    image_url: str | None = None
    share_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    is_liked: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PostListResponse(BaseModel):
    items: list[PostResponse]
    page: int
    page_size: int
    total: int
    pages: int


class ShareResponse(BaseModel):
    message: str = "Post shared successfully"
    share_count: int