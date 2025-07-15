from app.db.database import Base
from sqlalchemy import Column, BigInteger, Numeric, Date, ForeignKey

class IndexOhlcv(Base):
    __tablename__ = 'tb_index_ohlcv'

    index_id = Column(BigInteger, ForeignKey('tb_index_info.id'), primary_key=True)
    ymd = Column(Date, primary_key=True)
    open = Column(Numeric)
    high = Column(Numeric)
    low = Column(Numeric)
    close = Column(Numeric)
    volume = Column(BigInteger)