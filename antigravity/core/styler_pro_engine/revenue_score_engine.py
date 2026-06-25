import re
import sys
import json
import hashlib

def evaluate_revenue(keyword, search_volume, cpc_level, html_content):
    score = 0
    breakdown = {}
    
    # 1. CPC Bid Value (Max 30)
    cpc_score = 10
    if cpc_level == "높음":
        cpc_score = 30
    elif cpc_level == "보통":
        cpc_score = 20
    else:
        cpc_score = 10
    score += cpc_score
    breakdown["cpc"] = {"score": cpc_score, "max": 30}
    
    # 2. Search Volume (Max 25)
    vol_score = 10
    if search_volume >= 25000:
        vol_score = 25
    elif search_volume >= 12000:
        vol_score = 20
    elif search_volume >= 5000:
        vol_score = 15
    else:
        vol_score = 10
    score += vol_score
    breakdown["volume"] = {"score": vol_score, "max": 25}
    
    # 3. Commercial Intent (Max 15)
    commercial_triggers = ["신청", "조회", "대출", "지원금", "가성비", "절약", "수수료", "가격", "비교"]
    has_commercial = any(t in keyword for t in commercial_triggers)
    intent_score = 15 if has_commercial else 8
    score += intent_score
    breakdown["intent"] = {"score": intent_score, "max": 15}
    
    # 4. Ad Placement Suitability (Max 15)
    # Target: 3 tables and 10 FAQs
    table_count = len(re.findall(r'<table', html_content, re.IGNORECASE))
    faq_count = len(re.findall(r'Q\d+\.', html_content, re.IGNORECASE))
    
    ad_suitability = 0
    if table_count >= 3:
        ad_suitability += 8
    elif table_count >= 1:
        ad_suitability += 4
        
    if faq_count >= 10:
        ad_suitability += 7
    elif faq_count >= 5:
        ad_suitability += 4
        
    score += ad_suitability
    breakdown["ad_suitability"] = {"score": ad_suitability, "max": 15}
    
    # 5. CTA Placement Suitability (Max 15)
    # Target: 4 CTA block occurrences
    cta_count = html_content.count("cta-block")
    cta_score = 5
    if cta_count >= 4:
        cta_score = 15
    elif cta_count >= 2:
        cta_score = 10
    else:
        cta_score = 5
    score += cta_score
    breakdown["cta_suitability"] = {"score": cta_score, "max": 15}
    
    # Determine Class Grade
    if score >= 90:
        grade = "S"
        rpm = "상 (High)"
    elif score >= 80:
        grade = "A+"
        rpm = "상 (High)"
    elif score >= 70:
        grade = "A"
        rpm = "중 (Medium)"
    elif score >= 55:
        grade = "B"
        rpm = "중 (Medium)"
    else:
        grade = "C"
        rpm = "하 (Low)"

    # Seed-based exact metrics mapping for consistent layout feedback
    def get_keyword_hash_float(k, min_val, max_val):
        h = hashlib.md5(k.encode('utf-8')).hexdigest()
        val = int(h[:6], 16) / 0xffffff
        return round(min_val + val * (max_val - min_val), 3)

    if cpc_level == "높음":
        cpc_dollar = get_keyword_hash_float(keyword, 2.5, 4.5)
    elif cpc_level == "낮음":
        cpc_dollar = get_keyword_hash_float(keyword, 0.2, 0.9)
    else:
        cpc_dollar = get_keyword_hash_float(keyword, 1.0, 2.4)

    visitor_factor = get_keyword_hash_float(keyword, 0.01, 0.05)
    estimated_visitors = int(search_volume * visitor_factor)

    # Boost CTR based on post-processing quality (scaled down to realistic Adsense CTR)
    base_ctr = get_keyword_hash_float(keyword, 0.8, 2.2)
    ctr_boost = 0.0
    if cta_count >= 4:
        ctr_boost += 0.3
    elif cta_count >= 2:
        ctr_boost += 0.15
    if table_count >= 3:
        ctr_boost += 0.1
    if faq_count >= 10:
        ctr_boost += 0.1
    ctr = round(base_ctr + ctr_boost, 2)

    # Calculate estimated revenue based on standard CTR/CPC
    estimated_revenue = int(estimated_visitors * (ctr / 100.0) * cpc_dollar * 1400)

    # Category matching logic based on keyword terms
    category = "생활"
    if any(w in keyword for w in ["개인", "대출", "ISA", "배당주", "연말정산", "신용등급", "파킹통장", "CMA"]):
        category = "금융"
    elif any(w in keyword for w in ["당뇨", "고혈압", "고지혈증", "비타민", "간수치", "위염", "식도염", "탈모"]):
        category = "건강"
    elif any(w in keyword for w in ["정부", "지원금", "소상공인", "청년", "근로장려금", "주거급여", "바우처", "취업", "보조금"]):
        category = "정부지원금"
    elif any(w in keyword for w in ["노트북", "티스토리", "애드센스", "챗GPT", "알뜰폰", "유튜브", "아이폰", "갤럭시"]):
        category = "IT"

    if category == "금융":
        affiliate_product = "고금리 파킹통장 개설 및 신용카드 캐시백 혜택"
    elif category == "건강":
        affiliate_product = "식약처 인증 유기농 당뇨 예방 루테인 90일분"
    elif category == "정부지원금":
        affiliate_product = "소상공인 정책자금 신청서 자동 작성 가이드북"
    elif category == "IT":
        affiliate_product = "초보자를 위한 구글 애드센스 승인 치트키 전자책"
    else:
        affiliate_product = "에어컨 청소 및 다용도 곰팡이 방지 방수 스프레이"

    # AI Recommendation Badge
    # Golden score calculation replica
    if any(w in keyword for w in ["대출", "보험", "주식", "금융", "지원금", "보조금", "영양제"]):
        cpc_factor = 3.0
    elif any(w in keyword for w in ["절약", "아끼는", "요금", "제거", "청소"]):
        cpc_factor = 0.8
    else:
        cpc_factor = 1.6
    comp_denominator = max(100, int(search_volume / visitor_factor / 1.5)) # Competition mock
    raw_gold = (search_volume * cpc_factor) / comp_denominator
    golden_score = min(99, max(15, int(raw_gold * 12)))

    if golden_score >= 80 and cpc_level == "높음":
        ai_badge = "🟢 무조건 작성"
    elif golden_score >= 65 and cpc_level != "낮음":
        ai_badge = "🔵 작성 추천"
    elif golden_score >= 45:
        ai_badge = "🟡 보류"
    else:
        ai_badge = "🔴 경쟁 과열"

    base_ocean = int((search_volume / comp_denominator) * 15 + get_keyword_hash_float(keyword, -5.0, 5.0))
    blue_ocean_score = min(99, max(5, int(base_ocean + golden_score * 0.5)))
    
    if blue_ocean_score >= 85:
        blue_ocean_recommend = "매우 높음"
    elif blue_ocean_score >= 65:
        blue_ocean_recommend = "높음"
    elif blue_ocean_score >= 45:
        blue_ocean_recommend = "보통"
    else:
        blue_ocean_recommend = "낮음"
        
    return {
        "score": score,
        "grade": grade,
        "estimated_rpm": rpm,
        "cpc_rating": cpc_level,
        "breakdown": breakdown,
        "cpc_dollar": cpc_dollar,
        "estimated_visitors": estimated_visitors,
        "ctr": ctr,
        "estimated_revenue": estimated_revenue,
        "affiliate_product": affiliate_product,
        "ai_badge": ai_badge,
        "blue_ocean_score": blue_ocean_score,
        "blue_ocean_recommend": blue_ocean_recommend
    }

if __name__ == "__main__":
    test_html = '<div class="cta-block"></div><div class="cta-block"></div><div class="cta-block"></div><div class="cta-block"></div><table></table><table></table><table></table>Q1. Q2. Q3. Q4. Q5. Q6. Q7. Q8. Q9. Q10.'
    res = evaluate_revenue("지원금 신청 여권", 15000, "높음", test_html)
    print(json.dumps(res, ensure_ascii=False, indent=2))

