import asyncio
import logging
from playwright.async_api import async_playwright
import pandas as pd
from app.db.database import SessionLocal
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime, timezone
from app.db.models.stock_info import StockInfo
from app.db.models.sector_info import SectorInfo
from app.db.models.stock_sector_relation import StockSectorRelation

logger = logging.getLogger('app.service.batch')

NAVER_SECTOR_URL = "https://finance.naver.com/sise/sise_group.naver?type=upjong"

async def fetch_sector_table(page):
    rows = await page.locator('table.type_1 > tbody > tr').all()
    logger.debug(f"  row 개수: {len(rows)}")
    sector_data = []
    for idx, row in enumerate(rows):
        try:
            tds = await row.locator('td').all()
            if len(tds) < 2:
                continue  # 데이터 row가 아님
            a_count = await tds[0].locator('a').count()
            if a_count == 0:
                continue  # 테마명이 없는 row
            sector_name = await tds[0].locator('a').inner_text()
            sector_link = await tds[0].locator('a').get_attribute('href')
            change_rate = await tds[1].inner_text()
            up_ticker_count = await tds[3].inner_text()
            neutral_ticker_count = await tds[4].inner_text()
            down_ticker_count = await tds[5].inner_text()
            if sector_link:
                sector_link = f"https://finance.naver.com{sector_link}"
            sector_data.append({
                '업종명': sector_name.strip(),
                '전일대비': change_rate.strip(),
                '상승종목수': up_ticker_count.strip(),
                '보합종목수': neutral_ticker_count.strip(),
                '하락종목수': down_ticker_count.strip(),
                '상세링크': sector_link
            })
            if (idx + 1) % 10 == 0:
                logger.debug(f"    {idx + 1}개 row 파싱 완료")
        except Exception as e:
            logger.error(f"    row {idx} 파싱 오류: {e}")
            continue
    logger.debug(f"  크롤링 완료, 총 {len(sector_data)}개")
    return sector_data

