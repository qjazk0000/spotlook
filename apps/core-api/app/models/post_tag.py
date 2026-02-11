from __future__ import annotations

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PostTag(Base):
    __tablename__ = "post_tags"
    
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
        primary_key=True,
    )
    
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
    )
    
    post = relationship("Post", back_populates="post_tags")
    tag = relationship("Tag",back_populates="post_tags")
    saves = relationship("Save", back_populates="post", cascade="all, delete-orphan")