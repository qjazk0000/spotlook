from datetime import datetime
from pydantic import BaseModel, Field

from app.schemas.tag import TagOut



class PostCreate(BaseModel):
    user_id: int
    caption: str | None = None
    visibility: str = Field(default="public", max_length=20)
    image_width: int | None = None
    image_height: int | None = None
    

class PostOut(BaseModel):
    id: int
    user_id: int
    caption: str | None
    visibility: str
    image_width: int | None
    image_height: int | None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # SQLAlchemy ORM -> Pydantic model
        
        
class HotspotDetailOut(BaseModel):
    id: int
    x: float
    y: float
    created_at: datetime
    
    model_config = {"from_attributes": True}
        
        
class PostDetailResponse(BaseModel):
    id: int
    user_id: int
    image_width: int | None
    image_height: int | None
    caption: str | None
    visibility: str
    created_at: datetime
    updated_at: datetime
    hotspots: list[HotspotDetailOut]
    tags: list[TagOut]
    
    model_config = {"from_attributes": True}