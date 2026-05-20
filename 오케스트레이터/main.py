import os
import sys
import subprocess

# [규칙 3] 실행 기준 디렉토리 고정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

# [규칙 2] 운영체제 의존 경로 제거
JOBS_DIR = os.path.join(BASE_DIR, "jobs")
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

def run_job(script_name):
    script_path = os.path.join(JOBS_DIR, script_name)
    try:
        # [규칙 1] 전용 파이썬 경로로 실행
        subprocess.run([sys.executable, script_path], check=True)
    except Exception as e:
        # 실패해도 시스템은 죽지 않고 로그를 남김 (가치 축적)
        with open(os.path.join(LOG_DIR, "error.log"), "a", encoding="utf-8") as f:
            f.write(f"[{script_name}] 에러 발생: {str(e)}\n")

if __name__ == "__main__":
    print("--- 자동화 시스템 가동 ---")
    run_job("telegram_bot.py") # 텔레그램 일꾼 호출
    print("--- 모든 작업 종료 ---")