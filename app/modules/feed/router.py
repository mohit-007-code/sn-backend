from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user_optional
from app.db.session import get_db
from app.modules.auth.models import User
from app.modules.feed.schemas import FeedResponse
from app.modules.feed.service import FeedService

router = APIRouter(
    prefix="/feed",
    tags=["Feed"],
)


@router.get("", response_model=FeedResponse)
async def get_feed(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    service = FeedService(db)
    return await service.get_feed(
        page=page,
        page_size=page_size,
        current_user_id=current_user.id if current_user else None,
    )

