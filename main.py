import requests
import datetime
import os
import time
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

NOTION_API_KEY = os.getenv('NOTION_API_KEY')
DATABASE_ID = os.getenv('DATABASE_ID')
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def get_updated_pages():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    response = requests.post(url, headers=HEADERS)
    data = response.json()

    updated_pages = []
    now = datetime.datetime.utcnow()
    for result in data.get('results', []):
        edited_time = datetime.datetime.fromisoformat(result['last_edited_time'].replace("Z", "+00:00"))
        if (now - edited_time).total_seconds() < 300:
            updated_pages.append(result)
    return updated_pages

def send_slack_message(message):
    payload = {"text": message}
    requests.post(SLACK_WEBHOOK_URL, json=payload)

def monitor():
    print("🚀 Notion 모니터링 시작됨...")
    while True:
        try:
            updated = get_updated_pages()
            if updated:
                for page in updated:
                    props = page['properties']
                    항목 = props.get('항목', {}).get('rich_text', [{}])[0].get('text', {}).get('content', '없음')
                    표현 = props.get('표현', {}).get('rich_text', [{}])[0].get('text', {}).get('content', '없음')
                    설명 = props.get('설명', {}).get('rich_text', [{}])[0].get('text', {}).get('content', '없음')
                    edited_time = page['last_edited_time'][:19].replace('T', ' ')
                    page_url = page.get('url', '링크 없음')

                    message = f"""🔔 [Notion 업데이트 감지]

# 항목 : {항목}
# 표현 : {표현}
# 설명 : {설명}
🕒 수정 시각 : {edited_time}
🔗 페이지 링크 : {page_url}
"""
                    send_slack_message(message)
            else:
                print("No update.")
        except Exception as e:
            print("❌ 오류 발생:", e)
        time.sleep(300)

if __name__ == "__main__":
    monitor()
