from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.models.timestamp_mixin import TimestampMixin
from app.db.database import Base

class RefreshToken(TimestampMixin, Base):
    __tablename__ = 'tb_refresh_token'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('tb_user.id', ondelete='CASCADE'), nullable=False)
    account_id = Column(BigInteger, ForeignKey('tb_account.id', ondelete='CASCADE'), nullable=False)
    token = Column(String(512), unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    user_agent = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user = relationship('User', back_populates='refresh_tokens')
    account = relationship('Account', back_populates='refresh_tokens') 