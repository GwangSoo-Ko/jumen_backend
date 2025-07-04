from sqlalchemy import Column, BigInteger, String, Date
from sqlalchemy.ext.declarative import declarative_base
from app.db.models.timestamp_mixin import TimestampMixin

Base = declarative_base()

class StockInfo(TimestampMixin, Base):
    __tablename__ = "tb_stock_info"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    ticker = Column(String, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    market = Column(String)
    sector = Column(String)
    listed_date = Column(Date)
    size = Column(String)
    company_class = Column(String)
    listed_count = Column(BigInteger)
    warning_status = Column(String) 