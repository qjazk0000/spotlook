from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.session import get_db
from app.models.post import Post
from app.models.hotspot import Hotspot
from app.schemas.hotspot import HotspotCreatePx, HotspotOut

router = APIRouter(prefix="/posts/{post_id}/hotspots", tags=["hotspots"])



@router.post("", response_model=HotspotOut)
def create_hotspot(post_id: int, payload: HotspotCreatePx, db: Session = Depends(get_db)):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail=f"Post {post_id} not found")
    
    if post.image_width is None or post.image_height is None:
        raise HTTPException(status_code=400, detail="Post image_width/image_height is required to normalize coords")
    
    if post.image_width <= 0 or post.image_height <= 0:
        raise HTTPException(status_code=400, detail="Post image_width/image_height must be > 0")
    
    
    # px -> normalized
    x = payload.x_px / post.image_width
    y = payload.y_px / post.image_height
    
    # 범위 검증
    if not (0.0 <= x <= 1.0) or not (0.0 <= y <= 1.0):
        raise HTTPException(status_code=400, detail="x/y must be within [0.0, 1.0] after normalization")
    
    hs = Hotspot(post_id=post_id, x=x, y=y)
    db.add(hs)
    
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"DB integrity error: {str(e.orig)}") from e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpeted error: {type(e).__name__}") from e
    
    db.refresh(hs)
    
    return hs