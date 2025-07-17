from sqlalchemy import Column, BigInteger, String, ForeignKey, UniqueConstraint, Text
from sqlalchemy.orm import relationship
from app.db.models.timestamp_mixin import TimestampMixin
from app.db.database import Base

class Account(TimestampMixin, Base):
    __tablename__ = 'tb_account'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('tb_user.id', ondelete='CASCADE'), nullable=False)
    provider = Column(String(32), nullable=False)
    provider_user_id = Column(String(128), nullable=True)
    email = Column(String(120), nullable=False)
    password_hash = Column(String(128), nullable=True)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    user = relationship('User', back_populates='accounts')
    refresh_tokens = relationship('RefreshToken', back_populates='account', cascade='all, delete-orphan')
    __table_args__ = (
        UniqueConstraint('provider', 'provider_user_id', name='uq_account_provider_user_id'),
        UniqueConstraint('provider', 'email', name='uq_account_provider_email'),
    ) 