import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Enum as SQLAlchemyEnum, String, Uuid ,func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.enums.user import UserRole

from app.modules.users.models import Follow, UserProfile


class User(Base):
    __tablename__ = "users"

    __table_args__ = (
        CheckConstraint(
            "length(email) > 0",
            name="ck_users_email_not_empty",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(100), nullable=False, index=True, unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SQLAlchemyEnum(UserRole, name="user_role", native_enum=False, length=20), default=UserRole.USER, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False )

    profile: Mapped["UserProfile"] = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    followers: Mapped[list["Follow"]] = relationship("Follow", foreign_keys="Follow.following_id", back_populates="following", cascade="all, delete-orphan")
    following: Mapped[list["Follow"]] = relationship("Follow", foreign_keys="Follow.follower_id", back_populates="follower", cascade="all, delete-orphan")