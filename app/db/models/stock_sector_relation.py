from sqlalchemy import Column, BigInteger, ForeignKey, Numeric, Text
from app.db.models.timestamp_mixin import TimestampMixin
from app.db.database import Base 

class StockSectorRelation(TimestampMixin, Base):
    __tablename__ = 'tb_relation_stock_sector'

    stock_id = Column(BigInteger, ForeignKey('tb_stock_info.id'), primary_key=True)
    sector_id = Column(BigInteger, ForeignKey('tb_sector_info.id'), primary_key=True)
    current_price = Column(Numeric)
    diff_price = Column(Numeric)
    change_rate = Column(Numeric)
    volume = Column(BigInteger)
    trading_value = Column(Numeric)
    volume_yesterday = Column(BigInteger) 
