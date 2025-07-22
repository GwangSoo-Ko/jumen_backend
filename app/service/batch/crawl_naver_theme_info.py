import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from app.db.database import SessionLocal
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime, timezone
from app.db.models.stock_info import StockInfo
from app.db.models.theme_info import ThemeInfo
from app.db.models.stock_theme_relation import StockThemeRelation

NAVER_THEME_URL = "https://finance.naver.com/sise/theme.naver"

async def get_last_page_num(page):
    # 페이지 하단의 페이징 링크에서 마지막 페이지 번호 추출
    page_links = await page.locator('table.Nnavi a').all()
    page_nums = []
    for link in page_links:
        text = await link.inner_text()
        if text.isdigit():
            page_nums.append(int(text))
    return max(page_nums) if page_nums else 1

async def fetch_theme_table(page):
    rows = await page.locator('table.type_1 > tbody > tr').all()
    print(f"  row 개수: {len(rows)}")
    theme_data = []
    for idx, row in enumerate(rows):
        try:
            tds = await row.locator('td').all()
            if len(tds) < 2:
                continue  # 데이터 row가 아님
            a_count = await tds[0].locator('a').count()
            if a_count == 0:
                continue  # 테마명이 없는 row
            theme_name = await tds[0].locator('a').inner_text()
            theme_link = await tds[0].locator('a').get_attribute('href')
            change_rate = await tds[1].inner_text()
            change_rate_3days = await tds[2].inner_text()
            up_ticker_count = await tds[3].inner_text()
            neutral_ticker_count = await tds[4].inner_text()
            down_ticker_count = await tds[5].inner_text()
            if theme_link:
                theme_link = f"https://finance.naver.com{theme_link}"
            theme_data.append({
                '테마명': theme_name.strip(),
                '전일대비': change_rate.strip(),
                '최근3일등락률(평균)': change_rate_3days.strip(),
                '상승종목수': up_ticker_count.strip(),
                '보합종목수': neutral_ticker_count.strip(),
                '하락종목수': down_ticker_count.strip(),
                '상세링크': theme_link
            })
            if (idx + 1) % 10 == 0:
                print(f"    {idx + 1}개 row 파싱 완료")
        except Exception as e:
            print(f"    row {idx} 파싱 오류: {e}")
            continue
    print(f"  크롤링 완료, 총 {len(theme_data)}개")
    return theme_data

