"""用户模型."""
from datetime import datetime

from sqlalchemy import Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, beijing_now


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="user")  # user / admin
    email: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    avatar: Mapped[str | None] = mapped_column(Text, nullable=True)  # base64
    nickname: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    balance: Mapped[float] = mapped_column(default=0.0, nullable=False)  # 余额
    vip_level: Mapped[str] = mapped_column(String(10), default="free", nullable=False)  # free/vip/svip
    vip_expire_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    daily_free_used: Mapped[int] = mapped_column(default=0, nullable=False)
    daily_exp_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    token_version: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=beijing_now, nullable=False
    )
