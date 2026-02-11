from __future__ import annotations

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Tag(Base):
    __tablename__ = "tags"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # 태그 이름 (중복 방지)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    post_tags = relationship("PostTag", back_populates="tag", cascade="all, delete-orphan")

