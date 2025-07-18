from sqlalchemy import Column, BigInteger, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.models.timestamp_mixin import TimestampMixin
from app.db.database import Base

class StrategyComment(TimestampMixin, Base):
    __tablename__ = 'strategy_comments'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    post_id = Column(BigInteger, ForeignKey('strategy_posts.id'), nullable=False)
    user_id = Column(BigInteger, ForeignKey('tb_user.id'), nullable=False)
    parent_id = Column(BigInteger, ForeignKey('strategy_comments.id'))
    content = Column(String, nullable=False)
    depth = Column(Integer, default=0)
    is_deleted = Column(Boolean, default=False)
    
    # 전략 댓글 특화 필드
    is_analysis = Column(Boolean, default=False)  # 분석 댓글 여부
    confidence_level = Column(Integer)  # 신뢰도 1-5
    
    # 관계 설정
    post = relationship('StrategyPost', back_populates='comments')
    user = relationship('User', backref='strategy_comments')
    parent = relationship('StrategyComment', remote_side=[id], backref='replies') 