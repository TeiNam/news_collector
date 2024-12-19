# News Collector Project

## 프로젝트 개요
이 프로젝트는 다양한 뉴스 사이트의 기사를 수집하고 분석하는 웹 크롤러입니다.

## 기능
- 주요 뉴스 사이트 기사 수집
- 수집된 데이터 정제 및 저장
- 기사 메타데이터 추출 (제목, 날짜, 작성자, 카테고리 등)

## 기술 스택
- Python 3.12.8
- MySQL (데이터베이스)
- pandas (데이터 처리)


## 설치 방법
1. 저장소 클론
```bash
git clone [repository-url]
cd news_crawler
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

## 사용 방법
1. 설정 파일 구성
   - `config/` 디렉토리의 설정 파일을 수정하여 크롤링 대상 사이트 및 데이터베이스 설정

2. 크롤러 실행
```bash
python src/main.py
```

## .env
```angular2html
# MySQL 설정
MYSQL_HOST=
MYSQL_USER=
MYSQL_PASSWORD=
MYSQL_DATABASE=
MYSQL_PORT=

# Naver API 설정
NAVER_CLIENT_ID=
NAVER_CLIENT_SECRET=
```


## 라이센스
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details