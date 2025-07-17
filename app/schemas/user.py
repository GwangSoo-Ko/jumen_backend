from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class AccountBase(BaseModel):
    provider: str
    provider_user_id: Optional[str] = None
    email: EmailStr
    # password_hash, access_token, refresh_token 등은 응답에서 제외(보안)

class AccountResponse(AccountBase):
    id: int
    crt_date: Optional[datetime]
    mod_date: Optional[datetime]
    class Config:
        from_attributes = True
        orm_mode = True

class RefreshTokenResponse(BaseModel):
    id: int
    token: str
    expires_at: datetime
    crt_date: Optional[datetime]
    mod_date: Optional[datetime]
    user_agent: Optional[str]
    ip_address: Optional[str]
    class Config:
        from_attributes = True
        orm_mode = True

class UserBase(BaseModel):
    username: Optional[str] = None
    nickname: str
    profile_img: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    crt_date: Optional[datetime]
    mod_date: Optional[datetime]
    accounts: List[AccountResponse] = []
    refresh_tokens: List[RefreshTokenResponse] = []
    class Config:
        from_attributes = True
        orm_mode = True 