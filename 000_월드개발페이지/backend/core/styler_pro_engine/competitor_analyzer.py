import os
import sys
import json
import random
from pathlib import Path
HAS_GEMINI = False
try:
    from google.generativeai import GenerativeModel
    import google.generativeai as genai
    HAS_GEMINI = True
except Exception:
    HAS_GEMINI = False

def generate_mock_competitor_data(keyword):
    """Generates realistic metrics for 10 search results to feed the analyzer."""
    random.seed(keyword)
    competitors = []
    
    # Extract noun tokens for mockup
    tokens = keyword.split()
    base_noun = tokens[0] if tokens else "대상주제"
    
    for i in range(1, 11):
        word_count = random.randint(1200, 3200)
        img_count = random.randint(2, 15)
        h2_count = random.randint(3, 8)
        h3_count = random.randint(2, 10)
        faq_count = random.choice([0, 2, 3, 5])
        table_count = random.choice([0, 1, 2])
        links_count = random.randint(1, 8)
        
        competitors.append({
            "rank": i,
            "title": f"[칼럼] {keyword}에 관한 {i}번째 핵심 정보 및 가이드",
            "word_count": word_count,
            "image_count": img_count,
            "h2_headings": [f"{base_noun}의 {j}번째 중요성" for j in range(1, h2_count + 1)],
            "h3_headings": [f"세부 정보 {j}" for j in range(1, h3_count + 1)],
            "faq_included": faq_count > 0,
            "table_included": table_count > 0,
            "keyword_frequency": random.randint(5, 20),
            "links_count": links_count
        })
        
    return competitors

def analyze_competitors(keyword):
    competitors = generate_mock_competitor_data(keyword)
    
    # Calculate averages
    avg_length = int(sum(c["word_count"] for c in competitors) / len(competitors))
    avg_images = round(sum(c["image_count"] for c in competitors) / len(competitors), 1)
    
    # Setup Gemini API if available
    api_key = os.environ.get("GEMINI_API_KEY", "")
    
    if HAS_GEMINI and api_key.strip():
        try:
            genai.configure(api_key=api_key)
            model = GenerativeModel("gemini-1.5-flash")
            
            prompt = f"""
            주제 키워드: "{keyword}"
            아래는 이 키워드로 상위 노출된 10개 문서들의 간략한 메타데이터 요약입니다.
            {json.dumps(competitors, ensure_ascii=False, indent=2)}
            
            이 데이터를 바탕으로 구글 상위 노출을 위해 '더 완벽한 문서'를 기획할 수 있도록 역분석 보고서를 작성해 주십시오.
            반드시 아래의 JSON 구조로만 답변하고, 백틱(```json)이나 다른 설명 텍스트는 일체 포함하지 마십시오.
            
            {{
              "common_h2": ["상위 문서들이 공통으로 다루는 H2 주제 리스트 3~5개"],
              "common_questions": ["독자가 궁금해하는 공통 질문 및 FAQ 주제 3~5개"],
              "frequent_keywords": ["자주 반복 등장하는 핵심 단어 5개"],
              "average_word_count": {avg_length},
              "typical_structure": "상위 문서들의 공통적인 구성 흐름 설명",
              "missing_topics": ["상위 문서들이 놓치고 있지만 본문에 들어가면 독창성과 전문성을 높일 수 있는 보완/누락 토픽 2~4개"],
              "crawled_stats": {{
                 "avg_length": {avg_length},
                 "avg_images": {avg_images},
                 "faq_ratio": "70%",
                 "table_ratio": "50%"
              }}
            }}
            """
            response = model.generateContent(prompt)
            raw_text = response.text.strip()
            
            # Clean markdown JSON wraps
            import re
            if raw_text.startswith("```"):
                raw_text = re.sub(r'^```json\s*', '', raw_text, flags=re.IGNORECASE)
                raw_text = re.sub(r'```$', '', raw_text).strip()
            return json.loads(raw_text)
            
        except Exception as e:
            # Fallback to smart rule-based mockup on LLM failure
            sys.stderr.write(f"LLM analyzer error: {str(e)}\n")
            
    # Mock fallback response
    base_noun = keyword.split()[0] if keyword.split() else "대상"
    return {
        "common_h2": [
            f"{keyword} 정의 및 원인",
            f"{base_noun} 예방 및 관리 대책",
            f"실제 효과를 본 사람들의 꿀팁"
        ],
        "common_questions": [
            f"{base_noun}는 누구나 다 적용 가능한가요?",
            f"주의해야 할 부작용이나 위험 요인은 없나요?",
            f"기간은 얼마나 잡아야 효과를 볼 수 있나요?"
        ],
        "frequent_keywords": [base_noun, "효과", "방법", "추천", "주의사항"],
        "average_word_count": avg_length,
        "typical_structure": "도입부 -> 정의 -> 원인/필요성 -> 주요 방법 기술 -> FAQ -> 결론",
        "missing_topics": [
            f"GI 지수와의 상관관계 및 실질적 영향 분석",
            f"나이대별/시간대별 구체적인 행동 가이드라인",
            f"전문가의 임상 의견 및 과학적 근거 추가"
        ],
        "crawled_stats": {
            "avg_length": avg_length,
            "avg_images": avg_images,
            "faq_ratio": "60%",
            "table_ratio": "40%"
        }
    }

if __name__ == "__main__":
    keyword = "당뇨 환자 과일"
    if len(sys.argv) > 1:
        keyword = sys.argv[1]
        
    output = analyze_competitors(keyword)
    print(json.dumps(output, ensure_ascii=False, indent=2))
