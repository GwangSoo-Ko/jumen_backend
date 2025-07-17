from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.models.timestamp_mixin import TimestampMixin
from app.db.database import Base

class User(TimestampMixin, Base):
    __tablename__ = 'tb_user'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=True)  # 소셜 전용 계정은 null 허용
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    social_accounts = relationship('SocialAccount', back_populates='user', cascade='all, delete-orphan')

class SocialAccount(TimestampMixin, Base):
    __tablename__ = 'tb_social_account'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('tb_user.id'), nullable=False)
    provider = Column(String(50), nullable=False)  # 'google', 'facebook' 등
    provider_user_id = Column(String(128), nullable=False)
    access_token = Column(String(256), nullable=True)
    refresh_token = Column(String(256), nullable=True)
    user = relationship('User', back_populates='social_accounts')
    __table_args__ = (UniqueConstraint('provider', 'provider_user_id', name='uq_provider_user_id'),) 