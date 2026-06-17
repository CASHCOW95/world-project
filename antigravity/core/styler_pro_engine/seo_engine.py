import re
import sys
import json

def evaluate_seo(keyword, html_content):
    score_details = {}
    
    # 1. Word Length (15 pts) - check characters excluding HTML tags
    plain_text = re.sub(r'<[^>]*>', '', html_content)
    char_count = len(plain_text.strip())
    if char_count >= 5000:
        length_score = 15
    elif char_count >= 3500:
        length_score = 10
    else:
        length_score = 5
    score_details["length"] = {"score": length_score, "max": 15, "comment": f"글자 수: {char_count}자 (목표: 5,000자 이상)"}
    
    # 2. H-tag Structure (15 pts)
    # Require H2 x 5~8, H3 x 10~20
    h2_tags = re.findall(r'<h2[^>]*>', html_content, re.IGNORECASE)
    h3_tags = re.findall(r'<h3[^>]*>', html_content, re.IGNORECASE)
    
    h_score = 0
    if 5 <= len(h2_tags) <= 8:
        h_score += 8
    elif len(h2_tags) > 0:
        h_score += 4
        
    if 10 <= len(h3_tags) <= 20:
        h_score += 7
    elif len(h3_tags) > 0:
        h_score += 3
        
    score_details["headings"] = {"score": h_score, "max": 15, "comment": f"H2: {len(h2_tags)}개 (목표: 5~8개), H3: {len(h3_tags)}개 (목표: 10~20개)"}
    
    # 3. Image Alt Tags (10 pts)
    # Require 5 images total with alt tags
    img_tags = re.findall(r'<img[^>]*>', html_content, re.IGNORECASE)
    imgs_with_alt = re.findall(r'<img[^>]+alt=["\'][^"\']+["\']', html_content, re.IGNORECASE)
    
    alt_score = 0
    if len(img_tags) >= 5:
        alt_score += 5
    elif len(img_tags) > 0:
        alt_score += 2
        
    if img_tags and len(imgs_with_alt) == len(img_tags):
        alt_score += 5
    elif len(imgs_with_alt) > 0:
        alt_score += 2
        
    score_details["img_alt"] = {"score": alt_score, "max": 10, "comment": f"이미지: {len(img_tags)}개 (목표: 5개), alt 등록: {len(imgs_with_alt)}개"}
    
    # 4. Tables Included (10 pts)
    # Require 3 tables minimum
    table_tags = re.findall(r'<table[^>]*>', html_content, re.IGNORECASE)
    if len(table_tags) >= 3:
        table_score = 10
    elif len(table_tags) >= 1:
        table_score = 5
    else:
        table_score = 0
    score_details["tables"] = {"score": table_score, "max": 10, "comment": f"표(table): {len(table_tags)}개 (목표: 3개 이상)"}
    
    # 5. FAQ Included (10 pts)
    # Require 10 FAQ items
    faq_questions = re.findall(r'Q\d+\.', html_content, re.IGNORECASE)
    if len(faq_questions) >= 10:
        faq_score = 10
    elif len(faq_questions) >= 5:
        faq_score = 6
    else:
        faq_score = 2
    score_details["faq"] = {"score": faq_score, "max": 10, "comment": f"FAQ 질문 개수: {len(faq_questions)}개 (목표: 10개)"}
    
    # 6. Internal Linking / Table of Contents (10 pts)
    # Table of Contents with 5+ links
    toc_links = re.findall(r'<a[^>]+href=["\']#sec-\d+["\']', html_content, re.IGNORECASE)
    if len(toc_links) >= 5:
        link_score = 10
    elif len(toc_links) >= 2:
        link_score = 5
    else:
        link_score = 0
    score_details["linking"] = {"score": link_score, "max": 10, "comment": f"목차 내부링크: {len(toc_links)}개 (목표: 5개 이상)"}
    
    # 7. Topic Coverage / Key Terms Density (15 pts)
    keyword_count = len(re.findall(re.escape(keyword), plain_text))
    if 8 <= keyword_count <= 30:
        coverage_score = 15
    elif 1 <= keyword_count < 8:
        coverage_score = 8
    else:
        coverage_score = 4
    score_details["coverage"] = {"score": coverage_score, "max": 15, "comment": f"핵심 키워드 빈도: {keyword_count}회"}
    
    # 8. Mobile Readability (15 pts)
    # p-tag text count analysis
    p_tags = re.findall(r'<p[^>]*>(.*?)</p>', html_content, re.DOTALL | re.IGNORECASE)
    long_p_count = 0
    long_ratio = 1.0
    
    if p_tags:
        long_p_count = sum(1 for p in p_tags if len(re.sub(r'<[^>]*>', '', p).strip()) > 180)
        long_ratio = long_p_count / len(p_tags)
        if long_ratio <= 0.15:
            read_score = 15
        elif long_ratio <= 0.4:
            read_score = 10
        else:
            read_score = 5
    else:
        read_score = 0
        
    score_details["readability"] = {"score": read_score, "max": 15, "comment": f"긴 모바일 단락 비율: {round(long_ratio * 100, 1) if p_tags else 100}%"}
    
    total_score = sum(d["score"] for d in score_details.values())
    
    feedbacks = []
    if length_score < 15:
        feedbacks.append(f"본문 글자 수가 {char_count}자로 다소 부족합니다. 5,000자 이상을 충실히 채워주십시오.")
    if h_score < 15:
        feedbacks.append("H2 태그를 5~8개 범위로 조절하고 H3 소주제를 10~20개로 촘촘히 보강하여 글의 목차 구조 깊이를 늘리십시오.")
    if alt_score < 10:
        feedbacks.append("본문에 배치된 5장의 모든 이미지 태그(img)에 alt='설명'과 title='제목' 속성을 누락 없이 입력해 주십시오.")
    if table_score < 10:
        feedbacks.append("비교분석 데이터를 정리한 표(table)를 3개 이상 본문에 포함해야 합니다.")
    if faq_score < 10:
        feedbacks.append(f"독자가 100% 묻는 FAQ 질문 10가지를 채워주십시오. (현재 {len(faq_questions)}개)")
    if link_score < 10:
        feedbacks.append("본문 시작지점의 목차에 내부 앵커 링크(#sec-1 등)를 5개 이상 추가해 주십시오.")
    if coverage_score < 15:
        if keyword_count < 8:
            feedbacks.append(f"핵심 키워드 '{keyword}'가 너무 적게 노출되었습니다. 본문 맥락에 자연스럽게 8회 이상 녹여내십시오.")
        else:
            feedbacks.append(f"핵심 키워드 '{keyword}'가 너무 자주 노출되었습니다. 어뷰징 방지를 위해 대명사나 유의어로 완화해 주십시오.")
    if read_score < 15:
        feedbacks.append("모바일 가독성을 위해, 한 단락(p)은 2~3줄 단위로 짧게 줄바꿈(엔터) 처리해주십시오.")
        
    return {
        "score": total_score,
        "pass": total_score >= 85,
        "details": score_details,
        "feedback": "\n".join(feedbacks)
    }

if __name__ == "__main__":
    test_html = """
    <div class="toc"><a href="#sec-1">1</a></div>
    <h2 id="sec-1">첫 번째</h2>
    <p>짧은 문단입니다.</p>
    <img src="pic1.webp" alt="테스트" title="테스트"/>
    <table></table>
    """
    res = evaluate_seo("당뇨", test_html)
    print(json.dumps(res, ensure_ascii=False, indent=2))
