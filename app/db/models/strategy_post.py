from sqlalchemy import Column, BigInteger, String, Boolean, Integer, ARRAY, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from app.db.models.timestamp_mixin import TimestampMixin
from app.db.database import Base

class StrategyPost(TimestampMixin, Base):
    __tablename__ = 'strategy_posts'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    board_id = Column(BigInteger, ForeignKey('strategy_boards.id'), nullable=True)
    user_id = Column(BigInteger, ForeignKey('tb_user.id'), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(String, nullable=False)
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    is_deleted = Column(Boolean, default=False)
    is_notice = Column(Boolean, default=False)
    
    # 전략 게시판 특화 필드
    related_stock_id = Column(BigInteger, ForeignKey('tb_stock_info.id'))
    related_theme_id = Column(BigInteger, ForeignKey('tb_theme_info.id'))
    strategy_type = Column(String(20))  # 'buy', 'sell', 'hold', 'analysis'
    target_price = Column(DECIMAL(10, 2))
    risk_level = Column(Integer)  # 1-5
    performance_rating = Column(Integer)  # 1-5
    entry_price = Column(DECIMAL(10, 2))
    exit_price = Column(DECIMAL(10, 2))
    holding_period = Column(String(50))  # 'short', 'medium', 'long'
    tags = Column(ARRAY(String))
    
    # 관계 설정
    board = relationship('StrategyBoard', back_populates='posts')
    user = relationship('User', backref='strategy_posts')
    related_stock = relationship('StockInfo')
    related_theme = relationship('ThemeInfo')
    comments = relationship('StrategyComment', back_populates='post', cascade='all, delete-orphan')
    attachments = relationship('StrategyAttachment', back_populates='post', cascade='all, delete-orphan') 