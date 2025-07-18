from sqlalchemy import event, func, inspect
from sqlalchemy.orm import Session
from app.db.models.strategy_post import StrategyPost
from app.db.models.free_post import FreePost
from app.db.models.strategy_comment import StrategyComment
from app.db.models.free_comment import FreeComment
from app.db.models.post_like import PostLike
from app.db.models.post_view import PostView

# 전략 게시글 조회수 자동 업데이트
@event.listens_for(PostView, 'after_insert')
def update_strategy_post_view_count(mapper, connection, target):
    if target.post_type == 'strategy':
        # 전략 게시글 조회수 업데이트
        connection.execute(
            StrategyPost.__table__.update()
            .where(StrategyPost.id == target.post_id)
            .values(view_count=StrategyPost.view_count + 1)
        )

@event.listens_for(PostView, 'after_insert')
def update_free_post_view_count(mapper, connection, target):
    if target.post_type == 'free':
        # 자유 게시글 조회수 업데이트
        connection.execute(
            FreePost.__table__.update()
            .where(FreePost.id == target.post_id)
            .values(view_count=FreePost.view_count + 1)
        )

# 전략 게시글 댓글 수 자동 업데이트
@event.listens_for(StrategyComment, 'after_insert')
def update_strategy_post_comment_count_insert(mapper, connection, target):
    connection.execute(
        StrategyPost.__table__.update()
        .where(StrategyPost.id == target.post_id)
        .values(comment_count=StrategyPost.comment_count + 1)
    )

@event.listens_for(StrategyComment, 'after_delete')
def update_strategy_post_comment_count_delete(mapper, connection, target):
    connection.execute(
        StrategyPost.__table__.update()
        .where(StrategyPost.id == target.post_id)
        .values(comment_count=StrategyPost.comment_count - 1)
    )

# 자유 게시글 댓글 수 자동 업데이트
@event.listens_for(FreeComment, 'after_insert')
def update_free_post_comment_count_insert(mapper, connection, target):
    connection.execute(
        FreePost.__table__.update()
        .where(FreePost.id == target.post_id)
        .values(comment_count=FreePost.comment_count + 1)
    )

@event.listens_for(FreeComment, 'after_delete')
def update_free_post_comment_count_delete(mapper, connection, target):
    connection.execute(
        FreePost.__table__.update()
        .where(FreePost.id == target.post_id)
        .values(comment_count=FreePost.comment_count - 1)
    )

# 전략 게시글 좋아요 수 자동 업데이트
@event.listens_for(PostLike, 'after_insert')
def update_strategy_post_like_count_insert(mapper, connection, target):
    if target.post_type == 'strategy':
        connection.execute(
            StrategyPost.__table__.update()
            .where(StrategyPost.id == target.post_id)
            .values(like_count=StrategyPost.like_count + 1)
        )

@event.listens_for(PostLike, 'after_delete')
def update_strategy_post_like_count_delete(mapper, connection, target):
    if target.post_type == 'strategy':
        connection.execute(
            StrategyPost.__table__.update()
            .where(StrategyPost.id == target.post_id)
            .values(like_count=func.greatest(StrategyPost.like_count - 1, 0))
        )

# 자유 게시글 좋아요 수 자동 업데이트
@event.listens_for(PostLike, 'after_insert')
def update_free_post_like_count_insert(mapper, connection, target):
    if target.post_type == 'free':
        connection.execute(
            FreePost.__table__.update()
            .where(FreePost.id == target.post_id)
            .values(like_count=FreePost.like_count + 1)
        )

@event.listens_for(PostLike, 'after_delete')
def update_free_post_like_count_delete(mapper, connection, target):
    if target.post_type == 'free':
        connection.execute(
            FreePost.__table__.update()
            .where(FreePost.id == target.post_id)
            .values(like_count=func.greatest(FreePost.like_count - 1, 0))
        )

# 좋아요 상태 변경 시 카운트 자동 업데이트 (is_active 필드 변경 감지)
@event.listens_for(PostLike, 'before_update')
def detect_is_active_change(mapper, connection, target):
    """is_active 필드 변경을 감지하여 플래그 설정"""
    # SQLAlchemy inspect를 사용하여 변경된 필드 확인
    insp = inspect(target)
    
    # is_active 필드가 변경되었는지 확인
    if insp.attrs.is_active.history.has_changes():
        target._is_active_changed = True
        # 변경 이력에서 이전 값과 현재 값 저장
        history = insp.attrs.is_active.history
        if len(history.deleted) > 0:
            target._previous_is_active = history.deleted[0]
        else:
            target._previous_is_active = not target.is_active

@event.listens_for(PostLike, 'after_update')
def update_post_like_count_on_status_change(mapper, connection, target):
    # is_active 필드가 변경되었는지 확인
    if hasattr(target, '_is_active_changed') and target._is_active_changed:
        if target.post_type == 'strategy':
            # 전략 게시글 좋아요 카운트 업데이트
            if target.is_active:
                # 좋아요 활성화 (카운트 증가)
                connection.execute(
                    StrategyPost.__table__.update()
                    .where(StrategyPost.id == target.post_id)
                    .values(like_count=StrategyPost.like_count + 1)
                )
            else:
                # 좋아요 비활성화 (카운트 감소) - 음수 방지
                connection.execute(
                    StrategyPost.__table__.update()
                    .where(StrategyPost.id == target.post_id)
                    .values(like_count=func.greatest(StrategyPost.like_count - 1, 0))
                )
        elif target.post_type == 'free':
            # 자유 게시글 좋아요 카운트 업데이트
            if target.is_active:
                # 좋아요 활성화 (카운트 증가)
                connection.execute(
                    FreePost.__table__.update()
                    .where(FreePost.id == target.post_id)
                    .values(like_count=FreePost.like_count + 1)
                )
            else:
                # 좋아요 비활성화 (카운트 감소) - 음수 방지
                connection.execute(
                    FreePost.__table__.update()
                    .where(FreePost.id == target.post_id)
                    .values(like_count=func.greatest(FreePost.like_count - 1, 0))
                )
        
        # 플래그 초기화
        target._is_active_changed = False
        if hasattr(target, '_previous_is_active'):
            delattr(target, '_previous_is_active')

# 댓글 depth 자동 계산
@event.listens_for(StrategyComment, 'before_insert')
def calculate_strategy_comment_depth(mapper, connection, target):
    if target.parent_id:
        # 부모 댓글의 depth를 조회하여 +1
        result = connection.execute(
            StrategyComment.__table__.select()
            .where(StrategyComment.id == target.parent_id)
        ).first()
        if result:
            target.depth = result.depth + 1

@event.listens_for(FreeComment, 'before_insert')
def calculate_free_comment_depth(mapper, connection, target):
    if target.parent_id:
        # 부모 댓글의 depth를 조회하여 +1
        result = connection.execute(
            FreeComment.__table__.select()
            .where(FreeComment.id == target.parent_id)
        ).first()
        if result:
            target.depth = result.depth + 1 