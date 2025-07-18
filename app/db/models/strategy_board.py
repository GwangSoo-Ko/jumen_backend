from sqlalchemy import Column, BigInteger, String, Boolean, Integer, ARRAY
from sqlalchemy.orm import relationship
from app.db.models.timestamp_mixin import TimestampMixin
from app.db.database import Base

class StrategyBoard(TimestampMixin, Base):
    __tablename__ = 'strategy_boards'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(String)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    
    # 전략 게시판 특화 설정
    max_risk_level = Column(Integer, default=5)
    allowed_strategy_types = Column(ARRAY(String), default=['buy', 'sell', 'hold', 'analysis'])
    require_stock_reference = Column(Boolean, default=False)
    require_theme_reference = Column(Boolean, default=False)
    allow_anonymous = Column(Boolean, default=False)
    max_tags_count = Column(Integer, default=10)
    require_target_price = Column(Boolean, default=False)
    require_risk_assessment = Column(Boolean, default=True)
    
    # 관계 설정
    posts = relationship('StrategyPost', back_populates='board', cascade='all, delete-orphan') 