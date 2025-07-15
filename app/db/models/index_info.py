from sqlalchemy import Column, BigInteger, Text
from app.db.database import Base
from app.db.models.timestamp_mixin import TimestampMixin

class IndexInfo(TimestampMixin, Base):
    __tablename__ = 'tb_index_info'

    id = Column(BigInteger, primary_key=True)
    name = Column(Text)
    description = Column(Text)