from sqlalchemy import Column, BigInteger, Text, Boolean
from app.db.database import Base
from app.db.models.timestamp_mixin import TimestampMixin

class IndexInfo(TimestampMixin, Base):
    __tablename__ = 'tb_index_info'

    id = Column(BigInteger, primary_key=True)
    order_no = Column(BigInteger)
    is_active = Column(Boolean, default=True)
    name = Column(Text, unique=True)
    description = Column(Text)
    