from selenium import webdriver


# ==========================================
# 1. 사용자 정보 (요청하신 내용 반영 완료)
# ==========================================
MY_DATA = {
    "secret_code": "여기에_비밀코드_입력",      # 매번 바뀌는 코드는 여기서 수정
    
    "twitter": "@cafri079",                 # 트위터 & 텔레그램 동일
    "telegram": "@cafri079",
    "youtube": "카프리썬",
    "phone": "010-2479-6866",
    
    "wallet": "0x1263901652a09af1975683ff2ce9bcd7f4d0c593"          # ⚠️ 지갑 주소는 여기에 넣어주세요!
}

# ==========================================
# 2. 구글 폼 주소 (ethgas AMA Reward)
# ==========================================
TARGET_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfxhWe2w2Ive8L412Vl5oNTAwGt9GjoH8Zl7SLYO7gktkzxOg/viewform?usp=header"

# ==========================================
# 3. 키워드 매칭 설정
# ==========================================
KEYWORD_MAPPING = {
    # 왼쪽(질문 키워드) : 오른쪽(입력할 데이터)
    "비밀코드": MY_DATA["secret_code"],
    
    "트위터": MY_DATA["twitter"],
    "twitter": MY_DATA["twitter"],
    
    "텔레그램": MY_DATA["telegram"],
    "telegram": MY_DATA["telegram"],
    
    "유튜브": MY_DATA["youtube"],
    "youtube": MY_DATA["youtube"],
    
    "evm": MY_DATA["wallet"],      # '혹시모를 EVM 주소'
    "지갑": MY_DATA["wallet"],
    "wallet": MY_DATA["wallet"],
    
    "휴대전화": MY_DATA["phone"],
    "전화": MY_DATA["phone"]
}

# 브라우저 실행 옵션
options = webdriver.ChromeOptions()
# options.add_argument("--headless") # 창 없이 실행하려면 주석 해제
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def auto_fill():
    print("🚀 브라우저를 실행합니다...")
    driver.get(TARGET_URL)
    time.sleep(3) 

    questions = driver.find_elements(By.CSS_SELECTOR, 'div[role="listitem"]')
    print(f"📋 총 {len(questions)}개의 질문을 발견했습니다.")

    for i, q in enumerate(questions):
        try:
            # 질문 제목 가져오기
            title_element = q.find_element(By.CSS_SELECTOR, 'div[role="heading"]')
            q_text = title_element.text.lower()
            
            print(f"[{i+1}번 질문] {title_element.text}")

            filled = False
            for keyword, value in KEYWORD_MAPPING.items():
                if keyword in q_text:
                    input_field = q.find_element(By.TAG_NAME, "input")
                    input_field.click()
                    input_field.clear()
                    input_field.send_keys(value)
                    
                    print(f"   ㄴ ✅ 입력 완료: {value}")
                    filled = True
                    break 
            
            if not filled:
                print("   ㄴ ⚠️ 매칭되는 키워드 없음 (패스)")

        except Exception as e:
            print(f"   ㄴ ❌ 에러: {e}")

# 실행
auto_fill()

print("\n✨ 작업 완료! 확인 후 제출 버튼을 누르세요.")
input("엔터를 누르면 종료됩니다...")
driver.quit()