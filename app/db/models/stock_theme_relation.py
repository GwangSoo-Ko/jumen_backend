from sqlalchemy import Column, BigInteger, ForeignKey, Numeric, Text
from sqlalchemy.orm import declarative_base
from app.db.models.timestamp_mixin import TimestampMixin

Base = declarative_base()

class StockThemeRelation(TimestampMixin, Base):
    __tablename__ = 'tb_relation_stock_theme'

    stock_id = Column(BigInteger, ForeignKey('tb_stock_info.id'), primary_key=True)
    theme_id = Column(BigInteger, ForeignKey('tb_theme_info.id'), primary_key=True)
    current_price = Column(Numeric)
    diff_price = Column(Numeric)
    change_rate = Column(Numeric)
    volume = Column(BigInteger)
    trading_value = Column(Numeric)
    volume_yesterday = Column(BigInteger) 
    description = Column(Text)      