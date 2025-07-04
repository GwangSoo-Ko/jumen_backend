from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models.kiwoom_api_info import KiwoomApiInfo
from app.config import os
from app.service.kiwoom import kiwoom_client, constant
import pytz
KST = pytz.timezone('Asia/Seoul')

def get_valid_token(db: Session, account_no: str):
    now = datetime.now(timezone.utc)
    row = db.query(KiwoomApiInfo).filter(
        KiwoomApiInfo.account_no == account_no,
        KiwoomApiInfo.valid_token.isnot(None),
        KiwoomApiInfo.token_expire_date > now
    ).first()
    if row:
        return row.valid_token
    else:
        return None

def update_kiwoom_token(db: Session, row: KiwoomApiInfo, new_token: str, expire_date: datetime):
    row.valid_token = new_token
    row.token_expire_date = expire_date
    row.mod_date = datetime.now(timezone.utc)
    db.commit()

def get_kiwoom_api_keys(db: Session, account_no: str):
    """
    tb_kiwoom_api_info 테이블에서 해당 account_no의 app_key, secret_key를 반환한다.
    """
    row = db.query(KiwoomApiInfo).filter(KiwoomApiInfo.account_no == account_no).first()
    if row:
        return row.app_key, row.secret_key, row.api_url
    return None, None, None

def get_kiwoom_api_url_and_valid_token():
    account_no = os.getenv("ACCOUNT_NO")
    if not account_no:
        print(".env 파일에 ACCOUNT_NO가 정의되어 있어야 합니다.")
        return
    db = SessionLocal()
    valid_token = get_valid_token(db, account_no)
    if valid_token:
        print(f"유효한 토큰 있음: {valid_token}")
    else:
        app_key, secret_key, api_url = get_kiwoom_api_keys(db, account_no)
        if api_url is None or app_key is None or secret_key is None:
            print("키움 API 정보 없음")
            return
        print(f"api_url: {api_url}, app_key: {app_key}, secret_key: {secret_key}")
        # 신규 토큰 발급을 위한 파라미터 생성
        params = {
            "grant_type": "client_credentials",
            "appkey": app_key,
            "secretkey": secret_key
        }
        response = kiwoom_client.fn_auth(data=params, host=api_url, endpoint=constant.AUTH_TOKEN_ENDPOINT)
        try:
            result = response.json()
            print(result)
        except Exception as e:
            db.close()
            raise ValueError("토큰 발급 API 응답 파싱 실패: " + str(e))

        if "token" not in result or "expires_dt" not in result:
            db.close()
            raise ValueError("API 응답에 token 또는 expires_dt가 포함되어 있지 않습니다.")

        token_value = result["token"]
        expires_str = result["expires_dt"]

        try:
            expires_dt = datetime.strptime(expires_str, "%Y%m%d%H%M%S").replace(tzinfo=KST)
        except Exception as e:
            db.close()
            raise ValueError("토큰 만료일 포맷 변환 실패: " + str(e))
        # 실제 키움 API 연동 코드 필요 (여기서는 예시)
        new_token = token_value
        expire_date = expires_dt  # 실제 만료일로 대체
        row = db.query(KiwoomApiInfo).filter(KiwoomApiInfo.account_no == account_no).first()
        if row:
            update_kiwoom_token(db, row, new_token, expire_date)
            print("토큰 갱신 완료")
        else:
            print("계정 정보 없음")
    db.close()
    return api_url, valid_token

if __name__ == "__main__":
    get_kiwoom_api_url_and_valid_token() 