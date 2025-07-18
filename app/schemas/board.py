from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
from decimal import Decimal

# 정렬 옵션
class SortOrder(str, Enum):
    LATEST = "latest"      # 최신순
    OLDEST = "oldest"      # 오래된순
    VIEWS = "views"        # 조회수순
    LIKES = "likes"        # 좋아요순
    COMMENTS = "comments"  # 댓글수순

# 전략 타입
class StrategyType(str, Enum):
    BUY = "buy"           # 매수
    SELL = "sell"         # 매도
    HOLD = "hold"         # 보유
    ANALYSIS = "analysis" # 분석

# 보유기간
class HoldingPeriod(str, Enum):
    SHORT = "short"       # 단기 (1개월 이하)
    MEDIUM = "medium"     # 중기 (1-6개월)
    LONG = "long"         # 장기 (6개월 이상)

# 게시글 목록 조회 요청
class PostListRequest(BaseModel):
    page: int = Field(1, ge=1, description="페이지 번호")
    size: int = Field(10, ge=1, le=100, description="페이지 크기")
    search: Optional[str] = Field(None, description="검색어")
    sort: SortOrder = Field(SortOrder.LATEST, description="정렬 기준")

# 게시글 작성 요청
class PostCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="제목")
    content: str = Field(..., min_length=1, description="내용")
    is_notice: bool = Field(False, description="공지사항 여부")
    
    # 전략 게시판 특화 필드
    strategy_type: Optional[StrategyType] = Field(None, description="전략 타입")
    target_price: Optional[Decimal] = Field(None, ge=0, description="목표가")
    risk_level: Optional[int] = Field(None, ge=1, le=5, description="위험도 (1-5)")
    performance_rating: Optional[int] = Field(None, ge=1, le=5, description="성과 평가 (1-5)")
    entry_price: Optional[Decimal] = Field(None, ge=0, description="진입가")
    exit_price: Optional[Decimal] = Field(None, ge=0, description="청산가")
    holding_period: Optional[HoldingPeriod] = Field(None, description="보유기간")
    related_stock_id: Optional[int] = Field(None, description="관련 주식 ID")
    related_theme_id: Optional[int] = Field(None, description="관련 테마 ID")
    tags: Optional[List[str]] = Field(None, description="태그 목록")

# 게시글 수정 요청
class PostUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="제목")
    content: Optional[str] = Field(None, min_length=1, description="내용")
    is_notice: Optional[bool] = Field(None, description="공지사항 여부")
    
    # 전략 게시판 특화 필드
    strategy_type: Optional[StrategyType] = Field(None, description="전략 타입")
    target_price: Optional[Decimal] = Field(None, ge=0, description="목표가")
    risk_level: Optional[int] = Field(None, ge=1, le=5, description="위험도 (1-5)")
    performance_rating: Optional[int] = Field(None, ge=1, le=5, description="성과 평가 (1-5)")
    entry_price: Optional[Decimal] = Field(None, ge=0, description="진입가")
    exit_price: Optional[Decimal] = Field(None, ge=0, description="청산가")
    holding_period: Optional[HoldingPeriod] = Field(None, description="보유기간")
    related_stock_id: Optional[int] = Field(None, description="관련 주식 ID")
    related_theme_id: Optional[int] = Field(None, description="관련 테마 ID")
    tags: Optional[List[str]] = Field(None, description="태그 목록")

# 댓글 작성 요청
class CommentCreateRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000, description="댓글 내용")
    parent_id: Optional[int] = Field(None, description="부모 댓글 ID (대댓글인 경우)")

# 댓글 수정 요청
class CommentUpdateRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000, description="댓글 내용")

# 첨부파일 응답
class AttachmentResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_size: int
    file_path: str
    crt_date: datetime
    
    class Config:
        from_attributes = True

# 댓글 응답
class CommentResponse(BaseModel):
    id: int
    content: str
    depth: int
    parent_id: Optional[int]
    user_id: int
    user_nickname: str
    user_profile_img: Optional[str]
    like_count: int
    is_liked: bool = False
    crt_date: datetime
    mod_date: Optional[datetime]
    children: List['CommentResponse'] = []
    
    class Config:
        from_attributes = True

# 게시글 목록 응답
class PostListResponse(BaseModel):
    id: int
    title: str
    content_preview: str
    user_id: int
    user_nickname: str
    user_profile_img: Optional[str]
    view_count: int
    like_count: int
    comment_count: int
    is_notice: bool
    is_liked: bool = False
    crt_date: datetime
    mod_date: Optional[datetime]
    
    # 전략 게시판 특화 필드
    strategy_type: Optional[StrategyType] = None
    target_price: Optional[Decimal] = None
    risk_level: Optional[int] = None
    performance_rating: Optional[int] = None
    entry_price: Optional[Decimal] = None
    exit_price: Optional[Decimal] = None
    holding_period: Optional[HoldingPeriod] = None
    related_stock_id: Optional[int] = None
    related_theme_id: Optional[int] = None
    tags: Optional[List[str]] = None
    
    class Config:
        from_attributes = True

# 게시글 상세 응답
class PostDetailResponse(BaseModel):
    id: int
    title: str
    content: str
    user_id: int
    user_nickname: str
    user_profile_img: Optional[str]
    view_count: int
    like_count: int
    comment_count: int
    is_notice: bool
    is_liked: bool = False
    crt_date: datetime
    mod_date: Optional[datetime]
    attachments: List[AttachmentResponse] = []
    comments: List[CommentResponse] = []
    
    # 전략 게시판 특화 필드
    strategy_type: Optional[StrategyType] = None
    target_price: Optional[Decimal] = None
    risk_level: Optional[int] = None
    performance_rating: Optional[int] = None
    entry_price: Optional[Decimal] = None
    exit_price: Optional[Decimal] = None
    holding_period: Optional[HoldingPeriod] = None
    related_stock_id: Optional[int] = None
    related_theme_id: Optional[int] = None
    tags: Optional[List[str]] = None
    
    class Config:
        from_attributes = True

# 좋아요 응답
class LikeResponse(BaseModel):
    is_liked: bool
    like_count: int

# 페이지네이션 응답
class PaginatedResponse(BaseModel):
    items: List[PostListResponse]
    total: int
    page: int
    size: int
    total_pages: int 