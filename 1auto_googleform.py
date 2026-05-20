import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# 1. 구글 폼 주소
TARGET_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfxhWe2w2Ive8L412Vl5oNTAwGt9GjoH8Zl7SLYO7gktkzxOg/viewform?usp=publish-editor"

# 2. 내 정보 (수정 필요 시 여기서 수정)
MY_DATA = {
    "secret_code": "여기에_비밀코드_입력",
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

# 3. [중요] 이미 켜진 크롬에 연결하는 설정
options = Options()
# 이 줄이 바로 3단계의 핵심입니다!
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

try:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    print("🔗 접속 중...")
    driver.get(TARGET_URL)
    time.sleep(3)

    questions = driver.find_elements(By.CSS_SELECTOR, 'div[role="listitem"]')
    print(f"📋 질문 {len(questions)}개 발견! 작성을 시작합니다.\n")

    for q in questions:
        try:
            title_el = q.find_element(By.CSS_SELECTOR, 'div[role="heading"]')
            q_text = title_el.text.lower()
            
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
                        print(f"   [{title_el.text}] -> ✅ 입력완료")
                        break
        except:
            continue

    print("\n✨ 모든 입력이 완료되었습니다!")

except Exception as e:
    print(f"\n❌ 에러 발생: {e}")
    print("💡 크롬이 9222 포트로 켜져 있는지 확인하세요.")