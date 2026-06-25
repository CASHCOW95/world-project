import sys
import json
import random
import hashlib
from pathlib import Path

# Load categories and seed keywords dynamically
DB_DIR = Path(__file__).resolve().parent
CATEGORIES_JSON_PATH = DB_DIR / "categories.json"

def load_seed_keywords():
    try:
        with open(CATEGORIES_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            flattened = {}
            for main_cat, val in data.items():
                if isinstance(val, dict):
                    for sub_cat, seeds in val.items():
                        flattened[sub_cat] = seeds
                else:
                    flattened[main_cat] = val
            return flattened
    except Exception as e:
        sys.stderr.write(f"Failed to load categories.json: {str(e)}\n")
        # Hardcoded fallback minimal dictionary
        return {
            "정부지원금": ["정부지원금 조회", "소상공인 지원금 신청", "청년 내일 채움 공제", "근로장려금 지급일", "에너지바우처 신청"],
            "생활꿀팁": ["욕실 찌든때 청소", "세탁기 통세척 방법", "음식물 쓰레기 기준", "초파리 없애는 법", "스티커 자국 제거"]
        }


# Category translation map for legacy English UI queries
CATEGORY_MAP = {
    "life": "생활꿀팁",
    "lifestyle": "생활꿀팁",
    "health": "건강",
    "finance": "재테크",
    "subsidies": "정부지원금",
    "subsidy": "정부지원금",
    "tech": "IT"
}

KEYWORD_MODIFIERS = [
    "실전 가이드", "주의사항 정리", "2026 최신 소식", "비교 분석", "추천 순위 TOP 5",
    "초보자 입문서", "신청 자격 요건", "가장 빠른 해결책", "완벽 정리", "10가지 비법"
]

def find_keywords(category_input):
    seed_keywords = load_seed_keywords()
    
    # Normalize category name
    normalized_cat = CATEGORY_MAP.get(category_input.lower(), category_input)
    
    if normalized_cat not in seed_keywords:
        # Case insensitive check
        found_key = None
        for k in seed_keywords.keys():
            if k.lower() == category_input.lower():
                found_key = k
                break
        if found_key:
            normalized_cat = found_key
        else:
            # Fallback to the first available category
            normalized_cat = list(seed_keywords.keys())[0] if seed_keywords else "정부지원금"
        
    seeds = seed_keywords.get(normalized_cat, ["정부지원금 조회"])
    generated = []
    
    # Expand to 500 keywords
    for seed in seeds:
        for mod in KEYWORD_MODIFIERS:
            generated.append(f"{seed} {mod}")
            
    random.seed(normalized_cat)
    random.shuffle(generated)
    
    while len(generated) < 500:
        seed = random.choice(seeds)
        mod = random.choice(KEYWORD_MODIFIERS)
        generated.append(f"{seed} {mod}")
        
    results = []
    for kw in generated[:500]:
        search_volume = random.randint(2000, 38000)
        competition = random.randint(800, 50000)
        
        # Define CPC level
        if any(w in kw for w in ["대출", "보험", "주식", "금융", "지원금", "보조금", "영양제", "부동산", "세금"]):
            cpc = "높음"
            cpc_factor = 3.0
        elif any(w in kw for w in ["절약", "아끼는", "요금", "제거", "청소", "생활꿀팁"]):
            cpc = "낮음"
            cpc_factor = 0.8
        else:
            cpc = "보통"
            cpc_factor = 1.6
            
        raw_score = (search_volume * cpc_factor) / competition
        golden_score = min(99, max(15, int(raw_score * 12)))
        
        # Simulated calculations based on keyword seed for consistency
        def get_keyword_hash_float(k, min_val, max_val):
            h = hashlib.md5(k.encode('utf-8')).hexdigest()
            val = int(h[:6], 16) / 0xffffff
            return round(min_val + val * (max_val - min_val), 1)

        if cpc == "높음":
            cpc_dollar = get_keyword_hash_float(kw, 2.5, 4.5)
        elif cpc == "낮음":
            cpc_dollar = get_keyword_hash_float(kw, 0.2, 0.9)
        else:
            cpc_dollar = get_keyword_hash_float(kw, 1.0, 2.4)

        visitor_factor = get_keyword_hash_float(kw, 0.10, 0.25)
        estimated_visitors = int(search_volume * visitor_factor)
        ctr = get_keyword_hash_float(kw, 2.5, 5.5)
        estimated_revenue = int(estimated_visitors * (ctr / 100.0) * cpc_dollar * 1400)

        # Determine main category for dynamic affiliate mapping
        def get_main_category_for_sub(sub_cat):
            try:
                with open(CATEGORIES_JSON_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for main, val in data.items():
                        if isinstance(val, dict) and sub_cat in val:
                            return main
            except:
                pass
            return None

        main_cat = get_main_category_for_sub(normalized_cat)

        # Affiliate mapping by category
        if main_cat == "금융":
            affiliate_product = "고금리 파킹통장 개설 및 우대금리 적금 신청 링크"
        elif main_cat == "건강":
            affiliate_product = "식약처 공식 인증 유기농 영양제 최저가 공동구매"
        elif main_cat == "정부정책":
            affiliate_product = "정부 지원 행정 서류 간편 대행 및 자격 심사 조회"
        elif main_cat == "비즈니스":
            affiliate_product = "초보 블로거를 위한 애드센스 고수익 승인 공략집 전자책"
        elif main_cat == "부동산":
            affiliate_product = "전국 유망 부동산 청약 정보 및 실시간 시세 분석 리포트"
        elif main_cat == "디지털":
            affiliate_product = "최신 가성비 디지털 기기 및 IT 액세서리 쿠팡 특가 링크"
        elif main_cat == "전문직":
            affiliate_product = "내용증명 양식 다운로드 및 실시간 무료 법률 대행 서비스"
        else:
            affiliate_product = "다용도 친환경 곰팡이 방지 세정 스프레이 할인 기획전"

        if golden_score >= 80 and cpc == "높음":
            ai_badge = "🟢 무조건 작성"
        elif golden_score >= 65 and cpc != "낮음":
            ai_badge = "🔵 작성 추천"
        elif golden_score >= 45:
            ai_badge = "🟡 보류"
        else:
            ai_badge = "🔴 경쟁 과열"

        ratio = search_volume / max(1, competition)
        base_ocean = int(ratio * 15 + get_keyword_hash_float(kw, -5.0, 5.0))
        blue_ocean_score = min(99, max(5, int(base_ocean + golden_score * 0.5)))
        
        if blue_ocean_score >= 85:
            blue_ocean_recommend = "매우 높음"
        elif blue_ocean_score >= 65:
            blue_ocean_recommend = "높음"
        elif blue_ocean_score >= 45:
            blue_ocean_recommend = "보통"
        else:
            blue_ocean_recommend = "낮음"

        results.append({
            "keyword": kw,
            "search_volume": search_volume,
            "competition": competition,
            "cpc": cpc,
            "golden_score": golden_score,
            "category": normalized_cat,
            "cpc_dollar": cpc_dollar,
            "estimated_visitors": estimated_visitors,
            "ctr": ctr,
            "estimated_revenue": estimated_revenue,
            "affiliate_product": affiliate_product,
            "ai_badge": ai_badge,
            "blue_ocean_score": blue_ocean_score,
            "blue_ocean_recommend": blue_ocean_recommend
        })
        
    results.sort(key=lambda x: (x["golden_score"], x["search_volume"]), reverse=True)
    return results[:100]

if __name__ == "__main__":
    cat = "정부지원금"
    if len(sys.argv) > 1:
        cat = sys.argv[1]
    output = find_keywords(cat)
    print(json.dumps(output, ensure_ascii=False, indent=2))
