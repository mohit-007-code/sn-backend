from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr


class UserProfileResponse(BaseModel):
    full_name: str | None = None
    bio: str | None = None
    profile_photo_url: str | None = None
    banner_photo_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class UserMeResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    profile: UserProfileResponse | None = None

    model_config = ConfigDict(from_attributes=True)

class UserProfileUpdate(BaseModel):
    full_name: str | None = None
    bio: str | None = None
    profile_photo_url: str | None = None
    banner_photo_url: str | None = None


class FollowUserItem(BaseModel):
    id: UUID
    username: str
    profile: UserProfileResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class FollowResponse(BaseModel):
    is_following: bool
    follower_count: int
    following_count: int


class FollowUserListResponse(BaseModel):
    items: list[FollowUserItem]
    page: int
    page_size: int
    total: int
    has_next: bool