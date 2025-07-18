from sqlalchemy import Column, BigInteger, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.models.timestamp_mixin import TimestampMixin
from app.db.database import Base

class FreeComment(TimestampMixin, Base):
    __tablename__ = 'free_comments'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    post_id = Column(BigInteger, ForeignKey('free_posts.id'), nullable=False)
    user_id = Column(BigInteger, ForeignKey('tb_user.id'), nullable=False)
    parent_id = Column(BigInteger, ForeignKey('free_comments.id'))
    content = Column(String, nullable=False)
    depth = Column(Integer, default=0)
    is_deleted = Column(Boolean, default=False)
    
    # 자유 댓글 특화 필드
    is_anonymous = Column(Boolean, default=False)
    is_best_answer = Column(Boolean, default=False)  # 베스트 답변 여부
    
    # 관계 설정
    post = relationship('FreePost', back_populates='comments')
    user = relationship('User', backref='free_comments')
    parent = relationship('FreeComment', remote_side=[id], backref='replies') 