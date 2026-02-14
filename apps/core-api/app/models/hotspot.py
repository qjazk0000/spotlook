from __future__ import annotations

from sqlalchemy import ForeignKey, String, DateTime, Float, func, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Hotspot(Base):
    __tablename__ = "hotspots"
    __table_args__ = (
        CheckConstraint("x >= 0 AND x <= 1", name="ck_hotspots_x_0_1"),
        CheckConstraint("y >= 0, AND y <= 1", name="ck_hotspots_y_0_1"),
    )
    
    x: Mapped[float] = mapped_column(Float, nullable=False)
    y: Mapped[float] = mapped_column(Float, nullable=False)
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    post = relationship("Post", back_populates="hotspots")
    
