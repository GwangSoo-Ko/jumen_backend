from sqlalchemy import Column, BigInteger, String, Boolean, Integer, ARRAY, ForeignKey
from sqlalchemy.orm import relationship
from app.db.models.timestamp_mixin import TimestampMixin
from app.db.database import Base

class FreePost(TimestampMixin, Base):
    __tablename__ = 'free_posts'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    board_id = Column(BigInteger, ForeignKey('free_boards.id'), nullable=False)
    user_id = Column(BigInteger, ForeignKey('tb_user.id'), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(String, nullable=False)
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    is_deleted = Column(Boolean, default=False)
    is_notice = Column(Boolean, default=False)
    
    # 자유 게시판 특화 필드
    category = Column(String(50))  # 'general', 'question', 'discussion', 'humor'
    is_anonymous = Column(Boolean, default=False)
    is_pinned = Column(Boolean, default=False)  # 고정글 여부
    is_hot = Column(Boolean, default=False)  # 인기글 여부
    tags = Column(ARRAY(String))
    
    # 관계 설정
    board = relationship('FreeBoard', back_populates='posts')
    user = relationship('User', backref='free_posts')
    comments = relationship('FreeComment', back_populates='post', cascade='all, delete-orphan')
    attachments = relationship('FreeAttachment', back_populates='post', cascade='all, delete-orphan') 