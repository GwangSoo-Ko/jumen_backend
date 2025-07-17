import os
import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models.user import User, SocialAccount
from app.schemas.user import UserResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/auth/google/login")
def google_login():
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        "?response_type=code"
        f"&client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={GOOGLE_REDIRECT_URI}"
        "&scope=openid%20email%20profile"
        "&access_type=offline"
        "&prompt=consent"
    )
    logger.info(f"Google auth URL: {google_auth_url}")
    return {"auth_url": google_auth_url}

@router.get("/auth/google/callback", response_model=UserResponse)
async def google_callback(code: str, db: Session = Depends(get_db)):
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(token_url, data=data)
        if token_resp.status_code != 200:
            logger.error(f"구글 토큰 요청 실패: {token_resp.status_code}")
            raise HTTPException(status_code=400, detail="구글 토큰 요청 실패")
        tokens = token_resp.json()
    access_token = tokens.get("access_token")
    if not access_token:
        logger.error("구글 access_token 획득 실패")
        raise HTTPException(status_code=400, detail="구글 access_token 획득 실패")
    userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        userinfo_resp = await client.get(userinfo_url, headers=headers)
        if userinfo_resp.status_code != 200:
            logger.error(f"구글 사용자 정보 조회 실패: {userinfo_resp.status_code}")
            raise HTTPException(status_code=400, detail="구글 사용자 정보 조회 실패")
        userinfo = userinfo_resp.json()
    email = userinfo["email"]
    google_id = userinfo["id"]
    username = userinfo.get("name", email.split("@")[0])
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(username=username, email=email, is_active=True)
        db.add(user)
        db.commit()
        db.refresh(user)
    social = (
        db.query(SocialAccount)
        .filter(SocialAccount.provider == "google", SocialAccount.provider_user_id == google_id)
        .first()
    )
    if not social:
        social = SocialAccount(
            user_id=user.id,
            provider="google",
            provider_user_id=google_id,
            access_token=access_token,
            refresh_token=tokens.get("refresh_token"),
        )
        db.add(social)
        db.commit()
    return user 