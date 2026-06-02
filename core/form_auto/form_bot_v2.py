import os
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# 1. 크롬 프로세스 정리
os.system("taskkill /f /im chrome.exe /t")
os.system("taskkill /f /im chromedriver.exe /t")
time.sleep(2)

# 2. 크롬 경로
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# ⚠️ 기존 User Data 사용 ❌
# ✅ 디버깅 전용 프로필
debug_profile = r"C:\chrome-debug-profile"

# 3. 디버깅 모드로 크롬 실행
subprocess.Popen([
    chrome_path,
    "--remote-debugging-port=9222",
    f"--user-data-dir={debug_profile}",
    "--no-first-run",
    "--no-default-browser-check"
])

# ⏳ 크롬 + 포트 열릴 때까지 충분히 대기
time.sleep(6)

# 4. Selenium 연결
options = Options()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# 5. 테스트
driver.get("https://www.google.com")
print("✅ 9222 디버깅 크롬 연결 성공")
