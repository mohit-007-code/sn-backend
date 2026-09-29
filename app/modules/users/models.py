import uuid
from datetime import datetime

from sqlalchemy import  DateTime,ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import CheckConstraint, UniqueConstraint

from app.db.base import Base

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"),unique=True, nullable=False, index=True)
    full_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    profile_photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    banner_photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    user = relationship("User", back_populates="profile")

class Follow(Base):
    __tablename__ = "follows"

    __table_args__ = (
        UniqueConstraint(
            "follower_id",
            "following_id",
            name="uq_follows_follower_following",
        ),
        CheckConstraint(
            "follower_id <> following_id",
            name="ck_follows_no_self_follow",
        ),
    )
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    follower_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    following_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    follower = relationship("User", foreign_keys=[follower_id], back_populates="following")

    following = relationship("User", foreign_keys=[following_id], back_populates="followers")