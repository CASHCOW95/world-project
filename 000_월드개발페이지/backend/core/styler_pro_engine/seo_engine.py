import re
import sys
import json

def evaluate_seo(keyword, html_content):
    score_details = {}
    
    # Clean tags for text checks
    plain_text = re.sub(r'<[^>]*>', ' ', html_content)
    # Replace multiple spaces with a single space
    plain_text = re.sub(r'\s+', ' ', plain_text).strip()
    char_count = len(plain_text)
    
    # 1. Word Length (8 pts)
    if char_count >= 5000:
        length_score = 8
    elif char_count >= 3500:
        length_score = 5
    else:
        length_score = 2
    score_details["length"] = {"score": length_score, "max": 8, "comment": f"본문 글자 수: {char_count}자 (목표: 5000자 이상)"}
    
    # 2. H-tag Structure (8 pts)
    h2_tags = re.findall(r'<h2[^>]*>', html_content, re.IGNORECASE)
    h3_tags = re.findall(r'<h3[^>]*>', html_content, re.IGNORECASE)
    h_score = 0
    if 5 <= len(h2_tags) <= 8:
        h_score += 4
    elif len(h2_tags) > 0:
        h_score += 2
        
    if 10 <= len(h3_tags) <= 20:
        h_score += 4
    elif len(h3_tags) > 0:
        h_score += 2
    score_details["headings"] = {"score": h_score, "max": 8, "comment": f"H2: {len(h2_tags)}개 (목표: 5~8), H3: {len(h3_tags)}개 (목표: 10~20)"}
    
    # 3. Image Alt Tags (8 pts)
    img_tags = re.findall(r'<img[^>]*>', html_content, re.IGNORECASE)
    imgs_with_alt = re.findall(r'<img[^>]+alt=["\'][^"\']+["\']', html_content, re.IGNORECASE)
    alt_score = 0
    if len(img_tags) >= 5:
        alt_score += 4
    elif len(img_tags) > 0:
        alt_score += 2
    if img_tags and len(imgs_with_alt) == len(img_tags):
        alt_score += 4
    elif len(imgs_with_alt) > 0:
        alt_score += 2
    score_details["img_alt"] = {"score": alt_score, "max": 8, "comment": f"이미지: {len(img_tags)}개, alt: {len(imgs_with_alt)}개"}
    
    # 4. Tables Included (8 pts)
    table_tags = re.findall(r'<table[^>]*>', html_content, re.IGNORECASE)
    if len(table_tags) >= 3:
        table_score = 8
    elif len(table_tags) >= 1:
        table_score = 4
    else:
        table_score = 0
    score_details["tables"] = {"score": table_score, "max": 8, "comment": f"표(table): {len(table_tags)}개 (목표: 3개 이상)"}
    
    # 5. FAQ Included (8 pts)
    faq_questions = re.findall(r'Q\d+\.', html_content, re.IGNORECASE)
    if len(faq_questions) >= 10:
        faq_score = 8
    elif len(faq_questions) >= 5:
        faq_score = 4
    else:
        faq_score = 1
    score_details["faq"] = {"score": faq_score, "max": 8, "comment": f"FAQ 개수: {len(faq_questions)}개 (목표: 10개)"}
    
    # 6. Internal Linking / TOC (8 pts)
    toc_links = re.findall(r'<a[^>]+href=["\']#sec-\d+["\']', html_content, re.IGNORECASE)
    if len(toc_links) >= 5:
        link_score = 8
    elif len(toc_links) >= 2:
        link_score = 4
    else:
        link_score = 0
    score_details["linking"] = {"score": link_score, "max": 8, "comment": f"목차 내부링크: {len(toc_links)}개 (목표: 5개 이상)"}
    
    # 7. Topic Coverage / Key Terms Density (8 pts)
    keyword_count = len(re.findall(re.escape(keyword), plain_text))
    if 8 <= keyword_count <= 30:
        coverage_score = 8
    elif 1 <= keyword_count < 8:
        coverage_score = 4
    else:
        coverage_score = 2
    score_details["coverage"] = {"score": coverage_score, "max": 8, "comment": f"핵심 키워드 노출 빈도: {keyword_count}회"}
    
    # 8. Mobile Readability (8 pts)
    p_tags = re.findall(r'<p[^>]*>(.*?)</p>', html_content, re.DOTALL | re.IGNORECASE)
    long_p_count = 0
    long_ratio = 1.0
    if p_tags:
        long_p_count = sum(1 for p in p_tags if len(re.sub(r'<[^>]*>', '', p).strip()) > 180)
        long_ratio = long_p_count / len(p_tags)
        if long_ratio <= 0.15:
            read_score = 8
        elif long_ratio <= 0.4:
            read_score = 5
        else:
            read_score = 2
    else:
        read_score = 0
    score_details["readability"] = {"score": read_score, "max": 8, "comment": f"긴 단락 비율: {round(long_ratio * 100, 1)}%"}
    
    # 9. Keyword Naturalness (9 pts)
    # Check for stuffed keywords or adjacent repeating words
    natural_score = 9
    adjacent_dups = re.findall(r'\b(\w+)\s+\1\b', plain_text)
    if adjacent_dups:
        natural_score -= min(4, len(adjacent_dups) * 2) # deduct for adjacent duplicate words
    if keyword_count > 30:
        natural_score -= 3 # stuffed keyword penalty
        
    # Check if keyword repeats too closely (e.g. within 20 words)
    keyword_indices = [m.start() for m in re.finditer(re.escape(keyword), plain_text)]
    close_calls = 0
    for idx in range(len(keyword_indices) - 1):
        if keyword_indices[idx+1] - keyword_indices[idx] < len(keyword) + 60: # very close keywords
            close_calls += 1
    if close_calls > 3:
        natural_score -= min(2, close_calls - 3)
        
    natural_score = max(0, natural_score)
    score_details["naturalness"] = {"score": natural_score, "max": 9, "comment": f"인접 단어 중복: {len(adjacent_dups)}회, 키워드 근접 노출: {close_calls}회"}
    
    # 10. Topic Consistency (9 pts)
    # Check if this article mixes in unrelated topics (e.g. youth employment terms in small business or general)
    consistency_score = 9
    clean_keyword = keyword.replace(" ", "")
    is_youth_related = "청년" in clean_keyword or "내일채움" in clean_keyword or "청내공" in clean_keyword
    
    if not is_youth_related:
        # If it is NOT youth related, check for youth-policy specific words
        youth_words = ["청년내일채움공제", "청내공", "군필 청년", "청년 가입", "워크넷 신청"]
        found_youth = [w for w in youth_words if w in plain_text]
        if found_youth:
            consistency_score -= min(6, len(found_youth) * 2)
            
    # Check for other unrelated category terms
    is_health_related = any(w in clean_keyword for w in ["당뇨", "혈압", "지혈", "비타민", "의학", "질환"])
    if not is_health_related:
        health_words = ["당뇨 환자", "인슐린", "콜레스테롤", "의사 처방", "간수치"]
        found_health = [w for w in health_words if w in plain_text]
        if found_health:
            consistency_score -= min(3, len(found_health))
            
    consistency_score = max(0, consistency_score)
    score_details["consistency"] = {"score": consistency_score, "max": 9, "comment": f"이종 카테고리 정책 어휘 유입 감점 유무 (점수: {consistency_score}/9)"}
    
    # 11. Fact Accuracy (9 pts)
    # Penalize fake meta terms like "가독성 55점", "체류시간 180초", "스타일러 프로"
    fact_score = 9
    fake_terms = ["가독성 향상", "체류시간 유도", "체류 시간", "포스팅 작성 가이드", "SEO 노출", "가독성 점수", "체류시간 점수", "스타일러 프로"]
    found_fake = [t for t in fake_terms if t in plain_text]
    if found_fake:
        fact_score -= min(5, len(found_fake) * 2)
        
    # Check if statistics are written using placeholders
    placeholders = ["00%", "000원", "00개", "xx년", "xx월"]
    found_placeholders = [p for p in placeholders if p in plain_text]
    if found_placeholders:
        fact_score -= min(4, len(found_placeholders) * 2)
        
    fact_score = max(0, fact_score)
    score_details["fact_accuracy"] = {"score": fact_score, "max": 9, "comment": f"메타 지표/더미 데이터 노출 감점 유무 (점수: {fact_score}/9)"}
    
    # 12. Duplicate Sentence Ratio (9 pts)
    # Split text into sentences and check redundancy
    dup_sentence_score = 9
    sentences = [s.strip() for s in re.split(r'[.!?\n]', plain_text) if len(s.strip()) > 10]
    if len(sentences) > 5:
        seen = set()
        dups = 0
        for s in sentences:
            if s in seen:
                dups += 1
            else:
                seen.add(s)
        dup_ratio = dups / len(sentences)
        if dup_ratio > 0.15:
            dup_sentence_score = 2
        elif dup_ratio > 0.05:
            dup_sentence_score = 5
        else:
            dup_sentence_score = 9
    else:
        dup_ratio = 0.0
        
    score_details["dup_ratio"] = {"score": dup_sentence_score, "max": 9, "comment": f"중복 문장 비율: {round(dup_ratio * 100, 1)}%"}
    
    total_score = sum(d["score"] for d in score_details.values())
    
    feedbacks = []
    if length_score < 8:
        feedbacks.append(f"본문 글자 수가 {char_count}자로 다소 부족합니다. 5,000자 이상을 충실히 채워주십시오.")
    if h_score < 8:
        feedbacks.append("H2 태그를 5~8개 범위로 조절하고 H3 소주제를 10~20개로 촘촘히 보강하여 글의 목차 구조 깊이를 늘리십시오.")
    if alt_score < 8:
        feedbacks.append("본문에 배치된 5장의 모든 이미지 태그(img)에 alt 및 title 속성을 누락 없이 입력해 주십시오.")
    if table_score < 8:
        feedbacks.append("비교분석 데이터를 정리한 표(table)를 3개 이상 본문에 포함해야 합니다.")
    if faq_score < 8:
        feedbacks.append(f"FAQ 질문 10가지를 채워주십시오. (현재 {len(faq_questions)}개)")
    if link_score < 8:
        feedbacks.append("본문 시작지점의 목차에 내부 앵커 링크(#sec-1 등)를 5개 이상 추가해 주십시오.")
    if coverage_score < 8:
        feedbacks.append(f"핵심 키워드 '{keyword}'가 너무 적게 쓰였거나 지나치게 반복되었습니다. 8회~30회 내외로 자연스럽게 배치하십시오.")
    if read_score < 8:
        feedbacks.append("모바일 가독성을 위해, 한 단락(p)은 2~3줄 단위로 짧게 줄바꿈(엔터) 처리해주십시오.")
    if natural_score < 9:
        feedbacks.append("동일한 단어의 어색한 연속 중복 노출을 지양하고 키워드 배치를 넓게 고루 펴주십시오.")
    if consistency_score < 9:
        feedbacks.append("키워드 주제와 전혀 부합하지 않는 다른 지원금(청내공, 워크넷 등)이나 타 분야 전문 용어가 유입되었습니다. 해당 이종 내용을 완전히 제거해 주십시오.")
    if fact_score < 9:
        feedbacks.append("본문 텍스트 내에 글 쓰기 과정을 설명하는 불필요한 메타 가이드 단어(가독성 향상, 체류시간 유도 등)나 더미 서식(xx년, 00원 등)을 제거해 주십시오.")
    if dup_sentence_score < 9:
        feedbacks.append(f"글 분량을 채우기 위해 동일한 문장을 중복 복사하여 사용한 패턴이 감지되었습니다. 중복된 문장을 삭제하거나 새 정보로 개정하십시오.")

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
    <p>짧은 문단입니다. 신청 신청.</p>
    <img src="pic1.webp" alt="테스트" title="테스트"/>
    <table></table>
    """
    res = evaluate_seo("당뇨", test_html)
    print(json.dumps(res, ensure_ascii=False, indent=2))
