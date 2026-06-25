import re
import sys
import json

def evaluate_profitability(keyword, search_volume, competition, cpc_level, html_content):
    score = 0
    breakdown = {}
    
    # 1. CPC Ad Bid Value (Max 30)
    cpc_score = 10
    if cpc_level == "high":
        cpc_score = 30
    elif cpc_level == "medium":
        cpc_score = 20
    else:
        cpc_score = 10
    score += cpc_score
    breakdown["cpc"] = {"score": cpc_score, "max": 30}
    
    # 2. Search Volume Traffic Scale (Max 20)
    vol_score = 5
    if search_volume >= 25000:
        vol_score = 20
    elif search_volume >= 12000:
        vol_score = 15
    elif search_volume >= 5000:
        vol_score = 10
    else:
        vol_score = 5
    score += vol_score
    breakdown["volume"] = {"score": vol_score, "max": 20}
    
    # 3. Commercial / Purchase Intent (Max 20)
    # Keywords with commercial trigger words indicate high intent
    commercial_triggers = ["추천", "비교", "가격", "신청", "대출", "보험", "꿀팁", "비법", "후기", "바이블"]
    has_trigger = any(t in keyword for t in commercial_triggers)
    intent_score = 20 if has_trigger else 10
    score += intent_score
    breakdown["intent"] = {"score": intent_score, "max": 20}
    
    # 4. Ad Placement Suitability (Max 15)
    # Check for content layout triggers (tables, CTA banners, FAQ lists) that capture high CTR
    has_tables = len(re.findall(r'<table', html_content, re.IGNORECASE)) >= 2
    has_cta = "cta-banner" in html_content or "href=" in html_content
    has_faq = len(re.findall(r'Q\d+\.', html_content, re.IGNORECASE)) >= 5
    
    ad_layout_score = 0
    if has_tables: ad_layout_score += 5
    if has_cta: ad_layout_score += 5
    if has_faq: ad_layout_score += 5
    score += ad_layout_score
    breakdown["ad_layout"] = {"score": ad_layout_score, "max": 15}
    
    # 5. Competition Difficulty Inverse Weight (Max 15)
    # Lower competition relative to volume means easier rank & profit
    ratio = search_volume / max(1, competition)
    comp_score = 5
    if ratio >= 4.0:
        comp_score = 15
    elif ratio >= 1.5:
        comp_score = 10
    else:
        comp_score = 5
    score += comp_score
    breakdown["competitiveness"] = {"score": comp_score, "max": 15}
    
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
        
    return {
        "score": score,
        "grade": grade,
        "estimated_rpm": rpm,
        "cpc_rating": "높음" if cpc_level == "high" else "보통" if cpc_level == "medium" else "낮음",
        "breakdown": breakdown
    }

if __name__ == "__main__":
    test_html = '<div class="cta-banner">CTA</div><table class="table"></table><table class="table"></table>Q1. A1. Q2. A2. Q3. A3. Q4. A4. Q5. A5.'
    res = evaluate_profitability("당뇨 대출 추천", 15000, 3100, "high", test_html)
    print(json.dumps(res, ensure_ascii=False, indent=2))
