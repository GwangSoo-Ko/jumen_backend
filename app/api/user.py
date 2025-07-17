from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import SessionLocal
from app.db.models.user import User, SocialAccount
from app.schemas.user import UserCreate, UserResponse, SocialAccountCreate, SocialAccountResponse

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get('/users', response_model=List[UserResponse])
def read_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.get('/users/{user_id}', response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return user

@router.post('/users', response_model=UserResponse)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    user = User(
        username=user_in.username,
        email=user_in.email,
        password_hash=user_in.password if user_in.password else None,
        is_active=user_in.is_active,
        is_superuser=user_in.is_superuser
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post('/users/{user_id}/social', response_model=SocialAccountResponse)
def add_social_account(user_id: int, social_in: SocialAccountCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    social = SocialAccount(
        user_id=user_id,
        provider=social_in.provider,
        provider_user_id=social_in.provider_user_id,
        access_token=social_in.access_token,
        refresh_token=social_in.refresh_token
    )
    db.add(social)
    db.commit()
    db.refresh(social)
    return social

@router.get('/users/{user_id}/social', response_model=List[SocialAccountResponse])
def get_social_accounts(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return user.social_accounts 