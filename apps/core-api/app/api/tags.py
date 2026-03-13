from __future__ import annotations

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.post import Post
from app.models.tag import Tag
from app.models.post_tag import PostTag
from app.schemas.tag import PostTagsAttachRequest, PostTagsResponse, TagOut

router = APIRouter(prefix="/posts", tags=["tags"])

def normalize_tag_name(name: str) -> str:
    return name.strip().lower()

@router.get(
    "/{post_id}/tags",
    response_model=PostTagsResponse,
    status_code=status.HTTP_200_OK,
)
def get_tags_of_post(
    post_id: int,
    db: Session = Depends(get_db),
) -> PostTagsResponse:
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post {post_id} not found",
        )
        
    tags = db.execute(
        select(Tag)
        .join(PostTag, PostTag.tag_id == Tag.id)
        .where(PostTag.post_id == post_id)
        .order_by(Tag.id.asc())
    ).scalars().all()
    
    return PostTagsResponse(
        post_id=post_id,
        tags=[TagOut.model_validate(tag) for tag in tags],
    )


@router.post(
    "/{post_id}/tags",
    response_model=PostTagsResponse,
    status_code=status.HTTP_200_OK,
)
def attach_tags_to_post(
    post_id: int,
    payload: PostTagsAttachRequest,
    db: Session = Depends(get_db),
) -> PostTagsResponse:
    # 1) post 존재 확인
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f"Post {post_id} not found",
        )
        
    # 2) 태그 정규화 + 빈 값 제거 + 중복 제거
    normalized_names: list[str] = []
    seen: set[str] = set()
    
    for raw_name in payload.tag_names:
        name = normalize_tag_name(raw_name)
        if not name:
            continue
        if name in seen:
            continue
        seen.add(name)
        normalized_names.append(name)
        
    if not normalized_names:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid tag names provied",
        )
        
    # 3) 기존 태그 조회
    existing_tags = db.execute(
        select(Tag).where(Tag.name.in_(normalized_names))
    ).scalars().all()
    
    existing_tag_map = {tag.name: tag for tag in existing_tags}
    
    # 4) 없는 태그 생성
    created_tags: list[Tag] = []
    for name in normalized_names:
        if name not in existing_tag_map:
            tag = Tag(name=name)
            db.add(tag)
            created_tags.append(tag)
            
    # 새로 만든 태그에 id 할당
    if created_tags:
        db.flush()
        
    # 5) 최종 태그 목록 재구성
    all_tags = db.execute(
        select(Tag).where(Tag.name.in_(normalized_names))
    ).scalars().all()
    
    all_tag_map = {tag.name: tag for tag in all_tags}
    
    # 6) 기존 post_tags 조회
    existing_post_tags = db.execute(
        select(PostTag.tag_id).where(PostTag.post_id == post_id)
    ).scalars().all()
    
    existing_tag_ids = set(existing_post_tags)
    
    # 7) 없는 연결만 추가
    for name in normalized_names:
        tag = all_tag_map[name]
        if tag.id not in existing_tag_ids:
            db.add(PostTag(post_id=post_id, tag_id=tag.id))
            
    db.commit()
    
    # 8) 응답용 태그 정렬
    result_tags = [all_tag_map[name] for name in normalized_names]
    
    return PostTagsResponse(
        post_id=post_id,
        tags=[TagOut.model_validate(tag) for tag in result_tags],
    )
