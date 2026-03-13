from __future__ import annotations

from fastapi import APIRouter, HTTPException, status, Depends, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.post import Post
from app.models.tag import Tag
from app.models.post_tag import PostTag
from app.schemas.tag import (
    PostTagsAttachRequest,
    PostTagsReplaceRequest,
    PostTagsResponse,
    TagOut,
)

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


@router.put(
    "/{post_id}/tags",
    response_model=PostTagsResponse,
    status_code=status.HTTP_200_OK,
)
def replace_post_tags(
    post_id:int,
    payload: PostTagsReplaceRequest,
    db: Session = Depends(get_db),
) -> PostTagsResponse:
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post {post_id} not found",
        )
        
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
        
    # 전체 교체 API에서는 빈 배열도 허용 가능
    # -> "이 게시물의 태그를 모두 제거"
    existing_tags = []
    if normalized_names:
        existing_tags = db.execute(
            select(Tag).where(Tag.name.in_(normalized_names))
        ).scalars().all()
        
    existing_tag_map = {tag.name: tag for tag in existing_tags}
    
    created_tags: list[Tag] = []
    for name in normalized_names:
        if name not in existing_tag_map:
            tag = Tag(name=name)
            db.add(tag)
            created_tags.append
            
    if created_tags:
        db.flush()
        
    final_tags = []
    if normalized_names:
        final_tags = db.execute(
            select(Tag).where(Tag.name.in_(normalized_names))
        ).scalars().all()
        
    final_tag_map = {tag.name: tag for tag in final_tags}
    desired_tag_ids = {tag.id for tag in final_tags}
    
    current_post_tags = db.execute(
        select(PostTag).where(PostTag.post_id == post_id)
    ).scalars().all()
    
    current_tag_ids = {pt.tag_id for pt in current_post_tags}
    
    # 제거할 연결 삭제
    for post_tag in current_post_tags:
        if post_tag.tag_id not in desired_tag_ids:
            db.delete(post_tag)
            
    # 추가할 연결 생성
    for tag in final_tags:
        if tag.id not in current_tag_ids:
            db.add(PostTag(post_id=post_id, tag_id=tag.id))
            
    db.commit()
    
    result_tags = [final_tag_map[name] for name in normalized_names]
    
    return PostTagsResponse(
        post_id=post_id,
        tags=[TagOut.model_validate(tag) for tag in result_tags],
    )


@router.delete(
    "/{post_id}/tags/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def detach_tag_from_post(
    post_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
) -> Response:
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post {post_id} not found",
        )
        
    tag = db.get(Tag, tag_id)
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag {tag_id} not found",
        )
        
    post_tag = db.execute(
        select(PostTag).where(
            PostTag.post_id == post_id, PostTag.tag_id == tag_id,
            )
    ).scalar_one_or_none()
    
    if post_tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag {tag_id} is not attached to Post {post_id}",
        )
        
    db.delete(post_tag)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)