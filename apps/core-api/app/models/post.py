from __future__ import annotations

from sqlalchemy import ForeignKey, String, DateTime, func, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class Post(Base):
    __tablename__ = "posts"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        )
    
    image_width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    image_height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    caption: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    
    visibility: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="public",
    )
    
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    
    user = relationship("User", back_populates="posts")
    hotspots = relationship("Hotspot", back_populates="post", cascade="all, delete-orphan")
    