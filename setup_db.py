from datetime import datetime, timedelta


def generate_init_sql():
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    day_after = today + timedelta(days=2)

    sql = f"""CREATE DATABASE IF NOT EXISTS my_stock;
USE my_stock;

CREATE TABLE IF NOT EXISTS news (
    news_id BIGINT UNSIGNED auto_increment NOT NULL COMMENT 'PK',
    title varchar(100) NOT NULL COMMENT '기사 제목',
    link varchar(255) NOT NULL COMMENT '주소 Url',
    `section` varchar(20) NOT NULL COMMENT '섹션',
    keyword varchar(30) NOT NULL COMMENT '검색 키워드',
    pub_date DATE NOT NULL COMMENT '발행일',
    pub_time TIME NOT NULL COMMENT '발행시간',
    create_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL COMMENT '수집일',
    CONSTRAINT news_pk PRIMARY KEY (news_id,pub_date)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_general_ci
PARTITION BY RANGE (TO_DAYS(pub_date)) (
    PARTITION p{today.strftime('%Y%m%d')} VALUES LESS THAN (TO_DAYS('{tomorrow.strftime('%Y-%m-%d')}')),
    PARTITION p{tomorrow.strftime('%Y%m%d')} VALUES LESS THAN (TO_DAYS('{day_after.strftime('%Y-%m-%d')}')),
    PARTITION p_maxvalue VALUES LESS THAN MAXVALUE
);"""

    with open('init.sql', 'w') as f:
        f.write(sql)


if __name__ == "__main__":
    generate_init_sql()