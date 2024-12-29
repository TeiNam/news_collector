# News Collector

## 프로젝트 소개
이 프로젝트는 Naver 뉴스 API를 활용하여 주식 및 금융 관련 뉴스를 자동으로 수집하고 저장하는 시스템입니다. FastAPI를 기반으로 구축되었으며, 정기적인 스케줄링을 통해 최신 뉴스를 수집합니다.

## 주요 기능
- **자동화된 뉴스 수집**: 3시간 간격으로 자동 뉴스 수집 (00:00, 03:00, 06:00, 09:00, 12:00, 15:00, 18:00, 21:00)
- **실시간 뉴스 모니터링**: 주식, 금융 관련 키워드 기반 뉴스 수집
- **데이터 저장**: MySQL 데이터베이스를 활용한 효율적인 데이터 관리
- **RESTful API**: FastAPI 기반의 API 엔드포인트 제공
- **Docker 지원**: 컨테이너화된 환경 구성 지원

## 기술 스택
- **Backend**: Python 3.12.8, FastAPI
- **Database**: MySQL 8.0
- **API**: Naver News Search API
- **Container**: Docker, Docker Compose
- **Libraries**: 
  - pandas (데이터 처리)
  - schedule (작업 스케줄링)
  - uvicorn (ASGI 서버)
  - requests (HTTP 요청)

## 프로젝트 구조
```
news_collector/
├── configs/                 # 설정 파일
│   ├── mysql_setting.py    # MySQL 설정
│   └── news_api_setting.py # Naver API 설정
├── modules/                 # 핵심 모듈
│   ├── mysql_connector.py  # 데이터베이스 연결
│   ├── news_repository.py  # 뉴스 데이터 처리
│   └── scheduler.py        # 스케줄러
├── utils/                   # 유틸리티
│   └── naver_search_api_collector.py # 뉴스 수집기
├── Dockerfile              # Docker 설정
├── docker-compose.yml      # 프로덕션 환경 설정
├── docker-compose.local.yml # 로컬 개발 환경 설정
├── main.py                 # 애플리케이션 엔트리포인트
├── setup_db.py            # 데이터베이스 초기화
└── requirements.txt       # 의존성 패키지
```

## 설치 및 실행 방법

### 환경 설정
1. 프로젝트 클론
```bash
git clone [repository-url]
cd news_collector
```

2. 환경 변수 설정
`.env` 파일을 생성하고 다음 변수들을 설정:
```env
# MySQL 설정
MYSQL_HOST=localhost
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=my_stock
MYSQL_PORT=3306

# Naver API 설정
NAVER_CLIENT_ID=your_naver_client_id
NAVER_CLIENT_SECRET=your_naver_client_secret
```

### Docker를 이용한 실행

1. 로컬 개발 환경 실행
```bash
docker-compose -f docker-compose.local.yml up --build
```

2. 프로덕션 환경 실행
```bash
docker-compose up --build
```

### 수동 설치 및 실행

1. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. 의존성 설치
```bash
pip install -r requirements.txt
```

3. 데이터베이스 초기화
```bash
python setup_db.py
```

4. 애플리케이션 실행
```bash
python main.py
```

## API 엔드포인트
- `GET /`: API 상태 확인
- `POST /collector/run`: 수동으로 뉴스 수집 실행
- `GET /scheduler/status`: 스케줄러 상태 확인

## 모니터링 키워드
현재 다음 키워드들에 대한 뉴스를 수집합니다:
- 코스피 코스닥
- 증권 주식
- 금리정책
- 반도체 SK하이닉스
- 기업공시
- 지분매각
- 외인 기관
- 환률
- S&P

## 데이터베이스 스키마
```sql
CREATE TABLE news (
    news_id BIGINT UNSIGNED auto_increment NOT NULL,
    title varchar(100) NOT NULL,
    link varchar(255) NOT NULL,
    section varchar(20) NOT NULL,
    keyword varchar(30) NOT NULL,
    pub_date DATE NOT NULL,
    pub_time TIME NOT NULL,
    create_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT news_pk PRIMARY KEY (news_id,pub_date)
)
```

## 라이센스
이 프로젝트는 MIT 라이센스 하에 배포됩니다.
