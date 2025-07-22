from sqlalchemy import Column, BigInteger, String, Numeric, Integer, Text, UniqueConstraint
from app.db.models.timestamp_mixin import TimestampMixin
from app.db.database import Base

class SectorInfo(TimestampMixin, Base):
    __tablename__ = "tb_sector_info"
    __table_args__ = (
        UniqueConstraint('sector_code', 'sector_name', 'ref', name='tb_sector_info_code_name_ref_unique'),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    sector_code = Column(String, nullable=False)
    sector_name = Column(String, nullable=False)
    change_rate = Column(Numeric, nullable=False)
    up_ticker_count = Column(Integer, nullable=False)
    neutral_ticker_count = Column(Integer, nullable=False)
    down_ticker_count = Column(Integer, nullable=False)
    detail_url = Column(Text, nullable=False)
    ref = Column(String, nullable=False, default='')
