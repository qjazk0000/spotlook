from pydantic import BaseModel, Field


class PostTagsAttachRequest(BaseModel):
    tag_names: list[str] = Field(..., min_length=1)
    
    
class TagOut(BaseModel):
    id: int
    name: str
    
    model_config = {"from_attributes": True}
    
    
class PostTagsResponse(BaseModel):
    post_id: int
    tags: list[TagOut]
    