FROM --platform=linux/amd64 python:3.12.8-slim

WORKDIR /app

# 시스템 패키지 설치
# 빌드에 필요한 패키지 설치
RUN apt-get update && apt-get install -y g++ pkg-config default-libmysqlclient-dev && rm -rf /var/lib/apt/lists/*

# requirements.txt 복사
COPY requirements.txt .

# pip install 실행
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# init.sql 생성
RUN python setup_db.py

# 포트 노출
EXPOSE 8000

# 실행 명령
CMD ["python", "main.py"]