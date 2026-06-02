import os
import sys
import requests

# [규칙 3] 기준 디렉토리 고정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

# 여기에 네 정보를 넣어
TOKEN = "8204355471:AAHSapDO4DNvuVgRD0vxSWFymQcg_4l6mzw"
CHAT_ID = "6046121539"

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=10)

if __name__ == "__main__":
    send_message("🚀 시스템 연결 성공! 24시간 가동 준비 완료.")