async def fetch_theme_table_all_pages():
    print("브라우저 실행 및 첫 페이지 접속 중...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(NAVER_THEME_URL)
        print("첫 페이지 접속 완료")
        last_page = await get_last_page_num(page)
        print(f"총 {last_page}페이지 탐색 예정")
        all_theme_data = []
        for page_num in range(1, last_page + 1):
            url = f"{NAVER_THEME_URL}?&page={page_num}"
            await page.goto(url)
            print(f"{page_num}페이지 크롤링 중...")
            theme_data = await fetch_theme_table(page)
            all_theme_data.extend(theme_data)
        await browser.close()
    print(f"전체 크롤링 완료, 총 {len(all_theme_data)}개")
    return all_theme_data

def validate_theme_data(theme_data):
    """데이터 유효성 검증 및 결측치 처리"""
    df = pd.DataFrame(theme_data)
    # 등락률이 숫자가 아닌 경우 결측치 처리 (마이너스는 유지, 플러스만 제거)
    df['전일대비'] = pd.to_numeric(df['전일대비'].str.replace('%','').str.replace('+','').str.strip(), errors='coerce') / 100
    df['최근3일등락률(평균)'] = pd.to_numeric(df['최근3일등락률(평균)'].str.replace('%','').str.replace('+','').str.strip(), errors='coerce') / 100
    df['상승종목수'] = pd.to_numeric(df['상승종목수'].str.replace(',','').str.strip(), errors='coerce')
    df['보합종목수'] = pd.to_numeric(df['보합종목수'].str.replace(',','').str.strip(), errors='coerce')
    df['하락종목수'] = pd.to_numeric(df['하락종목수'].str.replace(',','').str.strip(), errors='coerce')
    df = df.dropna(subset=['테마명', '전일대비', '최근3일등락률(평균)'])
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

async def fetch_all_theme_stocks(theme_df):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        all_theme_description = []
        all_stock_data = []
        for idx, row in theme_df.iterrows():
            theme_name = row['테마명']
            theme_url = row['상세링크']
            theme_code = None
            if row['상세링크'] and 'no=' in row['상세링크']:
                theme_code = row['상세링크'].split('no=')[-1]
            print(f"{theme_name} 종목 크롤링 중...")
            await page.goto(theme_url)
            table1 = await page.locator('table.type_1 > tbody > tr').all()
            for r in table1:
                tds = await r.locator('td').all()
                if len(tds) < 2:
                    continue
                a_count = await tds[0].locator('a').count()
                if a_count == 0:
                    continue
                theme_description = await tds[0].locator('div.info_layer_wrap').locator('p').inner_text()
                all_theme_description.append({
                    '테마코드': theme_code,
                    '설명': theme_description
                })
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
                description = await tds[1].locator('div.info_layer_wrap').locator('p').inner_text()
                current_price = await tds[2].inner_text()
                diff_price = await tds[3].evaluate("""
                    (node) => {
                        // <em> 태그를 모두 제거
                        node.querySelectorAll('em').forEach(em => em.remove());
                        return node.innerText;
                    }
                """)
                change_rate = await tds[4].inner_text()
                volume = await tds[5].inner_text()
                trading_value = await tds[6].inner_text()
                volume_yesterday = await tds[7].inner_text()
                ticker = None
                if stock_link and 'code=' in stock_link:
                    ticker = stock_link.split('code=')[-1]
                all_stock_data.append({
                    '테마코드': theme_code,
                    '테마명': theme_name,
                    '종목명': stock_name.strip(),
                    '티커': ticker,
                    '설명': description,
                    '현재가': current_price,
                    '전일대비': diff_price,
                    '등락률': change_rate,
                    '거래량': volume,
                    '거래대금': trading_value,
                    '전일거래량': volume_yesterday
                })
        await browser.close()
    return pd.DataFrame(all_stock_data), pd.DataFrame(all_theme_description)

class ThemeInfoService:
    def __init__(self):
        self.db = SessionLocal()

    def upsert_theme_info(self, df):
        """크롤링된 테마 DataFrame을 tb_theme_info 테이블에 upsert"""
        theme_data_list = []
        for _, row in df.iterrows():
            # theme_code는 상세링크에서 추출 (예: ...no=579)
            theme_code = None
            if row['상세링크'] and 'no=' in row['상세링크']:
                theme_code = row['상세링크'].split('no=')[-1]
            if theme_code == '284':
                continue  # 스팩주 테마는 제외
            theme_data_list.append({
                'theme_code': theme_code,
                'theme_name': row['테마명'],
                'change_rate': row['전일대비'],
                'avg_change_rate_3days': row['최근3일등락률(평균)'],
                'up_ticker_count': int(row['상승종목수']),
                'neutral_ticker_count': int(row['보합종목수']),
                'down_ticker_count': int(row['하락종목수']),
                'detail_url': row['상세링크'],
                'ref': '네이버',
                'mod_date': datetime.now(timezone.utc)
            })
        try:
            if theme_data_list:
                from app.db.models.theme_info import ThemeInfo
                stmt = insert(ThemeInfo).values(theme_data_list)
                update_dict = {
                    'theme_name': stmt.excluded.theme_name,
                    'change_rate': stmt.excluded.change_rate,
                    'avg_change_rate_3days': stmt.excluded.avg_change_rate_3days,
                    'up_ticker_count': stmt.excluded.up_ticker_count,
                    'neutral_ticker_count': stmt.excluded.neutral_ticker_count,
                    'down_ticker_count': stmt.excluded.down_ticker_count,
                    'detail_url': stmt.excluded.detail_url,
                    'ref': stmt.excluded.ref,
                    'mod_date': stmt.excluded.mod_date
                }
                stmt = stmt.on_conflict_do_update(
                    index_elements=['theme_code', 'theme_name', 'ref'],
                    set_=update_dict
                )
                self.db.execute(stmt)
                self.db.commit()
                print(f"tb_theme_info 테이블에 {len(theme_data_list)}건 upsert 완료")
            else:
                print("업데이트할 테마 데이터가 없습니다.")
        except Exception as e:
            print(f"DB upsert 오류: {e}")
            self.db.rollback()
        finally:
            self.db.close()

    def upsert_stock_theme_relation(self, stock_df):
        db = SessionLocal()
        try:
            # DB에서 필요한 id 매핑 정보 미리 조회
            stock_map = dict(db.query(StockInfo.ticker, StockInfo.id).all())
            theme_map = dict(db.query(ThemeInfo.theme_code, ThemeInfo.id).filter(ThemeInfo.ref == '네이버').all())
            relation_data = []
            for _, row in stock_df.iterrows():
                theme_code = row['테마코드']
                ticker = row['티커']
                
                stock_id = stock_map.get(ticker)
                theme_id = theme_map.get(theme_code)
                if stock_id and theme_id:
                    relation_data.append({
                        'stock_id': stock_id,
                        'theme_id': theme_id,
                        'current_price': row['현재가'],
                        'diff_price': row['전일대비'],
                        'change_rate': row['등락률'],
                        'volume': row['거래량'],
                        'trading_value': row['거래대금'],
                        'volume_yesterday': row['전일거래량'],
                        'description': row['설명'],
                        'mod_date': datetime.now(timezone.utc)
                    })
            if relation_data:
                stmt = insert(StockThemeRelation).values(relation_data)
                update_dict = {
                    'current_price': stmt.excluded.current_price,
                    'diff_price': stmt.excluded.diff_price,
                    'change_rate': stmt.excluded.change_rate,
                    'volume': stmt.excluded.volume,
                    'trading_value': stmt.excluded.trading_value,
                    'volume_yesterday': stmt.excluded.volume_yesterday,
                    'description': stmt.excluded.description,
                    'mod_date': stmt.excluded.mod_date
                }
                stmt = stmt.on_conflict_do_update(
                    index_elements=['stock_id', 'theme_id'],
                    set_=update_dict
                )
                db.execute(stmt)
                db.commit()
                print(f"tb_relation_stock_theme 테이블에 {len(relation_data)}건 upsert 완료")
            else:
                print("업데이트할 관계 데이터가 없습니다.")
        except Exception as e:
            print(f"DB upsert 오류: {e}")
            db.rollback()
        finally:
            db.close()

    def upsert_theme_description(self, theme_description_df):
        from app.db.models.theme_info import ThemeInfo
        db = SessionLocal()
        try:
            # 테마코드 → theme_id 매핑
            theme_map = dict(db.query(ThemeInfo.theme_code, ThemeInfo.id).filter(ThemeInfo.ref == '네이버').all())
            for _, row in theme_description_df.iterrows():
                theme_code = row['테마코드']
                description = row['설명']
                theme_id = theme_map.get(theme_code)
                if theme_id and description:
                    db.query(ThemeInfo).filter(ThemeInfo.id == theme_id).update({
                        'description': description,
                        'mod_date': datetime.now(timezone.utc)
                    })
            db.commit()
            print(f"tb_theme_info 테이블에 {len(theme_description_df)}건 description 업데이트 완료")
        except Exception as e:
            print(f"DB description update 오류: {e}")
            db.rollback()
        finally:
            db.close()

async def main():
    # 테마 크롤링
    theme_data = await fetch_theme_table_all_pages()
    df = validate_theme_data(theme_data)
    # DB upsert
    theme_info_service = ThemeInfoService()
    theme_info_service.upsert_theme_info(df)
    # 테마별 종목 크롤링
    stock_df, theme_description_df = await fetch_all_theme_stocks(df)
    stock_df = validate_stock_data(stock_df)
    theme_info_service.upsert_stock_theme_relation(stock_df)
    theme_info_service.upsert_theme_description(theme_description_df)
    
if __name__ == "__main__":
    asyncio.run(main()) 