from pydantic import BaseModel
from app.modules.posts.schemas import PostResponse


class FeedResponse(BaseModel):
    items: list[PostResponse]
    page: int
    page_size: int
    total: int
    has_next: bool
