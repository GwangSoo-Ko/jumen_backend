from app.service.kiwoom import kiwoom_client, constant, update_kiwoom_token
from app.db.database import SessionLocal
from app.config import os
from datetime import datetime
from app.db.models.stock_info import StockInfo
from sqlalchemy.dialects.postgresql import insert

class StockInfoService:
    def __init__(self):
        self.db = SessionLocal()
        self.api_url, self.token = update_kiwoom_token.get_kiwoom_api_url_and_valid_token()

    def get_stock_list(self, market_type: str):
        if market_type == '0':
            market = '코스피'
        elif market_type == '10':
            market = '코스닥'
        else:
            raise ValueError(f"Invalid market type: {market_type}")
        params = {
            'mrkt_tp': market_type, # 시장구분 0:코스피,10:코스닥,3:ELW,8:ETF,30:K-OTC,50:코넥스,5:신주인수권,4:뮤추얼펀드,6:리츠,9:하이일드
        }
        response = kiwoom_client.fn_stock_info(token=self.token, data=params, host=self.api_url, api_id=constant.종목정보리스트)
        db = self.db
        try:
            if response.status_code == 200:
                data = response.json()
                print(data)
                # if data['list']:
                #     stock_data_list = []
                #     for item in data['list']:
                #         ticker = item['code']
                #         name = item['name']
                #         sector = item['upName']
                        
                #         size = item['upSizeName']
                #         company_class = item['companyClassName']
                        
                #         listed_count = int(item['listCount'])
                #         listed_date = datetime.strptime(item['regDay'], '%Y%m%d').date()
                #         warning_status = item['orderWarning']
                #         if warning_status == '0':
                #             warning_status = '정상'
                #         elif warning_status == '2':
                #             warning_status = '정리매매'
                #         elif warning_status == '3':
                #             warning_status = '단기과열'
                #         elif warning_status == '4':
                #             warning_status = '투자위험'
                #         elif warning_status == '5':
                #             warning_status = '투자경고'
                #         else:
                #             print(f"ticker: {ticker}, name: {name}, sector: {sector}, size: {size}, company_class: {company_class}, listed_count: {listed_count}, listed_date: {listed_date}, market: {market}, warning_status: {warning_status}")
                #             continue
                #         if market == '코스피':
                #             if sector == '' or company_class == '스팩':
                #                 print(f"ticker: {ticker}, name: {name}, sector: {sector}, size: {size}, company_class: {company_class}, listed_count: {listed_count}, listed_date: {listed_date}, market: {market}, warning_status: {warning_status}")
                #                 continue
                #         elif market == '코스닥':
                #             if company_class == '스팩':
                #                 print(f"ticker: {ticker}, name: {name}, sector: {sector}, size: {size}, company_class: {company_class}, listed_count: {listed_count}, listed_date: {listed_date}, market: {market}, warning_status: {warning_status}")
                #                 continue
                #         stock_data_list.append({
                #             'ticker': ticker,
                #             'name': name,
                #             'sector': sector,
                #             'market': market,
                #             'listed_date': listed_date,
                #             'size': size,
                #             'company_class': company_class,
                #             'listed_count': listed_count,
                #             'warning_status': warning_status
                #         })
                #     if stock_data_list:
                #         stmt = insert(StockInfo).values(stock_data_list)
                #         update_dict = {
                #             'name': stmt.excluded.name,
                #             'sector': stmt.excluded.sector,
                #             'market': stmt.excluded.market,
                #             'listed_date': stmt.excluded.listed_date,
                #             'size': stmt.excluded.size,
                #             'company_class': stmt.excluded.company_class,
                #             'listed_count': stmt.excluded.listed_count,
                #             'warning_status': stmt.excluded.warning_status,
                #         }
                #         stmt = stmt.on_conflict_do_update(
                #             index_elements=['ticker'],
                #             set_=update_dict
                #         )
                #         db.execute(stmt)
                #         db.commit()
                # else:
                #     print("No data found")
            else:
                print(f"Error: {response.status_code}")
        finally:
            db.close()

    def get_stock_info(self, stock_code: str):
        pass

    def print_response(response):
        """
        API 응답을 출력하는 함수
        :param response: API 응답 객체
        """
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")


if __name__ == "__main__":
    stock_info_service = StockInfoService()
    market_type = '10'
    try:
        stock_info_service.get_stock_list(market_type)
    except Exception as e:
        print(f"Error: {e}")