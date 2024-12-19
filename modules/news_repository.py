# modules/news_repository.py
from mysql.connector import Error
import pandas as pd
from datetime import datetime


class NewsRepository:
    def __init__(self, connector):
        self.connector = connector

    def get_last_pub_time(self, date: str) -> str:
        """특정 날짜의 마지막 수집 시간 조회"""
        connection = self.connector.get_connection()
        cursor = connection.cursor()

        try:
            query = """
            SELECT MAX(pub_time) 
            FROM news 
            WHERE pub_date = %s
            """
            cursor.execute(query, (date,))
            result = cursor.fetchone()
            return result[0] if result and result[0] else '00:00:00'

        finally:
            cursor.close()

    def insert_news(self, df: pd.DataFrame) -> None:
        """뉴스 데이터 삽입"""
        connection = self.connector.get_connection()
        cursor = connection.cursor()

        try:
            for _, row in df.iterrows():
                pub_datetime = datetime.strptime(row['pubDate'], '%a, %d %b %Y %H:%M:%S %z')
                pub_date = pub_datetime.strftime('%Y-%m-%d')
                pub_time = pub_datetime.strftime('%H:%M:%S')

                query = """
                INSERT INTO news (title, link, section, keyword, pub_date, pub_time)
                VALUES (%s, %s, %s, %s, %s, %s)
                """

                values = (
                    row['title'],
                    row['link'],
                    row['section'],
                    row['keyword'],
                    pub_date,
                    pub_time
                )

                cursor.execute(query, values)

            connection.commit()
            print(f"{len(df)} 개의 뉴스 기사가 데이터베이스에 저장되었습니다.")

        except Error as e:
            print(f"데이터 삽입 오류: {e}")
            connection.rollback()
            raise
        finally:
            cursor.close()

    def get_news_by_date(self, date: str) -> pd.DataFrame:
        """특정 날짜의 뉴스 조회"""
        connection = self.connector.get_connection()
        query = """
        SELECT title, link, section, keyword, pub_date, pub_time
        FROM news
        WHERE pub_date = %s
        """

        try:
            return pd.read_sql(query, connection, params=(date,))
        except Error as e:
            print(f"데이터 조회 오류: {e}")
            raise

    def get_news_by_keyword(self, keyword: str, start_date: str, end_date: str) -> pd.DataFrame:
        """키워드로 뉴스 검색"""
        connection = self.connector.get_connection()
        query = """
        SELECT title, link, section, keyword, pub_date, pub_time
        FROM news
        WHERE keyword LIKE %s
        AND pub_date BETWEEN %s AND %s
        """

        try:
            return pd.read_sql(query, connection, params=(f"%{keyword}%", start_date, end_date))
        except Error as e:
            print(f"데이터 조회 오류: {e}")
            raise

    def get_news_count_by_keyword(self, start_date: str, end_date: str) -> pd.DataFrame:
        """키워드별 뉴스 개수 통계"""
        connection = self.connector.get_connection()
        query = """
        SELECT keyword, COUNT(*) as count
        FROM news
        WHERE pub_date BETWEEN %s AND %s
        GROUP BY keyword
        ORDER BY count DESC
        """

        try:
            return pd.read_sql(query, connection, params=(start_date, end_date))
        except Error as e:
            print(f"데이터 조회 오류: {e}")
            raise