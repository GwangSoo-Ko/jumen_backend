# 📈 Stock Theme Backend

## 1. 프로젝트 개요

국내/해외 주식 종목별 테마 정보와 ohlcv(시가, 고가, 저가, 종가, 거래량) 데이터를 제공하는 RESTful API 백엔드 서비스입니다.

- **주요 사용처**: 웹/모바일 프론트엔드(React, React Native), 데이터 분석, 투자 정보 제공 플랫폼 등

---

## 2. 주요 기능

- 종목(Stock) 목록 및 상세 정보 제공
- 테마(Theme) 목록 및 상세 정보 제공
- 종목별 ohlcv(시가, 고가, 저가, 종가, 거래량) 데이터 제공
- 테마별 종목 목록 제공
- (확장) 데이터 등록/수정/삭제, 인증/권한 관리, 캐싱, API 버전 관리

---

## 3. 시스템 아키텍처 및 폴더 구조

```
stock_theme_backend/
└── app/
    ├── __init__.py
    ├── main.py              # FastAPI 앱 진입점
    ├── models/              # SQLAlchemy 모델 정의
    ├── schemas/             # Pydantic 스키마 정의
    ├── crud/                # DB 접근 함수
    ├── api/                 # 라우터(엔드포인트) 모음
    ├── database.py          # DB 연결/세션 관리
    ├── core/                # 설정, 유틸리티, 보안 등
    └── config.py            # 환경설정
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 4. 기술 스택 및 의존성

- **Python 3.9+**
- **FastAPI**: 웹 프레임워크
- **SQLAlchemy**: ORM
- **Pydantic**: 데이터 검증/직렬화
- **Supabase (PostgreSQL)**: 클라우드 DB
- **Uvicorn**: ASGI 서버
- **Alembic**: DB 마이그레이션
- **python-dotenv**: 환경변수 관리
- **pytest**: 테스트
- **loguru**: 로깅
- **Docker**: 컨테이너화

#### requirements.txt 예시
```
fastapi[standard]==0.113.0
pydantic==2.8.0
sqlalchemy
psycopg2-binary
alembic
python-dotenv
uvicorn
loguru
pytest
```

---

## 5. 데이터베이스 모델 (ERD)

- **Stock**: id, code, name, ...
- **Theme**: id, name, description
- **StockTheme**: id, stock_id, theme_id (다대다 관계)
- **OHLCV**: id, stock_id, date, open, high, low, close, volume

> 실제 ERD는 DB 설계 툴(ERDCloud, dbdiagram.io 등)로 시각화 권장
> 
> **Supabase(PostgreSQL)**를 사용하므로, 모델 설계 및 마이그레이션은 PostgreSQL 호환성을 고려해야 합니다.

---

## 6. API 명세 (예시)

| 메서드 | 엔드포인트                  | 설명                       |
|--------|-----------------------------|----------------------------|
| GET    | `/stocks/`                  | 종목 목록 조회             |
| GET    | `/stocks/{stock_id}`        | 종목 상세 조회             |
| GET    | `/stocks/{stock_id}/ohlcv`  | 종목별 ohlcv 데이터 조회   |
| GET    | `/themes/`                  | 테마 목록 조회             |
| GET    | `/themes/{theme_id}`        | 테마 상세 조회             |
| GET    | `/themes/{theme_id}/stocks` | 테마별 종목 목록 조회      |

- **응답 예시**
```json
{
  "id": 1,
  "code": "005930",
  "name": "삼성전자",
  "themes": [
    {"id": 2, "name": "반도체"}
  ]
}
```
```json
{
  "date": "2024-06-01",
  "open": 80000,
  "high": 82000,
  "low": 79000,
  "close": 81000,
  "volume": 12345678
}
```

---

## 7. 개발 및 배포 가이드

### 7.1. 개발 환경 세팅

```bash
# 가상환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 환경변수 파일(.env) 작성
cp .env.example .env

# DB 마이그레이션 (Supabase/PostgreSQL)
alembic upgrade head

# 개발 서버 실행
uvicorn app.main:app --reload

# frontend 실행
npm run dev
```

- **Supabase 연결**: 
  - Supabase 프로젝트에서 PostgreSQL 연결 정보를 발급받아 .env 파일에 저장합니다.
  - 예시: `DATABASE_URL=postgresql://username:password@host:port/dbname`

