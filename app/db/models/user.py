from sqlalchemy import Column, BigInteger, String, Boolean
from sqlalchemy.orm import relationship
from app.db.models.timestamp_mixin import TimestampMixin
from app.db.database import Base

class User(TimestampMixin, Base):
    __tablename__ = 'tb_user'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=True)
    nickname = Column(String(100), unique=True, nullable=False)
    profile_img = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    accounts = relationship('Account', back_populates='user', cascade='all, delete-orphan')
    refresh_tokens = relationship('RefreshToken', back_populates='user', cascade='all, delete-orphan') 