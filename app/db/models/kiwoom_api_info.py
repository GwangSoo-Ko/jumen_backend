from sqlalchemy import Column, BigInteger, String, TIMESTAMP
from app.db.models.timestamp_mixin import TimestampMixin
from app.db.database import Base

class KiwoomApiInfo(TimestampMixin, Base):
    __tablename__ = "tb_kiwoom_api_info"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    account_no = Column(String)
    investment_mode = Column(String)
    investment_type = Column(String)
    api_url = Column(String)
    app_key = Column(String)
    secret_key = Column(String)
    valid_token = Column(String)
    token_expire_date = Column(TIMESTAMP(timezone=True)) 