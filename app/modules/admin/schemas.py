from datetime import date, datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class AdminStatsSummary(BaseModel):
    total_users: int
    active_users: int
    inactive_users: int
    total_posts: int
    total_comments: int
    total_likes: int
    new_users_today: int
    new_users_this_month: int


class DailyRegistrationItem(BaseModel):
    date: str
    count: int


class MonthlyRegistrationItem(BaseModel):
    month: str
    count: int


class TopPostItem(BaseModel):
    id: UUID
    title: str
    caption: Optional[str] = None
    image_url: Optional[str] = None
    author_username: str
    author_email: str
    created_at: datetime
    likes_count: int
    comments_count: int
    share_count: int


class AdminDashboardAnalytics(BaseModel):
    summary: AdminStatsSummary
    daily_registrations: List[DailyRegistrationItem]
    monthly_registrations: List[MonthlyRegistrationItem]
    top_posts_by_likes: List[TopPostItem]
    top_posts_by_comments: List[TopPostItem]


class AdminUserItem(BaseModel):
    id: UUID
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    posts_count: int
    comments_count: int
    likes_count: int
    profile_photo_url: Optional[str] = None
    full_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AdminUserListResponse(BaseModel):
    items: List[AdminUserItem]
    total: int
    page: int
    page_size: int
    has_next: bool


class AdminPostItem(BaseModel):
    id: UUID
    title: str
    caption: Optional[str] = None
    image_url: Optional[str] = None
    created_at: datetime
    author_id: UUID
    author_username: str
    likes_count: int
    comments_count: int
    share_count: int


class AdminPostListResponse(BaseModel):
    items: List[AdminPostItem]
    total: int
    page: int
    page_size: int
    has_next: bool


class AdminCommentItem(BaseModel):
    id: UUID
    text: str
    created_at: datetime
    post_id: UUID
    post_title: str
    author_id: UUID
    author_username: str


class AdminCommentListResponse(BaseModel):
    items: List[AdminCommentItem]
    total: int
    page: int
    page_size: int
    has_next: bool


class CreateAdminRequest(BaseModel):
    username: str
    email: str
    password: str
