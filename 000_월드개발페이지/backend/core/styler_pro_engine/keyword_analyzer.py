import sys
import json
import random
from pathlib import Path

# Seed data to generate realistic keywords per category
SEED_KEYWORDS = {
    "health": [
        "당뇨 환자 과일", "고혈압에 좋은 음식", "고지혈증 영양제", "비타민D 권장량", "오메가3 고르는 법",
        "간수치 낮추는 법", "위염에 좋은 차", "역류성 식도염 증상", "탈모 초기 증상", "유산균 복용 시간",
        "크릴오일 효능", "루테인 효과", "대상포진 초기증상", "콜레스테롤 낮추는 법", "아르기닌 부작용",
        "콜라겐 추천", "맥주효모 탈모", "밀크씨슬 실체", "눈 밑 떨림 원인", "비오틴 효과"
    ],
    "finance": [
        "미국 주식 추천", "비트코인 반감기", "청약 통장 전환", "개인 연금 저축", "ISA 계좌 혜택",
        "주택 담보 대출 금리", "소상공인 지원금", "양도소득세 계산기", "종합소득세 신고", "연말정산 미리보기",
        "적격대출 자격", "엔화 환전 팁", "배당주 투자 전략", "금값 시세 전망", "특례보금자리론",
        "실손보험 청구서류", "신용등급 올리기", "파킹통장 추천", "CMA 금리 비교", "근로장려금 신청"
    ],
    "lifestyle": [
        "감기몸살 빨리 낫는 법", "가스비 아끼는 꿀팁", "전기세 절약 방법", "수도요금 줄이는 법", "핸드폰 배터리 오래 쓰는 법",
        "겨울철 난방비 절약", "여름철 전기세 절감", "자동차 기름값 절약", "식비 절약하는 방법", "인터넷 요금 할인",
        "집에서 곰팡이 제거", "옷에 묻은 볼펜 자국", "싱크대 냄새 제거", "에어컨 청소 셀프", "세탁기 청소 방법",
        "텀블러 냄새 제거", "과일 세척법", "초간단 계란말이", "에어프라이어 청소", "흰옷 얼룩 제거"
    ],
    "tech": [
        "노트북 가성비 추천", "아이폰 17 출시일", "갤럭시 S26 울트라", "아이패드 프로 할인", "기계식 키보드 입문",
        "알뜰폰 요금제 비교", "VPN 추천 무료", "유튜브 프리미엄 우회", "챗GPT 한글 사용법", "스마트워치 가성비",
        "블루투스 이어폰 순위", "외장하드 복구 비용", "윈도우 11 정품인증", "모니터 크기 추천", "무선 마우스 가성비",
        "웹캠 추천", "코딩 입문 언어", "AI 이미지 생성 사이트", "스마트스토어 시작하기", "티스토리 애드센스 승인"
    ]
}

# Modifiers to expand to 500 keywords
KEYWORD_MODIFIERS = [
    "실전 가이드", "핵심 정리", "부작용 및 효능", "주의사항 총정리", "2026 최신 정보",
    "이유와 해결책", "비교 분석", "추천 순위 TOP 5", "초보자 가이드", "신청 자격 및 조건",
    "아끼는 방법", "완벽 정리", "10가지 비법", "꿀팁 대방해", "쉽고 빠른 방법"
]

def generate_500_keywords(category):
    seeds = SEED_KEYWORDS.get(category, SEED_KEYWORDS["lifestyle"])
    generated = []
    
    # 1. Base keywords with modifiers
    for seed in seeds:
        for mod in KEYWORD_MODIFIERS:
            generated.append(f"{seed} {mod}")
            
    # 2. Shuffle and trim or pad to exactly 500
    random.seed(category) # Ensure deterministic but natural list per category
    random.shuffle(generated)
    
    while len(generated) < 500:
        seed = random.choice(seeds)
        mod = random.choice(KEYWORD_MODIFIERS)
        generated.append(f"{seed} {mod}")
        
    return generated[:500]

def analyze_keywords(category):
    raw_list = generate_500_keywords(category)
    results = []
    
    for idx, kw in enumerate(raw_list):
        # Generate realistic metrics
        search_volume = random.randint(1500, 35000)
        competition = random.randint(800, 45000)
        
        # Determine CPC based on keyword topics
        if any(w in kw for w in ["대출", "보험", "주식", "청약", "계좌", "비트코인", "영양제", "임문"]):
            cpc_level = "high"
            cpc_factor = 2.5 + random.uniform(0.5, 1.5)
        elif any(w in kw for w in ["아끼는", "절약", "요금", "제거", "청소", "얼룩"]):
            cpc_level = "low"
            cpc_factor = 0.8 + random.uniform(0.1, 0.4)
        else:
            cpc_level = "medium"
            cpc_factor = 1.4 + random.uniform(0.2, 0.6)
            
        # Calculate raw score
        raw_score = (search_volume * cpc_factor) / competition
        
        # Scale to a neat 0-100 score format
        golden_score = min(99, max(15, int(raw_score * 15)))
        
        results.append({
            "keyword": kw,
            "search_volume": search_volume,
            "competition": competition,
            "cpc": cpc_level,
            "golden_score": golden_score
        })
        
    # Sort by golden_score descending, then search_volume descending
    results.sort(key=lambda x: (x["golden_score"], x["search_volume"]), reverse=True)
    
    # Return TOP 100
    return results[:100]

if __name__ == "__main__":
    category = "lifestyle"
    if len(sys.argv) > 1:
        category = sys.argv[1]
        
    output = analyze_keywords(category)
    print(json.dumps(output, ensure_ascii=False, indent=2))