async def fetch_sector_table_all():
    logger.debug("브라우저 실행 및 업종 페이지 접속 중...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(NAVER_SECTOR_URL)
        logger.debug("업종 페이지 접속 완료, 데이터 크롤링 중...")
        sector_data = await fetch_sector_table(page)
        await browser.close()
    logger.debug(f"전체 크롤링 완료, 총 {len(sector_data)}개")
    return sector_data

def validate_sector_data(sector_data):
    """데이터 유효성 검증 및 결측치 처리"""
    df = pd.DataFrame(sector_data)
    # 등락률이 숫자가 아닌 경우 결측치 처리 (마이너스는 유지, 플러스만 제거)
    df['전일대비'] = pd.to_numeric(df['전일대비'].str.replace('%','').str.replace('+','').str.strip(), errors='coerce') / 100
    df['상승종목수'] = pd.to_numeric(df['상승종목수'].str.replace(',','').str.strip(), errors='coerce')
    df['보합종목수'] = pd.to_numeric(df['보합종목수'].str.replace(',','').str.strip(), errors='coerce')
    df['하락종목수'] = pd.to_numeric(df['하락종목수'].str.replace(',','').str.strip(), errors='coerce')
    df = df.dropna(subset=['업종명', '전일대비'])
    return df

def validate_stock_data(stock_data):
    """종목 데이터 유효성 검증 및 결측치 처리"""
    df = pd.DataFrame(stock_data)
    df['현재가'] = pd.to_numeric(df['현재가'].str.replace(',','').str.strip(), errors='coerce')
    df['전일대비'] = pd.to_numeric(df['전일대비'].str.replace(',','').str.strip(), errors='coerce')
    df['등락률'] = pd.to_numeric(df['등락률'].str.replace('%','').str.replace('+','').str.strip(), errors='coerce') / 100
    df['거래량'] = pd.to_numeric(df['거래량'].str.replace(',','').str.strip(), errors='coerce')
    df['거래대금'] = pd.to_numeric(df['거래대금'].str.replace(',','').str.strip(), errors='coerce')
    df['전일거래량'] = pd.to_numeric(df['전일거래량'].str.replace(',','').str.strip(), errors='coerce')
    return df

async def fetch_all_sector_stocks(sector_df):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        all_stock_data = []
        for idx, row in sector_df.iterrows():
            sector_name = row['업종명']
            sector_url = row['상세링크']
            sector_code = None
            if row['상세링크'] and 'no=' in row['상세링크']:
                sector_code = row['상세링크'].split('no=')[-1]
            if sector_name == '기타':
                continue  # 기타 업종은 제외
            logger.debug(f"{sector_name} 종목 크롤링 중...")
            await page.goto(sector_url)
            table1 = await page.locator('table.type_1 > tbody > tr').all()
            for r in table1:
                tds = await r.locator('td').all()
                if len(tds) < 2:
                    continue
                a_count = await tds[0].locator('a').count()
                if a_count == 0:
                    continue
            table5 = await page.locator('table.type_5 > tbody > tr').all()
            for r in table5:
                tds = await r.locator('td').all()
                if len(tds) < 2:
                    continue
                a_count = await tds[0].locator('a').count()
                if a_count == 0:
                    continue
                stock_name = await tds[0].locator('a').inner_text()
                stock_link = await tds[0].locator('a').get_attribute('href')
                current_price = await tds[1].inner_text()
                diff_price = await tds[2].evaluate("""
                    (node) => {
                        // <em> 태그를 모두 제거
                        node.querySelectorAll('em').forEach(em => em.remove());
                        return node.innerText;
                    }
                """)
                change_rate = await tds[3].inner_text()
                volume = await tds[6].inner_text()
                trading_value = await tds[7].inner_text()
                volume_yesterday = await tds[8].inner_text()
                ticker = None
                if stock_link and 'code=' in stock_link:
                    ticker = stock_link.split('code=')[-1]
                all_stock_data.append({
                    '업종코드': sector_code,
                    '업종명': sector_name,
                    '종목명': stock_name.strip(),
                    '티커': ticker,
                    '현재가': current_price,
                    '전일대비': diff_price,
                    '등락률': change_rate,
                    '거래량': volume,
                    '거래대금': trading_value,
                    '전일거래량': volume_yesterday
                })
        await browser.close()
    return pd.DataFrame(all_stock_data)

class SectorInfoService:
    def __init__(self):
        self.db = SessionLocal()

    def upsert_sector_info(self, df):
        """크롤링된 업종 DataFrame을 tb_sector_info 테이블에 upsert"""
        sector_data_list = []
        for _, row in df.iterrows():
            # sector_code는 상세링크에서 추출 (예: ...no=579)
            sector_code = None
            if row['상세링크'] and 'no=' in row['상세링크']:
                sector_code = row['상세링크'].split('no=')[-1]
            sector_data_list.append({
                'sector_code': sector_code,
                'sector_name': row['업종명'],
                'change_rate': row['전일대비'],
                'up_ticker_count': int(row['상승종목수']),
                'neutral_ticker_count': int(row['보합종목수']),
                'down_ticker_count': int(row['하락종목수']),
                'detail_url': row['상세링크'],
                'ref': '네이버',
                'mod_date': datetime.now(timezone.utc)
            })
        try:
            if sector_data_list:
                from app.db.models.sector_info import SectorInfo
                stmt = insert(SectorInfo).values(sector_data_list)
                update_dict = {
                    'sector_name': stmt.excluded.sector_name,
                    'change_rate': stmt.excluded.change_rate,
                    'up_ticker_count': stmt.excluded.up_ticker_count,
                    'neutral_ticker_count': stmt.excluded.neutral_ticker_count,
                    'down_ticker_count': stmt.excluded.down_ticker_count,
                    'detail_url': stmt.excluded.detail_url,
                    'ref': stmt.excluded.ref,
                    'mod_date': stmt.excluded.mod_date
                }
                stmt = stmt.on_conflict_do_update(
                    index_elements=['sector_code', 'sector_name', 'ref'],
                    set_=update_dict
                )
                self.db.execute(stmt)
                self.db.commit()
                logger.info(f"tb_sector_info 테이블에 {len(sector_data_list)}건 upsert 완료")
            else:
                logger.warning("업데이트할 업종 데이터가 없습니다.")
        except Exception as e:
            logger.error(f"DB upsert 오류: {e}")
            self.db.rollback()
        finally:
            self.db.close()

    def upsert_stock_sector_relation(self, stock_df):
        db = SessionLocal()
        try:
            # DB에서 필요한 id 매핑 정보 미리 조회
            stock_map = dict(db.query(StockInfo.ticker, StockInfo.id).all())
            sector_map = dict(db.query(SectorInfo.sector_code, SectorInfo.id).filter(SectorInfo.ref == '네이버').all())
            relation_data = []
            for _, row in stock_df.iterrows():
                sector_code = row['업종코드']
                ticker = row['티커']

                stock_id = stock_map.get(ticker)
                sector_id = sector_map.get(sector_code)
                if stock_id and sector_id:
                    relation_data.append({
                        'stock_id': stock_id,
                        'sector_id': sector_id,
                        'current_price': row['현재가'],
                        'diff_price': row['전일대비'],
                        'change_rate': row['등락률'],
                        'volume': row['거래량'],
                        'trading_value': row['거래대금'],
                        'volume_yesterday': row['전일거래량'],
                        'mod_date': datetime.now(timezone.utc)
                    })
            if relation_data:
                stmt = insert(StockSectorRelation).values(relation_data)
                update_dict = {
                    'current_price': stmt.excluded.current_price,
                    'diff_price': stmt.excluded.diff_price,
                    'change_rate': stmt.excluded.change_rate,
                    'volume': stmt.excluded.volume,
                    'trading_value': stmt.excluded.trading_value,
                    'volume_yesterday': stmt.excluded.volume_yesterday,
                    'mod_date': stmt.excluded.mod_date
                }
                stmt = stmt.on_conflict_do_update(
                    index_elements=['stock_id', 'sector_id'],
                    set_=update_dict
                )
                db.execute(stmt)
                db.commit()
                logger.info(f"tb_relation_stock_sector 테이블에 {len(relation_data)}건 upsert 완료")
            else:
                logger.warning("업데이트할 관계 데이터가 없습니다.")
        except Exception as e:
            logger.error(f"DB upsert 오류: {e}")
            db.rollback()
        finally:
            db.close()

    def upsert_sector_description(self, sector_description_df):
        from app.db.models.sector_info import SectorInfo
        db = SessionLocal()
        try:
            # 업종코드 → sector_id 매핑
            sector_map = dict(db.query(SectorInfo.sector_code, SectorInfo.id).filter(SectorInfo.ref == '네이버').all())
            for _, row in sector_description_df.iterrows():
                sector_code = row['업종코드']
                description = row['설명']
                sector_id = sector_map.get(sector_code)
                if sector_id and description:
                    db.query(SectorInfo).filter(SectorInfo.id == sector_id).update({
                        'description': description,
                        'mod_date': datetime.now(timezone.utc)
                    })
            db.commit()
            logger.info(f"tb_sector_info 테이블에 {len(sector_description_df)}건 description 업데이트 완료")
        except Exception as e:
            logger.error(f"DB description update 오류: {e}")
            db.rollback()
        finally:
            db.close()

async def main():
    # 섹터 크롤링
    sector_data = await fetch_sector_table_all()
    df = validate_sector_data(sector_data)
    # DB upsert
    sector_info_service = SectorInfoService()
    sector_info_service.upsert_sector_info(df)
    # 섹터별 종목 크롤링
    stock_df = await fetch_all_sector_stocks(df)
    stock_df = validate_stock_data(stock_df)
    sector_info_service.upsert_stock_sector_relation(stock_df)

if __name__ == "__main__":
    asyncio.run(main()) 