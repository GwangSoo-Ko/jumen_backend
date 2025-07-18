from sqlalchemy import Column, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.models.timestamp_mixin import TimestampMixin
from app.db.database import Base

class PostView(TimestampMixin, Base):
    __tablename__ = 'post_views'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    post_type = Column(String(20), nullable=False)  # 'strategy', 'free'
    post_id = Column(BigInteger, nullable=False)
    user_id = Column(BigInteger, ForeignKey('tb_user.id'))
    ip_address = Column(String(45))  # IPv6 지원
    user_agent = Column(String)
    
    # 관계 설정
    user = relationship('User', backref='post_views') 