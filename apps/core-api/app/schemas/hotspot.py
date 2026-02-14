from datetime import datetime
from pydantic import BaseModel, Field


class HotspotCreatePx(BaseModel):
    x_px: float = Field(..., ge=0)
    y_px: float = Field(..., ge=0)
    
    
class HotspotOut(BaseModel):
    id: int
    post_id: int
    x: float  # normalized (0~1)
    y: float  # normalized (0~1)
    created_at: datetime
    
    class Config:
        from_attributes = True
    