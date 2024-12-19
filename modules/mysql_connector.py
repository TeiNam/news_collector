# modules/mysql_connector.py
import mysql.connector
from mysql.connector import Error
from configs.mysql_setting import MYSQL_CONFIG


class MySQLConnector:
    def __init__(self):
        self.connection = None

    def connect(self):
        """데이터베이스 연결"""
        try:
            self.connection = mysql.connector.connect(**MYSQL_CONFIG)
            print("MySQL 데이터베이스 연결 성공")
        except Error as e:
            print(f"MySQL 연결 오류: {e}")
            raise

    def get_connection(self):
        """현재 연결 반환"""
        if self.connection is None or not self.connection.is_connected():
            self.connect()
        return self.connection

    def close(self):
        """데이터베이스 연결 종료"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL 연결이 종료되었습니다.")