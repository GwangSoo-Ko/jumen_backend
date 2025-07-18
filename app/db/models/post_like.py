from sqlalchemy import Column, BigInteger, String, ForeignKey, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship
from app.db.models.timestamp_mixin import TimestampMixin
from app.db.database import Base

class PostLike(TimestampMixin, Base):
    __tablename__ = 'post_likes'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    post_type = Column(String(20), nullable=False)  # 'strategy', 'free'
    post_id = Column(BigInteger, nullable=False)
    user_id = Column(BigInteger, ForeignKey('tb_user.id'), nullable=False)
    is_active = Column(Boolean, default=True)  # 좋아요 활성화 상태 (취소 시 False)
    
    # 복합 유니크 제약조건
    __table_args__ = (
        UniqueConstraint('post_type', 'post_id', 'user_id', name='uq_post_like'),
    )
    
    # 관계 설정
    user = relationship('User', backref='post_likes') 