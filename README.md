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
- **MySQL**: 데이터베이스
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
mysql-connector-python
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

# DB 마이그레이션
alembic upgrade head

# 개발 서버 실행
uvicorn app.main:app --reload
```

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

---

## 9. 참고 자료

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/ko/)
- [SQLAlchemy 공식 문서](https://docs.sqlalchemy.org/)
- [Pydantic 공식 문서](https://docs.pydantic.dev/)
- [MySQL 공식 문서](https://dev.mysql.com/doc/)

---

문의 및 기여는 이슈/PR로 남겨주세요.
실제 서비스에 맞게 항목을 추가/수정하여 사용하세요! 