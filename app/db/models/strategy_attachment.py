from sqlalchemy import Column, BigInteger, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.models.timestamp_mixin import TimestampMixin
from app.db.database import Base

class StrategyAttachment(TimestampMixin, Base):
    __tablename__ = 'strategy_attachments'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    post_id = Column(BigInteger, ForeignKey('strategy_posts.id'), nullable=False)
    file_name = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String(100), nullable=False)
    download_count = Column(Integer, default=0)
    
    # 전략 첨부파일 특화 필드
    file_type = Column(String(50))  # 'chart', 'analysis', 'document', 'image'
    is_public = Column(Boolean, default=True)  # 공개 여부
    
    # 관계 설정
    post = relationship('StrategyPost', back_populates='attachments') 