from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.models.post import Post
from app.models.hotspot import Hotspot
from app.models.post_tag import PostTag
from app.models.tag import Tag
from app.models.user import User
from app.schemas.post import PostCreate, PostOut, PostDetailResponse, HotspotDetailOut
from app.schemas.tag import TagOut

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


@router.get("/{post_id}",
        response_model=PostDetailResponse,
        status_code=status.HTTP_200_OK,
)
def get_post_detail(
    post_id: int,
    db: Session = Depends(get_db),
) -> PostDetailResponse:
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post {post_id} not found",
        )
    
    hotspots = db.execute(
        select(Hotspot)
        .where(Hotspot.post_id == post_id)
        .order_by(Hotspot.id.asc())
    ).scalars().all()
    
    tags = db.execute(
        select(Tag)
        .join(PostTag, PostTag.tag_id == Tag.id)
        .where(PostTag.post_id == post_id)
        .order_by(Tag.id.asc())
    ).scalars().all()
    
    return PostDetailResponse(
        id=post.id,
        user_id=post.user_id,
        image_width=post.image_width,
        image_height=post.image_height,
        caption=post.caption,
        visibility=post.visibility,
        created_at=post.created_at,
        updated_at=post.updated_at,
        hotspots=[HotspotDetailOut.model_validate(h) for h in hotspots],
        tags=[TagOut.model_validate(tag) for tag in tags],
    )