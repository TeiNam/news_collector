import requests
import pandas as pd
import datetime
import time
from typing import Dict, List
from modules.mysql_connector import MySQLConnector
from modules.news_repository import NewsRepository
from configs.news_api_setting import (
    NAVER_API_CONFIG,
    SECTIONS,
    EXCLUDE_KEYWORDS,
    API_REQUEST_CONFIG
)


class NaverNewsAPI:
    def __init__(self):
        self.client_id = NAVER_API_CONFIG['client_id']
        self.client_secret = NAVER_API_CONFIG['client_secret']
        self.base_url = NAVER_API_CONFIG['base_url']
        self.headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret
        }

    def clean_title(self, title: str) -> str:
        """HTML 태그와 엔티티를 제거"""
        return title.replace('<b>', '').replace('</b>', '').replace('&quot;', '')

    def search_news(self, query: str, start: int = 1) -> Dict:
        params = {
            "query": query,
            "start": start,
            "display": API_REQUEST_CONFIG['items_per_request'],
            "sort": "date"
        }

        response = requests.get(self.base_url, headers=self.headers, params=params)
        if response.status_code != 200:
            print(f"API Response: {response.text}")
        response.raise_for_status()
        return response.json()

    def collect_all_news(self, query: str) -> List[Dict]:
        news_items = []
        start = 1
        max_items = API_REQUEST_CONFIG['max_items']
        items_per_request = API_REQUEST_CONFIG['items_per_request']
        retry_delay = API_REQUEST_CONFIG['retry_delay']

        while start <= max_items:
            try:
                print(f"Collecting news for query '{query}' starting at {start}")
                result = self.search_news(query, start)
                if 'items' in result and result['items']:
                    news_items.extend(result['items'])
                    print(f"Found {len(result['items'])} items")
                else:
                    print(f"No items found for query '{query}'")
                    break

                if len(result['items']) < items_per_request:
                    break

                start += items_per_request
                time.sleep(1)

            except requests.exceptions.RequestException as e:
                if hasattr(e.response, 'status_code') and e.response.status_code == 429:
                    print(f"Rate limit reached, waiting {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
                else:
                    print(f"Error collecting news at start={start}: {e}")
                    break

        return news_items


def collect_daily_news(date: str = None):
    if date is None:
        date = datetime.datetime.now().strftime('%Y%m%d')

    try:
        api = NaverNewsAPI()
        mysql_conn = MySQLConnector()
        news_repo = NewsRepository(mysql_conn)

        # 마지막 수집 시간을 KST 기준 offset-aware datetime으로 변환
        kst = datetime.timezone(datetime.timedelta(hours=9))
        last_pub_time = datetime.datetime.strptime(f"{date} {news_repo.get_last_pub_time(date)}",
                                                 '%Y%m%d %H:%M:%S').replace(tzinfo=kst)
        print(f"마지막 수집 시간: {last_pub_time}")

        section_results = {}

        for section, keywords in SECTIONS.items():
            print(f"\n{section} 섹션 수집 시작...")
            section_news = []

            for keyword in keywords:
                print(f"- {keyword} 키워드 처리 중...")
                try:
                    query = f"{keyword}"
                    news_items = api.collect_all_news(query)

                    for item in news_items:
                        try:
                            # HTML 태그와 엔티티를 제거한 제목
                            title = api.clean_title(item['title'])

                            exclude = any(ex_keyword.lower() in title.lower()
                                        for ex_keyword in EXCLUDE_KEYWORDS)
                            if exclude:
                                continue

                            # 뉴스 발행 시간 파싱 (이미 timezone 정보 포함)
                            pub_date = datetime.datetime.strptime(item['pubDate'],
                                                               '%a, %d %b %Y %H:%M:%S %z')
                            # KST로 변환
                            pub_date = pub_date.astimezone(kst)
                            news_date = pub_date.strftime('%Y%m%d')

                            # 날짜가 같고 시간이 마지막 수집 시간보다 이후인 경우만 수집
                            if news_date == date and pub_date > last_pub_time:
                                section_news.append({
                                    'title': title,
                                    'link': item['link'],
                                    'section': section,
                                    'keyword': keyword,
                                    'pubDate': item['pubDate']
                                })
                        except Exception as e:
                            print(f"Error processing news item: {str(e)}")
                            continue

                    time.sleep(1)
                except Exception as e:
                    print(f"Error processing keyword '{keyword}': {e}")
                    continue

            df = pd.DataFrame(section_news)
            if not df.empty:
                df = df.drop_duplicates(subset=['title'])
                section_results[section] = df
                print(f"{section} 섹션: {len(df)}개 신규 기사 수집 완료")

                try:
                    news_repo.insert_news(df)
                except Exception as e:
                    print(f"데이터베이스 저장 오류: {e}")
            else:
                print(f"{section} 섹션: 신규 기사 없음")

    finally:
        mysql_conn.close()

    return section_results


if __name__ == "__main__":
    today = datetime.datetime.now().strftime('%Y%m%d')

    print("뉴스 수집 시작...")
    try:
        results = collect_daily_news(today)
        total_articles = sum(len(df) for df in results.values())
        print(f"\n전체 수집 완료: {total_articles}개 기사")
    except Exception as e:
        print(f"\n오류 발생: {e}")