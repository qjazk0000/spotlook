from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.post import Post
from app.models.user import User
from app.schemas.post import PostCreate, PostOut

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("", response_model=PostOut)
def create_post(payload: PostCreate, db: Session = Depends(get_db)):
    # 1) user 검증
    user = db.get(User, payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {payload.user_id} not found")
    
    post = Post(
        user_id=payload.user_id,
        caption=payload.caption,
        visibility=payload.visibility,
        image_width=payload.image_width,
        image_height=payload.image_height,
    )
    
    db.add(post)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"DB integrity error: {str(e.orig)}") from e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {type(e).__name__}") from e
    
    db.refresh(post)
    return post