from datetime import datetime
from pydantic import BaseModel, Field



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