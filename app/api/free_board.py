from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc, func
from typing import List, Optional
import logging

from app.db.database import SessionLocal
from app.db.models.user import User
from app.db.models.free_post import FreePost
from app.db.models.free_comment import FreeComment
from app.db.models.free_attachment import FreeAttachment
from app.db.models.post_like import PostLike
from app.db.models.post_view import PostView
from app.schemas.board import (
    PostListRequest, PostCreateRequest, PostUpdateRequest,
    PostListResponse, PostDetailResponse, PaginatedResponse,
    CommentCreateRequest, CommentUpdateRequest, CommentResponse,
    LikeResponse, SortOrder
)
from app.api.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/free-board", tags=["자유게시판"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 게시글 목록 조회
@router.get("/posts", response_model=PaginatedResponse)
def get_free_posts(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=100, description="페이지 크기"),
    search: Optional[str] = Query(None, description="검색어"),
    sort: SortOrder = Query(SortOrder.LATEST, description="정렬 기준"),
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """자유게시판 게시글 목록 조회"""
    
    # 기본 쿼리
    query = db.query(FreePost).options(
        joinedload(FreePost.user)
    )
    
    # 검색 조건
    if search:
        search_filter = or_(
            FreePost.title.contains(search),
            FreePost.content.contains(search)
        )
        query = query.filter(search_filter)
    
    # 정렬
    if sort == SortOrder.LATEST:
        query = query.order_by(desc(FreePost.crt_date))
    elif sort == SortOrder.OLDEST:
        query = query.order_by(asc(FreePost.crt_date))
    elif sort == SortOrder.VIEWS:
        query = query.order_by(desc(FreePost.view_count))
    elif sort == SortOrder.LIKES:
        query = query.order_by(desc(FreePost.like_count))
    elif sort == SortOrder.COMMENTS:
        query = query.order_by(desc(FreePost.comment_count))
    
    # 공지사항 먼저 표시
    query = query.order_by(desc(FreePost.is_notice))
    
    # 전체 개수
    total = query.count()
    
    # 페이징
    posts = query.offset((page - 1) * size).limit(size).all()
    
    # 사용자별 좋아요 상태 확인
    post_list = []
    for post in posts:
        post_dict = {
            "id": post.id,
            "title": post.title,
            "content_preview": post.content[:100] + "..." if len(post.content) > 100 else post.content,
            "user_id": post.user.id,
            "user_nickname": post.user.nickname,
            "user_profile_img": post.user.profile_img,
            "view_count": post.view_count,
            "like_count": post.like_count,
            "comment_count": post.comment_count,
            "is_notice": post.is_notice,
            "is_liked": False,
            "crt_date": post.crt_date,
            "mod_date": post.mod_date
        }
        
        # 현재 사용자의 좋아요 상태 확인
        if current_user:
            like = db.query(PostLike).filter(
                and_(
                    PostLike.post_type == 'free',
                    PostLike.post_id == post.id,
                    PostLike.user_id == current_user.id,
                    PostLike.is_active == True
                )
            ).first()
            post_dict["is_liked"] = like is not None
        
        post_list.append(PostListResponse(**post_dict))
    
    total_pages = (total + size - 1) // size
    
    return PaginatedResponse(
        items=post_list,
        total=total,
        page=page,
        size=size,
        total_pages=total_pages
    )