### 7.2. Docker 사용 예시

```dockerfile
FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
```

---

## 8. 확장성, 보안, 운영 고려사항

- **인증/권한 관리**: JWT, OAuth2 등 도입 가능
- **CORS 설정**: React/React Native 연동을 위한 허용 도메인 지정
- **API 버전 관리**: `/api/v1/` 등으로 엔드포인트 버전 구분
- **Swagger(OpenAPI) 문서 자동화**: `/docs`에서 확인 가능
- **비동기 처리/캐싱**: 대용량 데이터 대응을 위한 Redis 등 활용
- **로깅/모니터링**: loguru, Sentry, Prometheus 등 연동 가능
- **테스트**: pytest 기반 단위/통합 테스트 작성 권장
- **DB**: Supabase(PostgreSQL) 기반으로 운영, 백업 및 보안 정책 필요

---

## 9. 참고 자료

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/ko/)
- [SQLAlchemy 공식 문서](https://docs.sqlalchemy.org/)
- [Pydantic 공식 문서](https://docs.pydantic.dev/)
- [Supabase 공식 문서](https://supabase.com/docs)
- [PostgreSQL 공식 문서](https://www.postgresql.org/docs/)

---

문의 및 기여는 이슈/PR로 남겨주세요.
실제 서비스에 맞게 항목을 추가/수정하여 사용하세요!

# Jumen 실시간 테마별 시세 반영 전략

## 1. 목표
- 주식 거래 장중(실시간) 테마별 시세 변동을 jumen 웹서비스에 실시간으로 표현

## 2. 전체 아키텍처

```mermaid
graph TD
A[Playwright/크롤러] --주기적 수집--> B[DB]
B --API 제공--> C[FastAPI/Flask]
C --REST/WebSocket--> D[프론트엔드(React/Vue)]
```

## 3. 주요 구성 요소 및 역할

### (1) 크롤러 (Playwright 등)
- 1~5분 단위로 네이버 금융 등에서 테마별 시세를 주기적으로 수집
- Python의 APScheduler, Celery beat, asyncio 등으로 스케줄링
- 수집 데이터는 DB에 저장 (PostgreSQL 등)

### (2) 백엔드 API (FastAPI/Flask)
- REST API: `/api/theme/price?theme=2차전지` 등으로 최신 시세 제공
- WebSocket API: `/ws/theme/price` 등으로 실시간 push
- DB에서 최신 데이터 조회 및 가공

### (3) 프론트엔드 (React/Vue 등)
- REST API 폴링: 1~5초마다 주기적으로 API 호출하여 UI 갱신
- WebSocket: 서버에서 시세 변동 시 실시간 push 받아 UI 즉시 갱신
- 테마별, 종목별 실시간 변동 정보 시각화

## 4. 구현 전략

- 크롤러는 주기적으로 테마별 시세를 수집하여 DB에 저장
- 백엔드는 DB에서 최신 데이터를 읽어 REST 또는 WebSocket으로 제공
- 프론트엔드는 REST 폴링 또는 WebSocket으로 실시간 데이터 반영

## 5. 기술 스택 예시
- 크롤러: Python (Playwright, asyncio, APScheduler)
- DB: PostgreSQL, MySQL 등
- 백엔드: FastAPI, Flask, Django 등
- 프론트엔드: React, Vue, Svelte 등
- 실시간: WebSocket (FastAPI, Django Channels 등)

## 6. 고려사항
- 네이버 등에서 짧은 주기로 크롤링 시 차단될 수 있으니, User-Agent, 딜레이, 프록시 등 고려
- 실시간성이 매우 중요하다면, 증권사 API(유료/제휴) 활용도 고려
- 데이터 적재량이 많아지면, DB 파티셔닝/아카이빙 등도 필요

## 7. 참고
- REST 방식은 구현이 쉽고 안정적이나, 완전한 실시간성은 WebSocket이 더 적합
- jumen의 기술스택/운영환경에 따라 최적화 방안이 달라질 수 있음

---

**구체적 구현 예시, 코드 샘플, 배포 전략 등은 별도 문서로 추가 예정** 