from sqlalchemy import Column, BigInteger, String, Boolean, Integer, ARRAY
from sqlalchemy.orm import relationship
from app.db.models.timestamp_mixin import TimestampMixin
from app.db.database import Base

class FreeBoard(TimestampMixin, Base):
    __tablename__ = 'free_boards'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(String)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    
    # 자유 게시판 특화 설정
    allowed_categories = Column(ARRAY(String), default=['general', 'question', 'discussion', 'humor'])
    allow_anonymous = Column(Boolean, default=True)
    max_tags_count = Column(Integer, default=5)
    require_moderation = Column(Boolean, default=False)
    max_content_length = Column(Integer, default=10000)
    allow_image_upload = Column(Boolean, default=True)
    allow_video_upload = Column(Boolean, default=False)
    
    # 관계 설정
    posts = relationship('FreePost', back_populates='board', cascade='all, delete-orphan') 