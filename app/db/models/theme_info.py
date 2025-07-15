from sqlalchemy import Column, BigInteger, String, Numeric, Integer, Text, UniqueConstraint
from app.db.models.timestamp_mixin import TimestampMixin
from app.db.database import Base

class ThemeInfo(TimestampMixin, Base):
    __tablename__ = "tb_theme_info"
    __table_args__ = (
        UniqueConstraint('theme_code', 'theme_name', 'ref', name='tb_theme_info_code_name_ref_unique'),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    theme_code = Column(String, nullable=False)
    theme_name = Column(String, nullable=False)
    change_rate = Column(Numeric, nullable=False)
    avg_change_rate_3days = Column(Numeric, nullable=False)
    up_ticker_count = Column(Integer, nullable=False)
    neutral_ticker_count = Column(Integer, nullable=False)
    down_ticker_count = Column(Integer, nullable=False)
    detail_url = Column(Text, nullable=False)
    ref = Column(String, nullable=False, default='')
    description = Column(Text)