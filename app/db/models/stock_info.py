from sqlalchemy import Column, BigInteger, String, Numeric
from app.db.models.timestamp_mixin import TimestampMixin
from app.db.database import Base

class StockInfo(TimestampMixin, Base):
    __tablename__ = "tb_stock_info"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    ticker = Column(String, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    market = Column(String)
    stock_count = Column(BigInteger)
    market_cap = Column(BigInteger)
    bps = Column(BigInteger)
    per = Column(Numeric)
    pbr = Column(Numeric)
    eps = Column(BigInteger)
    div = Column(Numeric)
    dps = Column(BigInteger)