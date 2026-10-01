from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.users.schemas import UserProfileResponse


class CommentAuthorResponse(BaseModel):
    id: UUID
    username: str
    profile: UserProfileResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class CommentCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)


class CommentResponse(BaseModel):
    id: UUID
    post_id: UUID
    user_id: UUID
    text: str
    created_at: datetime
    updated_at: datetime
    user: CommentAuthorResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class CommentListResponse(BaseModel):
    items: list[CommentResponse]
    page: int
    page_size: int
    total: int
    has_next: bool
