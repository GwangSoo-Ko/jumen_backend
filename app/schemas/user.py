from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class SocialAccountBase(BaseModel):
    provider: str
    provider_user_id: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None

class SocialAccountCreate(SocialAccountBase):
    pass

class SocialAccountResponse(SocialAccountBase):
    id: int
    crt_date: Optional[datetime]
    mod_date: Optional[datetime]

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False

class UserCreate(UserBase):
    password: Optional[str] = None  # 소셜 계정은 비밀번호 없이 생성 가능

class UserResponse(UserBase):
    id: int
    last_login: Optional[datetime]
    crt_date: Optional[datetime]
    mod_date: Optional[datetime]
    social_accounts: List[SocialAccountResponse] = []

    class Config:
        orm_mode = True 