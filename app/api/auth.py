import os
import httpx
from fastapi import APIRouter, Depends, HTTPException, Body, Response, status, Request
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models.user import User
from app.db.models.account import Account
from app.db.models.refresh_token import RefreshToken
from app.schemas.user import UserResponse, AccountResponse
import logging
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
import random
import string
from jose import jwt
from datetime import datetime, timedelta, timezone
import hashlib
import secrets
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, ExpiredSignatureError

logger = logging.getLogger(__name__)

router = APIRouter()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 14

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def generate_nickname(base, db):
    salt = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    nickname = f"{base}_{salt}"
    while db.query(User).filter(User.nickname == nickname).first():
        salt = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        nickname = f"{base}_{salt}"
    return nickname

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def create_refresh_token():
    return secrets.token_urlsafe(64)

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str
    refresh_token_expires_at: str
    user: UserResponse

class ChangeNicknameRequest(BaseModel):
    user_id: int
    new_nickname: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/auth/email/register", response_model=UserResponse)
def email_register(req: RegisterRequest, db: Session = Depends(get_db)):
    nickname = generate_nickname(req.username, db)
    # 이메일+provider 중복 체크 (Account)
    if db.query(Account).filter(Account.provider == 'email', Account.email == req.email).first():
        raise HTTPException(status_code=400, detail="이미 사용 중인 이메일입니다.")
    user = User(nickname=nickname, username=req.username, is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    hashed_pw = get_password_hash(req.password)
    account = Account(
        user_id=user.id,
        provider='email',
        email=req.email,
        password_hash=hashed_pw
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    user.accounts.append(account)
    db.commit()
    return user

@router.post("/auth/email/login", response_model=LoginResponse)
def email_login(req: LoginRequest, response: Response, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.provider == 'email', Account.email == req.email).first()
    if not account or not account.password_hash:
        raise HTTPException(status_code=400, detail="이메일 또는 비밀번호가 올바르지 않습니다.")
    if not verify_password(req.password, account.password_hash):
        raise HTTPException(status_code=400, detail="이메일 또는 비밀번호가 올바르지 않습니다.")
    access_token = create_access_token(
        data={
            "sub": str(account.user_id),
            "account_id": account.id,
            "provider": account.provider,
            "email": account.email
        }
    )
    refresh_token = create_refresh_token()
    refresh_expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token_obj = RefreshToken(
        user_id=account.user_id,
        account_id=account.id,
        token=hash_token(refresh_token),
        expires_at=refresh_expires_at
    )
    db.add(refresh_token_obj)
    db.commit()
    db.refresh(refresh_token_obj)
    # refresh_token을 HTTP Only 쿠키로도 내려줌(보안 강화)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    user = db.query(User).filter(User.id == account.user_id).first()
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
        "refresh_token_expires_at": refresh_expires_at.isoformat(),
        "user": UserResponse.model_validate(user)
    }

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

@router.get("/auth/google/callback", response_model=LoginResponse)
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
    # username은 구글 name 그대로, nickname은 username+salt로 자동 생성
    account = db.query(Account).filter(Account.provider == 'google', Account.provider_user_id == google_id).first()
    if account:
        user = db.query(User).filter(User.id == account.user_id).first()
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "account_id": account.id,
                "provider": account.provider,
                "email": account.email
            }
        )
        refresh_token = create_refresh_token()
        refresh_expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token_obj = RefreshToken(
            user_id=user.id,
            account_id=account.id,
            token=hash_token(refresh_token),
            expires_at=refresh_expires_at
        )
        db.add(refresh_token_obj)
        db.commit()
        db.refresh(refresh_token_obj)
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "refresh_token": refresh_token,
            "refresh_token_expires_at": refresh_expires_at.isoformat(),
            "user": UserResponse.model_validate(user)
        }
    # 신규 유저 생성
    nickname = generate_nickname(username, db)
    user = User(username=username, nickname=nickname, is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    account = Account(
        user_id=user.id,
        provider='google',
        provider_user_id=google_id,
        email=email,
        access_token=access_token,
        refresh_token=tokens.get("refresh_token")
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    user.accounts.append(account)
    db.commit()
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "account_id": account.id,
            "provider": account.provider,
            "email": account.email
        }
    )
    refresh_token = create_refresh_token()
    refresh_expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token_obj = RefreshToken(
        user_id=user.id,
        account_id=account.id,
        token=hash_token(refresh_token),
        expires_at=refresh_expires_at
    )
    db.add(refresh_token_obj)
    db.commit()
    db.refresh(refresh_token_obj)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
        "refresh_token_expires_at": refresh_expires_at.isoformat(),
        "user": UserResponse.model_validate(user)
    }

@router.post("/auth/change-nickname")
def change_nickname(req: ChangeNicknameRequest, db: Session = Depends(get_db)):
    # 닉네임 중복 체크
    if db.query(User).filter(User.nickname == req.new_nickname).first():
        raise HTTPException(status_code=400, detail="이미 사용 중인 닉네임입니다.")
    user = db.query(User).filter(User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    user.nickname = req.new_nickname
    db.commit()
    db.refresh(user)
    return {"id": user.id, "nickname": user.nickname}

class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/auth/refresh", response_model=LoginResponse)
def refresh_token_api(request: Request, response: Response, db: Session = Depends(get_db)):
    # 쿠키에서 refresh_token 읽기
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="리프레시 토큰이 없습니다.")
    
    hashed = hash_token(refresh_token)
    token_obj = db.query(RefreshToken).filter(RefreshToken.token == hashed).first()
    if not token_obj or token_obj.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="리프레시 토큰이 유효하지 않거나 만료되었습니다.")
    account = db.query(Account).filter(Account.id == token_obj.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="계정을 찾을 수 없습니다.")
    # 기존 refresh_token 폐기(로테이션)
    db.delete(token_obj)
    db.commit()
    # 새 refresh_token 발급
    new_refresh_token = create_refresh_token()
    refresh_expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    new_token_obj = RefreshToken(
        user_id=account.user_id,
        account_id=account.id,
        token=hash_token(new_refresh_token),
        expires_at=refresh_expires_at
    )
    db.add(new_token_obj)
    db.commit()
    db.refresh(new_token_obj)
    access_token = create_access_token(
        data={
            "sub": str(account.user_id),
            "account_id": account.id,
            "provider": account.provider,
            "email": account.email
        }
    )
    user = db.query(User).filter(User.id == account.user_id).first()
    # refresh_token을 HTTP Only 쿠키로도 내려줌(보안 강화)
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": new_refresh_token,
        "refresh_token_expires_at": refresh_expires_at.isoformat(),
        "user": UserResponse.model_validate(user)
    }

class LogoutRequest(BaseModel):
    refresh_token: str

@router.post("/auth/logout")
def logout(request: Request, db: Session = Depends(get_db)):
    # 쿠키에서 refresh_token 읽기
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        hashed = hash_token(refresh_token)
        token_obj = db.query(RefreshToken).filter(RefreshToken.token == hashed).first()
        if token_obj:
            db.delete(token_obj)
            db.commit()
    return {"detail": "로그아웃 및 리프레시 토큰 폐기 완료"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise credentials_exception
        return user
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="토큰이 만료되었습니다.")
    except JWTError:
        raise credentials_exception

def require_superuser(current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
    return current_user

@router.get("/auth/me", response_model=UserResponse)
def get_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found") 
        return UserResponse.model_validate(user)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token") 

@router.get("/admin-only")
def admin_api(current_user: User = Depends(require_superuser)):
    return {"msg": "관리자만 접근 가능"}