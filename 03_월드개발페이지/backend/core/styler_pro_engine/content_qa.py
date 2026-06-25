import re
import sys
import json

def evaluate_qa(keyword, category, title, blocks, html_content, citations):
    """
    Styler Pro X 최종 발행 전 콘텐츠 품질 검증(QA) 엔진.
    
    Returns:
        {
            "pass": bool,
            "details": {
                "title_duplication": bool,
                "policy_consistency": bool,
                "faq_relevance": bool,
                "table_alignment": bool,
                "citation_relevance": bool,
                "context_naturalness": bool
            },
            "feedback": str
        }
    """
    details = {
        "title_duplication": True,
        "policy_consistency": True,
        "faq_relevance": True,
        "table_alignment": True,
        "citation_relevance": True,
        "context_naturalness": True
    }
    
    feedbacks = []
    plain_text = re.sub(r'<[^>]*>', ' ', html_content)
    plain_text = re.sub(r'\s+', ' ', plain_text).strip()
    
    # 1. 제목 중복 단어 검사 (예: "신청 신청")
    adjacent_title_dups = re.findall(r'\b(\w+)\s+\1\b', title)
    if adjacent_title_dups:
        details["title_duplication"] = False
        feedbacks.append(f"제목에 인접하여 반복되는 단어({', '.join(adjacent_title_dups)})가 있습니다. 제목을 자연스럽게 수정하십시오.")

    # 2. 정책명 일치 여부 (주제 오염 검출)
    clean_keyword = keyword.replace(" ", "")
    is_youth_related = any(w in clean_keyword for w in ["청년", "내일채움", "청내공", "구직청년", "군필"])
    is_sangsang_related = "소상공인" in clean_keyword
    
    # 소상공인 주제인데 청년 복지 사업 정책명이 유입된 경우 검출
    if is_sangsang_related:
        youth_terms = ["청년내일채움공제", "청내공", "군필 청년", "워크넷 신청", "청년 가입 연령", "정규직 채용 기준"]
        found_youth = [w for w in youth_terms if w in plain_text]
        if found_youth:
            details["policy_consistency"] = False
            feedbacks.append(f"소상공인 지원금 주제임에도 불구하고 청년 지원 정책 관련 어휘({', '.join(found_youth)})가 혼합되어 삽입되었습니다. 주제와 무관한 정책명을 완전히 삭제하십시오.")
            
    # 청년 주제가 아닌데 청년 관련 정책명이 유입된 경우 검출
    elif not is_youth_related:
        youth_terms = ["청년내일채움공제", "청내공", "군필 청년", "워크넷 신청"]
        found_youth = [w for w in youth_terms if w in plain_text]
        if found_youth:
            details["policy_consistency"] = False
            feedbacks.append(f"청년 관련 주제가 아님에도 불구하고 청년 전용 정책 관련 용어({', '.join(found_youth)})가 유입되었습니다. 본문 내용을 정밀 정제하십시오.")

    # 3. FAQ 일치 여부 (본문 내용과 FAQ 맥락 일관성 검사)
    faq_blocks = [b for b in blocks if b.get("type") == "FAQ"]
    if faq_blocks:
        faq_items = faq_blocks[0].get("items", [])
        faq_text = " ".join([item.get("question", "") + " " + item.get("answer", "") for item in faq_items if isinstance(item, dict)])
        
        # 소상공인 주제인데 FAQ에 청년 일자리 질문이 들어가 있는 경우 검출
        if is_sangsang_related and any(w in faq_text for w in ["청년", "군필", "워크넷", "청내공"]):
            details["faq_relevance"] = False
            feedbacks.append("FAQ 목록 중 일부 질문/답변이 소상공인이 아닌 청년 취업공제 및 군필자 등 엉뚱한 정책 내용으로 작성되었습니다. FAQ를 본문 요약 컨텍스트에 맞춰 재작성하십시오.")
        elif not is_youth_related and any(w in faq_text for w in ["청년내일채움공제", "청내공", "군필 청년", "워크넷"]):
            details["faq_relevance"] = False
            feedbacks.append("FAQ 내용이 본문의 주제 범위를 벗어난 청년내일채움공제 관련 질문들로 오염되었습니다. FAQ를 완전히 교체하십시오.")

    # 4. 표 데이터 일치 여부
    table_blocks = [b for b in blocks if b.get("type") == "TABLE"]
    if table_blocks:
        for t_idx, table in enumerate(table_blocks):
            headers = " ".join(table.get("headers", []))
            rows_text = " ".join([" ".join(row) for row in table.get("rows", [])])
            table_combined = headers + " " + rows_text
            
            if is_sangsang_related and any(w in table_combined for w in ["청년", "워크넷", "군필", "채용 기준"]):
                details["table_alignment"] = False
                feedbacks.append(f"{t_idx+1}번째 표(Table) 데이터에 청년 채용이나 군필 청년 등의 무관한 데이터가 포함되어 있습니다. 표 항목을 소상공인 요건에 맞춰 재배치하십시오.")
            elif not is_youth_related and any(w in table_combined for w in ["청년내일채움공제", "청내공", "군필 청년", "워크넷 신청"]):
                details["table_alignment"] = False
                feedbacks.append(f"{t_idx+1}번째 표(Table) 데이터가 본문 키워드와 불일치하며 청년 지원 정책 내용으로 구성되었습니다. 표 정보를 재조정하십시오.")

    # 5. 출처 관련성 검사 (Relevance Score 70점 미만 또는 무관한 정책명 포함 출처 배제)
    if citations:
        low_citations = [c for c in citations if c.get("relevance_score", 100) < 70]
        if low_citations:
            details["citation_relevance"] = False
            feedbacks.append(f"Keyword Relevance Score가 70점 미만인 출처 자료({', '.join([c.get('title', '') for c in low_citations])})가 포함되어 있습니다. 관련성이 떨어지는 출처를 배제하십시오.")

    # 6. 문맥 자연스러움 (중복 문장 비율 및 어색한 중복어)
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
        if dup_ratio > 0.05:
            details["context_naturalness"] = False
            feedbacks.append(f"동일 문장 중복 노출 비율이 {round(dup_ratio * 100, 1)}%로 임계치(5%)를 초과하여 품질 기준에 불합격했습니다.")
            
    # 키워드 어뷰징 도배 검출
    keyword_count = len(re.findall(re.escape(keyword), plain_text))
    if keyword_count > 30:
        details["context_naturalness"] = False
        feedbacks.append(f"핵심 키워드 빈도가 {keyword_count}회로 과도하여 키워드 스터핑 어뷰징 위험이 있습니다. 대명사나 지시어 등으로 문맥을 매끄럽게 보완하십시오.")

    overall_pass = all(details.values())
    
    return {
        "pass": overall_pass,
        "details": details,
        "feedback": "\n".join(feedbacks) if feedbacks else "모든 품질 검사 통과"
    }

if __name__ == "__main__":
    # Test case
    title_test = "소상공인 지원금 신청 신청 자격"
    blocks_test = [
        {"type": "TABLE", "headers": ["구분"], "rows": [["청년내일채움공제 만기 수령"]]},
        {"type": "FAQ", "items": [{"question": "청내공 자격?", "answer": "만 34세"}]}
    ]
    res = evaluate_qa("소상공인 지원금", "정부지원금", title_test, blocks_test, "<html>소상공인 지원금 청내공 군필 청년 워크넷</html>", [])
    print(json.dumps(res, ensure_ascii=False, indent=2))
