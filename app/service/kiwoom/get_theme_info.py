from app.service.kiwoom import kiwoom_client, constant, update_kiwoom_token
from app.db.database import SessionLocal
from app.config import os
from datetime import datetime, timezone
from app.db.models.theme_info import ThemeInfo
from sqlalchemy.dialects.postgresql import insert

class ThemeInfoService:
    def __init__(self):
        self.db = SessionLocal()
        self.api_url, self.token = update_kiwoom_token.get_kiwoom_api_url_and_valid_token()

    def get_theme_list(self):
        params = {
            'qry_tp': '0', # 검색구분 0:전체검색, 1:테마검색, 2:종목검색
            'stk_cd': '', # 종목코드 검색하려는 종목코드
            'date_tp': '10', # 날짜구분 n일전 (1일 ~ 99일 날짜입력)
            'thema_nm': '방산', # 테마명 검색하려는 테마명
            'flu_pl_amt_tp': '1', # 등락수익구분 1:상위기간수익률, 2:하위기간수익률, 3:상위등락률, 4:하위등락률
            'stex_tp': '1', # 거래소구분 1:KRX, 2:NXT 3.통합
        }
        response = kiwoom_client.fn_theme_info(token=self.token, data=params, host=self.api_url, api_id=constant.테마그룹별요청)
        if response.headers.get('cont_yn') == 'Y':
            next_key = response.headers.get('next_key')
            while next_key:
                response = kiwoom_client.fn_theme_info(token=self.token, data=params, cont_yn='Y',next_key=next_key, host=self.api_url, api_id=constant.테마그룹별요청)
                print(response.json())
                next_key = response.headers.get('next_key')
        else:
            print(response.json())
        db = self.db
        try:
            if response.status_code == 200:
                data = response.json()
                if data.get('thema_grp'):
                    theme_data_list = []
                    for thema_grp in data['thema_grp']:
                        theme_code = thema_grp.get('thema_grp_cd')
                        theme_name = thema_grp.get('thema_nm')
                        if not theme_code or not theme_name:
                            print(f"theme_code: {theme_code}, theme_name: {theme_name}")
                            continue
                        theme_data_list.append({
                            'theme_code': theme_code,
                            'theme_name': theme_name,
                            'mod_date': datetime.now(timezone.utc)
                        })
                    if theme_data_list:
                        stmt = insert(ThemeInfo).values(theme_data_list)
                        stmt = stmt.on_conflict_do_update(
                            index_elements=['theme_code'],
                            set_={'theme_name': stmt.excluded.theme_name, 'mod_date': stmt.excluded.mod_date}
                        )
                        db.execute(stmt)
                        db.commit()
                else:
                    print("No theme data found")
            else:
                print(f"Error: {response.status_code}")
        finally:
            db.close()
        response2 = kiwoom_client.fn_theme_info(token=self.token, data=params, cont_yn='Y',next_key=response.headers.get('next_key'), host=self.api_url, api_id=constant.테마그룹별요청)
        print(response2.json())
        response3 = kiwoom_client.fn_theme_info(token=self.token, data=params, cont_yn='Y',next_key=response2.headers.get('next_key'), host=self.api_url, api_id=constant.테마그룹별요청)
        print(response3.json())
        response4 = kiwoom_client.fn_theme_info(token=self.token, data=params, cont_yn='Y',next_key=response3.headers.get('next_key'), host=self.api_url, api_id=constant.테마그룹별요청)
        print(response4.json())

    def print_response(response):
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")

if __name__ == "__main__":
    theme_info_service = ThemeInfoService()
    try:
        theme_info_service.get_theme_list()
    except Exception as e:
        print(f"Error: {e}") 