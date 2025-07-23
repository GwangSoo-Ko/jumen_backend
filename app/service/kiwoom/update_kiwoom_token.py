import logging
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models.kiwoom_api_info import KiwoomApiInfo
from app.config import os as app_os
from app.service.kiwoom import kiwoom_client, constant
import pytz
KST = pytz.timezone('Asia/Seoul')

# .env 환경변수 로드 및 ENV 확인
load_dotenv()
ENV = os.getenv('ENV', 'development')

# 로그 디렉토리 및 파일 설정
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_filepath = os.path.join(log_dir, 'kiwoom_token.log')

logger = logging.getLogger('app.service.kiwoom')
logger.setLevel(logging.INFO)
for handler in logger.handlers[:]:
    logger.removeHandler(handler)
file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
if ENV != 'production':
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

def get_valid_token(db: Session, account_no: str):
    now = datetime.now(timezone.utc)
    row = db.query(KiwoomApiInfo).filter(
        KiwoomApiInfo.account_no == account_no,
        KiwoomApiInfo.valid_token.isnot(None),
        KiwoomApiInfo.token_expire_date > now
    ).first()
    if row:
        logger.info(f"유효한 토큰 조회 성공: {account_no}")
        return row.api_url, row.valid_token
    else:
        logger.info(f"유효한 토큰 없음: {account_no}")
        return None

def update_kiwoom_token(db: Session, row: KiwoomApiInfo, new_token: str, expire_date: datetime):
    row.valid_token = new_token
    row.token_expire_date = expire_date
    row.mod_date = datetime.now(timezone.utc)
    db.commit()
    logger.info(f"토큰 갱신: {row.account_no}, 만료일: {expire_date}")

def get_kiwoom_api_keys(db: Session, account_no: str):
    """
    tb_kiwoom_api_info 테이블에서 해당 account_no의 app_key, secret_key를 반환한다.
    """
    row = db.query(KiwoomApiInfo).filter(KiwoomApiInfo.account_no == account_no).first()
    if row:
        logger.info(f"API 키 조회 성공: {account_no}")
        return row.app_key, row.secret_key, row.api_url
    logger.warning(f"API 키 조회 실패: {account_no}")
    return None, None, None

def get_kiwoom_api_url_and_valid_token():
    account_no = app_os.getenv("ACCOUNT_NO")
    if not account_no:
        logger.error(".env 파일에 ACCOUNT_NO가 정의되어 있어야 합니다.")
        return None, None
    db = SessionLocal()
    try:
        result = get_valid_token(db, account_no)
        if result is None:
            # 유효한 토큰이 없는 경우 새로운 토큰 발급 시도
            app_key, secret_key, api_url = get_kiwoom_api_keys(db, account_no)
            if api_url is None or app_key is None or secret_key is None:
                logger.error("키움 API 정보 없음")
                return None, None
            logger.info(f"api_url: {api_url}, app_key: {app_key}, secret_key: {secret_key}")
            # 신규 토큰 발급을 위한 파라미터 생성
            params = {
                "grant_type": "client_credentials",
                "appkey": app_key,
                "secretkey": secret_key
            }
            response = kiwoom_client.fn_auth(data=params, host=api_url, endpoint=constant.AUTH_TOKEN_ENDPOINT)
            try:
                result = response.json()
                logger.info(f"토큰 발급 응답: {result}")
            except Exception as e:
                logger.error(f"토큰 발급 API 응답 파싱 실패: {e}", exc_info=True)
                raise ValueError("토큰 발급 API 응답 파싱 실패: " + str(e))

            if "token" not in result or "expires_dt" not in result:
                logger.error("API 응답에 token 또는 expires_dt가 포함되어 있지 않습니다.")
                raise ValueError("API 응답에 token 또는 expires_dt가 포함되어 있지 않습니다.")

            token_value = result["token"]
            expires_str = result["expires_dt"]

            try:
                expires_dt = datetime.strptime(expires_str, "%Y%m%d%H%M%S").replace(tzinfo=KST)
            except Exception as e:
                logger.error(f"토큰 만료일 포맷 변환 실패: {e}", exc_info=True)
                raise ValueError("토큰 만료일 포맷 변환 실패: " + str(e))
            # 실제 키움 API 연동 코드 필요 (여기서는 예시)
            new_token = token_value
            expire_date = expires_dt  # 실제 만료일로 대체
            row = db.query(KiwoomApiInfo).filter(KiwoomApiInfo.account_no == account_no).first()
            if row:
                update_kiwoom_token(db, row, new_token, expire_date)
                logger.info("토큰 갱신 완료")
                return api_url, new_token
            else:
                logger.error("계정 정보 없음")
                return None, None
        else:
            api_url, valid_token = result
            logger.info(f"유효한 토큰 있음: {api_url}, {valid_token}")
            return api_url, valid_token
    finally:
        db.close()

if __name__ == "__main__":
    get_kiwoom_api_url_and_valid_token() 