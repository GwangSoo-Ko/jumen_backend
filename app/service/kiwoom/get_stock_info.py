import logging
from app.service.kiwoom import kiwoom_client, constant, update_kiwoom_token
from app.db.database import SessionLocal
from app.config import os
from datetime import datetime, timezone
from app.db.models.stock_info import StockInfo
from sqlalchemy.dialects.postgresql import insert
from dotenv import load_dotenv

logger = logging.getLogger('app.service.batch')

class StockInfoService:
    def __init__(self):
        self.db = SessionLocal()
        result = update_kiwoom_token.get_kiwoom_api_url_and_valid_token()
        if result is None or result[0] is None or result[1] is None:
            raise ValueError("키움 API URL 또는 토큰을 가져올 수 없습니다. 계정 정보와 API 키를 확인해주세요.")
        self.api_url, self.token = result

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
                # print(data)
                if data['list']:
                    stock_data_list = []
                    for item in data['list']:
                        ticker = item['code']
                        name = item['name']
                        sector = item['upName']
                        
                        size = item['upSizeName']
                        company_class = item['companyClassName']
                        
                        listed_count = int(item['listCount'])
                        listed_date = datetime.strptime(item['regDay'], '%Y%m%d').date()
                        warning_status = item['orderWarning']
                        if warning_status == '0':
                            warning_status = '정상'
                        elif warning_status == '2':
                            warning_status = '정리매매'
                        elif warning_status == '3':
                            warning_status = '단기과열'
                        elif warning_status == '4':
                            warning_status = '투자위험'
                        elif warning_status == '5':
                            warning_status = '투자경고'
                        else:
                            logger.debug(f"ticker: {ticker}, name: {name}, sector: {sector}, size: {size}, company_class: {company_class}, listed_count: {listed_count}, listed_date: {listed_date}, market: {market}, warning_status: {warning_status}")
                            continue
                        if market == '코스피':
                            if sector == '' or company_class == '스팩':
                                logger.debug(f"ticker: {ticker}, name: {name}, sector: {sector}, size: {size}, company_class: {company_class}, listed_count: {listed_count}, listed_date: {listed_date}, market: {market}, warning_status: {warning_status}")
                                continue
                        elif market == '코스닥':
                            if company_class == '스팩':
                                logger.debug(f"ticker: {ticker}, name: {name}, sector: {sector}, size: {size}, company_class: {company_class}, listed_count: {listed_count}, listed_date: {listed_date}, market: {market}, warning_status: {warning_status}")
                                continue
                        stock_data_list.append({
                            'ticker': ticker,
                            'name': name,
                            'sector': sector,
                            'market': market,
                            'listed_date': listed_date,
                            'size': size,
                            'company_class': company_class,
                            'listed_count': listed_count,
                            'warning_status': warning_status,
                            'mod_date': datetime.now(timezone.utc)
                        })
                    if stock_data_list:
                        stmt = insert(StockInfo).values(stock_data_list)
                        update_dict = {
                            'name': stmt.excluded.name,
                            'sector': stmt.excluded.sector,
                            'market': stmt.excluded.market,
                            'listed_date': stmt.excluded.listed_date,
                            'size': stmt.excluded.size,
                            'company_class': stmt.excluded.company_class,
                            'listed_count': stmt.excluded.listed_count,
                            'warning_status': stmt.excluded.warning_status,
                            'mod_date': stmt.excluded.mod_date,
                        }
                        stmt = stmt.on_conflict_do_update(
                            index_elements=['ticker'],
                            set_=update_dict
                        )
                        db.execute(stmt)
                        db.commit()
                else:
                    logger.warning("No data found")
            else:
                logger.error(f"Error: {response.status_code}")
        finally:
            db.close()

    def get_stock_info(self, stock_code: str):
        pass

    def print_response(response):
        """
        API 응답을 출력하는 함수
        :param response: API 응답 객체
        """
        logger.debug(f"Status Code: {response.status_code}")
        logger.debug(f"Response: {response.json()}")

def setup_logging():
    load_dotenv()
    ENV = os.getenv('ENV', 'development')
    # 로그 디렉토리 생성
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # 로그 파일명 설정 (날짜 포함)
    today = datetime.now().strftime('%Y-%m-%d')
    log_filename = f'get_stock_info_{today}.log'
    log_filepath = os.path.join(log_dir, log_filename)
    
    # 로깅 설정 - 파일과 콘솔 모두에 출력
    logger.setLevel(logging.WARNING)
    
    # 기존 핸들러 제거 (중복 방지)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 파일 핸들러 설정
    file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
    file_handler.setLevel(logging.WARNING)
    
    # 포맷터 설정
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 콘솔 핸들러는 production이 아닐 때만 추가
    if ENV != 'production':
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

def main():
    """메인 실행 함수"""
    setup_logging()
    stock_info_service = StockInfoService()
    try:
        stock_info_service.get_stock_list('0')
        stock_info_service.get_stock_list('10')
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    main()