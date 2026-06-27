import re
import sys
import json

def evaluate_seo(keyword, html_content):
    score_details = {}
    
    # 1. Word Length (15 pts) - check text characters count excluding html tags
    plain_text = re.sub(r'<[^>]*>', '', html_content)
    char_count = len(plain_text.strip())
    if char_count >= 3000:
        length_score = 15
    elif char_count >= 2000:
        length_score = 10
    else:
        length_score = 5
    score_details["length"] = {"score": length_score, "max": 15, "comment": f"글자 수: {char_count}자"}
    
    # 2. H-tag Structure (15 pts)
    h2_tags = re.findall(r'<h2[^>]*>', html_content, re.IGNORECASE)
    h3_tags = re.findall(r'<h3[^>]*>', html_content, re.IGNORECASE)
    h2_ids = re.findall(r'id=["\']sec-\d+["\']', html_content, re.IGNORECASE)
    
    h_score = 0
    if len(h2_tags) >= 5:
        h_score += 10
    elif len(h2_tags) >= 3:
        h_score += 6
    else:
        h_score += 3
        
    if len(h3_tags) >= 3:
        h_score += 5
    elif len(h3_tags) >= 1:
        h_score += 3
        
    score_details["headings"] = {"score": h_score, "max": 15, "comment": f"H2: {len(h2_tags)}개, H3: {len(h3_tags)}개"}
    
    # 3. Image Alt Tags (10 pts)
    img_tags = re.findall(r'<img[^>]*>', html_content, re.IGNORECASE)
    imgs_with_alt = re.findall(r'<img[^>]+alt=["\'][^"\']+["\']', html_content, re.IGNORECASE)
    
    alt_score = 10
    if img_tags:
        if len(imgs_with_alt) == len(img_tags):
            alt_score = 10
        else:
            alt_score = int(10 * (len(imgs_with_alt) / len(img_tags)))
    else:
        alt_score = 0 # No images at all
    score_details["img_alt"] = {"score": alt_score, "max": 10, "comment": f"이미지: {len(img_tags)}개 중 alt 등록 {len(imgs_with_alt)}개"}
    
    # 4. Tables Included (10 pts)
    table_tags = re.findall(r'<table[^>]*>', html_content, re.IGNORECASE)
    if len(table_tags) >= 3:
        table_score = 10
    elif len(table_tags) >= 1:
        table_score = 6
    else:
        table_score = 0
    score_details["tables"] = {"score": table_score, "max": 10, "comment": f"표(table): {len(table_tags)}개"}
    
    # 5. FAQ Included (10 pts)
    # Check for lists/divs containing Q1, Q2 or Q&A patterns
    faq_questions = re.findall(r'Q\d+\.', html_content, re.IGNORECASE)
    if len(faq_questions) >= 8:
        faq_score = 10
    elif len(faq_questions) >= 4:
        faq_score = 6
    else:
        faq_score = 0
    score_details["faq"] = {"score": faq_score, "max": 10, "comment": f"FAQ 질문 개수: {len(faq_questions)}개"}
    
    # 6. Internal Linking / Table of Contents (10 pts)
    toc_links = re.findall(r'<a[^>]+href=["\']#sec-\d+["\']', html_content, re.IGNORECASE)
    if len(toc_links) >= 5:
        link_score = 10
    elif len(toc_links) >= 2:
        link_score = 6
    else:
        link_score = 0
    score_details["linking"] = {"score": link_score, "max": 10, "comment": f"목차 내부링크: {len(toc_links)}개"}
    
    # 7. Topic Coverage / Key Terms Density (15 pts)
    keyword_count = len(re.findall(re.escape(keyword), plain_text))
    # Optimal keyword density: 1% to 2.5% of total text length, say roughly 8 to 25 occurrences for 3000 words
    if 6 <= keyword_count <= 25:
        coverage_score = 15
    elif 1 <= keyword_count < 6:
        coverage_score = 8
    else:
        coverage_score = 5 # Stuffed or too low
    score_details["coverage"] = {"score": coverage_score, "max": 15, "comment": f"핵심 키워드 빈도: {keyword_count}회"}
    
    # 8. Mobile Readability (15 pts)
    # Paragraph lengths (p tag texts). Let's count paragraphs and see how many are short (under 200 chars)
    p_tags = re.findall(r'<p[^>]*>(.*?)</p>', html_content, re.DOTALL | re.IGNORECASE)
    if p_tags:
        long_p_count = sum(1 for p in p_tags if len(re.sub(r'<[^>]*>', '', p).strip()) > 220)
        long_ratio = long_p_count / len(p_tags)
        if long_ratio <= 0.15: # Less than 15% are excessively long
            read_score = 15
        elif long_ratio <= 0.4:
            read_score = 10
        else:
            read_score = 5
    else:
        read_score = 0
    score_details["readability"] = {"score": read_score, "max": 15, "comment": f"긴 모바일 단락 비율: {round(long_ratio * 100, 1) if p_tags else 100}%"}
    
    total_score = sum(d["score"] for d in score_details.values())
    
    # Formulate feedback guidelines if score < 85
    feedbacks = []
    if length_score < 15:
        feedbacks.append(f"본문 글자 수가 {char_count}자로 다소 부족합니다. 3,000자 이상으로 본문 내용을 대폭 살을 찌워주십시오.")
    if h_score < 15:
        feedbacks.append("H2 태그를 최소 5개 이상, H3 태그를 3개 이상 상세하게 배치하여 글의 목차 구조를 깊게 가져가십시오.")
    if alt_score < 10:
        feedbacks.append("삽입된 모든 이미지 태그(img)에 alt='설명'과 title='제목' 속성을 누락 없이 입력해 주십시오.")
    if table_score < 10:
        feedbacks.append("본문 데이터 요약을 돕는 비교표(table)를 반드시 3개 이상 풍부하게 설계하십시오.")
    if faq_score < 10:
        feedbacks.append(f"독자가 진짜 궁금해하는 FAQ Q1~Q8 양식의 핵심 질답 목록을 8개 이상으로 보충하십시오. (현재 {len(faq_questions)}개)")
    if link_score < 10:
        feedbacks.append("본문 시작 지점에 목차를 구성하고 H2 앵커들(#sec-1 등)로 바로 이동할 수 있는 내부 앵커 링크들을 5개 이상 추가해 주십시오.")
    if coverage_score < 15:
        if keyword_count < 6:
            feedbacks.append(f"핵심 키워드 '{keyword}'가 너무 적게 쓰였습니다. 본문 맥락에 맞게 8회 이상 녹여내십시오.")
        else:
            feedbacks.append(f"핵심 키워드 '{keyword}'가 과도하게 반복되어 어뷰징 위험이 있습니다. 자연스러운 대명사나 동의어로 순화해 주십시오.")
    if read_score < 15:
        feedbacks.append("모바일 화면에서의 가독성을 보장하기 위해, 하나의 p 문단은 최대 3~4줄로 짧게 엔터(줄바꿈)를 쳐서 나누어 주십시오.")
        
    return {
        "score": total_score,
        "pass": total_score >= 85,
        "details": score_details,
        "feedback": "\n".join(feedbacks)
    }

if __name__ == "__main__":
    test_html = """
    <div class="toc"><a href="#sec-1">1</a><a href="#sec-2">2</a></div>
    <h2 id="sec-1">첫 번째</h2>
    <p>짧은 문단입니다.</p>
    <img src="pic1.webp" alt="테스트" title="테스트"/>
    <table></table>
    <p>Q1. 질문? A1. 답변.</p>
    """
    res = evaluate_seo("당뇨", test_html)
    print(json.dumps(res, ensure_ascii=False, indent=2))
