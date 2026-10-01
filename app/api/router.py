from fastapi import APIRouter
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as user_router
from app.modules.posts.router import router as post_router
from app.modules.feed.router import router as feed_router
from app.modules.likes.router import router as like_router
from app.modules.comments.router import router as comment_router


api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(post_router)
api_router.include_router(like_router)
api_router.include_router(comment_router)
api_router.include_router(feed_router)
