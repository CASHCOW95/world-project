import time
import os

# 1. 필수 라이브러리 임포트
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    print("❌ 오류: 필수 라이브러리가 설치되지 않았습니다.")
    print("터미널에 다음 명령어를 입력해 설치하세요: python -m pip install selenium webdriver-manager")
    input("엔터를 누르면 종료합니다...")
    exit()

# =================================================================
# 👇 [입력란] 구글 폼 주소
# =================================================================
TARGET_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfxhWe2w2Ive8L412Vl5oNTAwGt9GjoH8Zl7SLYO7gktkzxOg/viewform?usp=publish-editor"

# =================================================================
# 👇 [내 정보] 
# =================================================================
MY_DATA = {
    "secret_code": "여기에_비밀코드_입력",      # 비밀코드는 그때그때 수정
    "twitter": "@cafri079",                 
    "telegram": "@cafri079",
    "youtube": "카프리썬",                    
    "phone": "010-2479-6866",               
    "wallet": "0x1263901652a09af1975683ff2ce9bcd7f4d0c593" 
}

# 키워드 매칭 리스트
KEYWORD_MAPPING = {
    "비밀코드": MY_DATA["secret_code"], "code": MY_DATA["secret_code"],
    "트위터": MY_DATA["twitter"], "twitter": MY_DATA["twitter"],
    "텔레그램": MY_DATA["telegram"], "telegram": MY_DATA["telegram"],
    "유튜브": MY_DATA["youtube"], "youtube": MY_DATA["youtube"],
    "evm": MY_DATA["wallet"], "지갑": MY_DATA["wallet"], "wallet": MY_DATA["wallet"],
    "휴대전화": MY_DATA["phone"], "전화": MY_DATA["phone"]
}

# =================================================================
# 2. 브라우저 설정 (로그인 정보 불러오기 반영)
# =================================================================
print("🚀 크롬 브라우저를 실행합니다...")
options = webdriver.ChromeOptions()

# [중요] 내 크롬 로그인 정보를 그대로 가져오는 설정
# 윈도우 계정명(ydh24)과 프로필 번호(Profile 22)가 반영되었습니다.
user_data_path = r"C:\Users\ydh24\AppData\Local\Google\Chrome\User Data"
options.add_argument(f"--user-data-dir={user_data_path}")
options.add_argument("--profile-directory=Profile 22")

# 자동화 감지 피하기 및 창 유지 설정
options.add_experimental_option("detach", True) 
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

# 드라이버 설치 및 실행
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

def auto_fill():
    try:
        print(f"🔗 접속 중: {TARGET_URL}")
        driver.get(TARGET_URL)
        time.sleep(3) # 페이지 로딩 대기

        questions = driver.find_elements(By.CSS_SELECTOR, 'div[role="listitem"]')
        print(f"📋 질문 {len(questions)}개 발견! 작성을 시작합니다.\n")

        for i, q in enumerate(questions):
            try:
                title_el = q.find_element(By.CSS_SELECTOR, 'div[role="heading"]')
                q_text = title_el.text.lower()
                
                filled = False
                for keyword, value in KEYWORD_MAPPING.items():
                    if keyword in q_text:
                        input_fields = q.find_elements(By.TAG_NAME, "input")
                        if not input_fields:
                            input_fields = q.find_elements(By.TAG_NAME, "textarea")
                        
                        if input_fields:
                            target_field = input_fields[0]
                            target_field.click()
                            target_field.clear()
                            target_field.send_keys(value)
                            print(f"   [{title_el.text}] -> ✅ '{value}' 입력완료")
                            filled = True
                            break 
                
                if not filled:
                    print(f"   [{title_el.text}] -> ⚠️ 패스 (키워드 매칭 안됨)")
            except Exception as e:
                print(f"   ❌ 질문 처리 중 에러: {e}")

    except Exception as e:
        print(f"❌ 접속 중 에러 발생: {e}")

# 함수 실행
auto_fill()

print("\n✨ 작업이 완료되었습니다.")
print("브라우저를 닫으려면 터미널에서 엔터 키를 누르세요.")
input() 
driver.quit()