from __future__ import annotations

from sqlalchemy import ForeignKey, String, DateTime, Float, func, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Hotspot(Base):
    __tablename__ = "hotspots"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # 위도/경도: +/-180 범위, 소수 6자리면 약 0.11m 단위까지 표현 가능
    x: Mapped[float] = mapped_column(Float, nullable=False)
    y: Mapped[float] = mapped_column(Float, nullable=False)
    
    coord_space: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="normalized",
    )
    
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    post = relationship("Post", back_populates="hotspots")
    
