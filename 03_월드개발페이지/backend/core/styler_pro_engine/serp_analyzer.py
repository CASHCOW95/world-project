import os
import sys
import json
import random
HAS_GEMINI = False
try:
    from google.generativeai import GenerativeModel
    import google.generativeai as genai
    HAS_GEMINI = True
except Exception:
    HAS_GEMINI = False

def collect_serp_metrics(keyword):
    """Mocks top 10 SERP documents with realistic metrics based on the keyword."""
    random.seed(keyword)
    docs = []
    for i in range(1, 11):
        word_count = random.randint(3000, 5200)
        images = random.randint(2, 7)
        tables = random.choice([1, 2, 3, 4])
        faqs = random.choice([6, 8, 10])
        
        docs.append({
            "rank": i,
            "title": f"{keyword}에 관한 {i}번째 정보 칼럼",
            "word_count": word_count,
            "image_count": images,
            "table_count": tables,
            "faq_count": faqs,
            "h2_count": random.randint(4, 7),
            "h3_count": random.randint(8, 15)
        })
    return docs

def analyze_serp(keyword):
    docs = collect_serp_metrics(keyword)
    
    # Calculate Averages
    avg_words = int(sum(d["word_count"] for d in docs) / len(docs))
    avg_images = round(sum(d["image_count"] for d in docs) / len(docs), 1)
    avg_tables = round(sum(d["table_count"] for d in docs) / len(docs), 1)
    avg_faqs = int(sum(d["faq_count"] for d in docs) / len(docs))
    
    # Target suggestion (Average + 20-30%, clamped to v2 standard recommendation ~ 5500 words)
    target_length = max(5000, min(7000, int(avg_words * 1.3)))
    
    api_key = os.environ.get("GEMINI_API_KEY", "")
    
    analysis_report = {
        "avg_word_count": avg_words,
        "avg_image_count": avg_images,
        "avg_table_count": avg_tables,
        "avg_faq_count": avg_faqs,
        "recommended_length": target_length,
        "typical_headings": [
            f"{keyword} 기본 정의와 이해",
            f"{keyword} 핵심 적용 단계 및 수수료/비용",
            f"주의해야 할 안전 수칙 및 꿀팁"
        ],
        "missing_gaps": [
            "연령별/상황별 구체적인 예외 상황 설명",
            "공식 사이트 연동 에러 대처 방안"
        ]
    }
    
    if HAS_GEMINI and api_key.strip():
        try:
            genai.configure(api_key=api_key)
            model = GenerativeModel("gemini-1.5-flash")
            
            prompt = f"""
            주제 키워드: "{keyword}"
            아래는 상위 10개 문서 구조 수집 데이터입니다:
            {json.dumps(docs, ensure_ascii=False, indent=2)}
            
            이 평균 지표들을 참고하여, 본문 글 쓰기 제작 시 기존 문서보다 검색 노출 경쟁력이 우수한 원고를 구성할 수 있도록 역분석 보고서를 JSON 형식으로 작성해 주십시오.
            반드시 아래의 JSON 포맷으로만 답변하고, 백틱(```json)이나 다른 설명글은 일체 포함하지 마십시오.
            
            {{
              "avg_word_count": {avg_words},
              "avg_image_count": {avg_images},
              "avg_table_count": {avg_tables},
              "avg_faq_count": {avg_faqs},
              "recommended_length": {target_length},
              "typical_headings": ["상위 노출 문헌들이 빈번히 활용하는 H2 대주제 목록 3개"],
              "missing_gaps": ["경쟁사에서 놓친 대표적인 꿀정보/누락 토픽 2개"]
            }}
            """
            response = model.generateContent(prompt)
            raw_text = response.text.strip()
            
            # Clean markdown wraps
            import re
            if raw_text.startswith("```"):
                raw_text = re.sub(r'^```json\s*', '', raw_text, flags=re.IGNORECASE)
                raw_text = re.sub(r'```$', '', raw_text).strip()
                
            parsed = json.loads(raw_text)
            # Merge parsed to final report
            analysis_report.update(parsed)
            
        except Exception as e:
            sys.stderr.write(f"SERP Analyzer LLM error: {str(e)}. Using fallback.\n")
            
    return analysis_report

if __name__ == "__main__":
    kw = "감기몸살 빨리 낫는 법"
    if len(sys.argv) > 1:
        kw = sys.argv[1]
    res = analyze_serp(kw)
    print(json.dumps(res, ensure_ascii=False, indent=2))
