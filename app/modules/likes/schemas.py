from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.modules.users.schemas import UserProfileResponse


class LikeUserItem(BaseModel):
    id: UUID
    username: str
    profile: UserProfileResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class PostLikesListResponse(BaseModel):
    items: list[LikeUserItem]
    page: int
    page_size: int
    total: int
    has_next: bool


class LikeToggleResponse(BaseModel):
    is_liked: bool
    like_count: int
