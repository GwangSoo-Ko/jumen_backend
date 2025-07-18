from sqlalchemy import Column, BigInteger, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.models.timestamp_mixin import TimestampMixin
from app.db.database import Base

class FreeAttachment(TimestampMixin, Base):
    __tablename__ = 'free_attachments'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    post_id = Column(BigInteger, ForeignKey('free_posts.id'), nullable=False)
    file_name = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String(100), nullable=False)
    download_count = Column(Integer, default=0)
    
    # 자유 첨부파일 특화 필드
    file_type = Column(String(50))  # 'image', 'video', 'document', 'other'
    thumbnail_path = Column(String(500))  # 썸네일 경로
    
    # 관계 설정
    post = relationship('FreePost', back_populates='attachments') 