# 게시글 상세 조회
@router.get("/posts/{post_id}", response_model=PostDetailResponse)
def get_free_post(
    post_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """자유게시판 게시글 상세 조회"""
    
    post = db.query(FreePost).options(
        joinedload(FreePost.user),
        joinedload(FreePost.attachments),
        joinedload(FreePost.comments).joinedload(FreeComment.user)
    ).filter(FreePost.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    
    # 조회수 증가 (로그인한 사용자만)
    if current_user:
        # 중복 조회 방지
        existing_view = db.query(PostView).filter(
            and_(
                PostView.post_type == 'free',
                PostView.post_id == post_id,
                PostView.user_id == current_user.id
            )
        ).first()
        
        if not existing_view:
            view = PostView(
                post_type='free',
                post_id=post_id,
                user_id=current_user.id
            )
            db.add(view)
            db.commit()
    
    # 사용자 좋아요 상태 확인
    is_liked = False
    if current_user:
        like = db.query(PostLike).filter(
            and_(
                PostLike.post_type == 'free',
                PostLike.post_id == post_id,
                PostLike.user_id == current_user.id,
                PostLike.is_active == True
            )
        ).first()
        is_liked = like is not None
    
    # 댓글 트리 구조 생성
    comments = []
    comment_dict = {}
    
    for comment in post.comments:
        comment_data = {
            "id": comment.id,
            "content": comment.content,
            "depth": comment.depth,
            "parent_id": comment.parent_id,
            "user_id": comment.user.id,
            "user_nickname": comment.user.nickname,
            "user_profile_img": comment.user.profile_img,
            "like_count": comment.like_count,
            "is_liked": False,
            "crt_date": comment.crt_date,
            "mod_date": comment.mod_date,
            "children": []
        }
        
        # 댓글 좋아요 상태 확인
        if current_user:
            comment_like = db.query(PostLike).filter(
                and_(
                    PostLike.post_type == 'free_comment',
                    PostLike.post_id == comment.id,
                    PostLike.user_id == current_user.id,
                    PostLike.is_active == True
                )
            ).first()
            comment_data["is_liked"] = comment_like is not None
        
        comment_dict[comment.id] = CommentResponse(**comment_data)
    
    # 트리 구조 생성
    for comment_id, comment in comment_dict.items():
        if comment.parent_id is None:
            comments.append(comment)
        else:
            if comment.parent_id in comment_dict:
                comment_dict[comment.parent_id].children.append(comment)
    
    # 첨부파일 정보
    attachments = []
    for attachment in post.attachments:
        attachments.append({
            "id": attachment.id,
            "filename": attachment.filename,
            "original_filename": attachment.original_filename,
            "file_size": attachment.file_size,
            "file_path": attachment.file_path,
            "crt_date": attachment.crt_date
        })
    
    return PostDetailResponse(
        id=post.id,
        title=post.title,
        content=post.content,
        user_id=post.user.id,
        user_nickname=post.user.nickname,
        user_profile_img=post.user.profile_img,
        view_count=post.view_count,
        like_count=post.like_count,
        comment_count=post.comment_count,
        is_notice=post.is_notice,
        is_liked=is_liked,
        crt_date=post.crt_date,
        mod_date=post.mod_date,
        attachments=attachments,
        comments=comments
    )

# 게시글 작성
@router.post("/posts", response_model=PostDetailResponse, status_code=status.HTTP_201_CREATED)
def create_free_post(
    post_data: PostCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """자유게시판 게시글 작성"""
    
    post = FreePost(
        title=post_data.title,
        content=post_data.content,
        is_notice=post_data.is_notice,
        user_id=current_user.id
    )
    
    db.add(post)
    db.commit()
    db.refresh(post)
    
    # 작성자 정보 로드
    db.refresh(post.user)
    
    return PostDetailResponse(
        id=post.id,
        title=post.title,
        content=post.content,
        user_id=post.user.id,
        user_nickname=post.user.nickname,
        user_profile_img=post.user.profile_img,
        view_count=post.view_count,
        like_count=post.like_count,
        comment_count=post.comment_count,
        is_notice=post.is_notice,
        is_liked=False,
        crt_date=post.crt_date,
        mod_date=post.mod_date,
        attachments=[],
        comments=[]
    )

# 게시글 수정
@router.put("/posts/{post_id}", response_model=PostDetailResponse)
def update_free_post(
    post_id: int,
    post_data: PostUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """자유게시판 게시글 수정"""
    
    post = db.query(FreePost).filter(FreePost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    
    # 작성자만 수정 가능
    if post.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="게시글을 수정할 권한이 없습니다.")
    
    # 수정할 필드만 업데이트
    if post_data.title is not None:
        post.title = post_data.title
    if post_data.content is not None:
        post.content = post_data.content
    if post_data.is_notice is not None:
        post.is_notice = post_data.is_notice
    
    db.commit()
    db.refresh(post)
    db.refresh(post.user)
    
    return PostDetailResponse(
        id=post.id,
        title=post.title,
        content=post.content,
        user_id=post.user.id,
        user_nickname=post.user.nickname,
        user_profile_img=post.user.profile_img,
        view_count=post.view_count,
        like_count=post.like_count,
        comment_count=post.comment_count,
        is_notice=post.is_notice,
        is_liked=False,
        crt_date=post.crt_date,
        mod_date=post.mod_date,
        attachments=[],
        comments=[]
    )

# 게시글 삭제
@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_free_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """자유게시판 게시글 삭제"""
    
    post = db.query(FreePost).filter(FreePost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    
    # 작성자만 삭제 가능
    if post.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="게시글을 삭제할 권한이 없습니다.")
    
    db.delete(post)
    db.commit()

# 댓글 작성
@router.post("/posts/{post_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_free_comment(
    post_id: int,
    comment_data: CommentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """자유게시판 댓글 작성"""
    
    # 게시글 존재 확인
    post = db.query(FreePost).filter(FreePost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    
    # 부모 댓글 확인 (대댓글인 경우)
    if comment_data.parent_id:
        parent_comment = db.query(FreeComment).filter(
            and_(
                FreeComment.id == comment_data.parent_id,
                FreeComment.post_id == post_id
            )
        ).first()
        if not parent_comment:
            raise HTTPException(status_code=404, detail="부모 댓글을 찾을 수 없습니다.")
    
    comment = FreeComment(
        content=comment_data.content,
        parent_id=comment_data.parent_id,
        post_id=post_id,
        user_id=current_user.id
    )
    
    db.add(comment)
    db.commit()
    db.refresh(comment)
    db.refresh(comment.user)
    
    return CommentResponse(
        id=comment.id,
        content=comment.content,
        depth=comment.depth,
        parent_id=comment.parent_id,
        user_id=comment.user.id,
        user_nickname=comment.user.nickname,
        user_profile_img=comment.user.profile_img,
        like_count=comment.like_count,
        is_liked=False,
        crt_date=comment.crt_date,
        mod_date=comment.mod_date,
        children=[]
    )

# 댓글 수정
@router.put("/comments/{comment_id}", response_model=CommentResponse)
def update_free_comment(
    comment_id: int,
    comment_data: CommentUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """자유게시판 댓글 수정"""
    
    comment = db.query(FreeComment).filter(FreeComment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")
    
    # 작성자만 수정 가능
    if comment.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="댓글을 수정할 권한이 없습니다.")
    
    comment.content = comment_data.content
    db.commit()
    db.refresh(comment)
    db.refresh(comment.user)
    
    return CommentResponse(
        id=comment.id,
        content=comment.content,
        depth=comment.depth,
        parent_id=comment.parent_id,
        user_id=comment.user.id,
        user_nickname=comment.user.nickname,
        user_profile_img=comment.user.profile_img,
        like_count=comment.like_count,
        is_liked=False,
        crt_date=comment.crt_date,
        mod_date=comment.mod_date,
        children=[]
    )

# 댓글 삭제
@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_free_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """자유게시판 댓글 삭제"""
    
    comment = db.query(FreeComment).filter(FreeComment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")
    
    # 작성자만 삭제 가능
    if comment.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="댓글을 삭제할 권한이 없습니다.")
    
    db.delete(comment)
    db.commit()

# 게시글 좋아요/취소
@router.post("/posts/{post_id}/like", response_model=LikeResponse)
def toggle_free_post_like(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """자유게시판 게시글 좋아요/취소"""
    
    # 게시글 존재 확인
    post = db.query(FreePost).filter(FreePost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    
    # 기존 좋아요 확인 (is_active 상태와 관계없이)
    existing_like = db.query(PostLike).filter(
        and_(
            PostLike.post_type == 'free',
            PostLike.post_id == post_id,
            PostLike.user_id == current_user.id
        )
    ).first()
    
    if existing_like:
        # 기존 좋아요가 있는 경우 토글
        if existing_like.is_active:
            # 현재 활성화된 상태면 비활성화 (좋아요 취소)
            existing_like.is_active = False
            is_liked = False
        else:
            # 현재 비활성화된 상태면 활성화 (좋아요 재활성화)
            existing_like.is_active = True
            is_liked = True
    else:
        # 기존 좋아요가 없는 경우 새로 생성
        new_like = PostLike(
            post_type='free',
            post_id=post_id,
            user_id=current_user.id,
            is_active=True
        )
        db.add(new_like)
        is_liked = True
    
    db.commit()
    
    # 이벤트 리스너가 자동으로 like_count를 업데이트하므로 
    # 업데이트된 게시글 정보를 다시 조회
    db.refresh(post)
    
    return LikeResponse(is_liked=is_liked, like_count=post.like_count) 