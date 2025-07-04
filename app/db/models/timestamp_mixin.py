from sqlalchemy import Column, TIMESTAMP
from sqlalchemy.sql import func

class TimestampMixin:
    crt_date = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=True)
    mod_date = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True) 