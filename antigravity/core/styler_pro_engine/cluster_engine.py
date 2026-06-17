"""
Topic Cluster Engine v1.0
키워드 1개 → 메인글 1 + 서브글 3~15개 동적 생성.
Gemini API 연동 + 오프라인 fallback 템플릿 내장.
"""

import os
import sys
import json
import random
import hashlib
import argparse

try:
    from google.generativeai import GenerativeModel
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False


# ── Gemini 기반 클러스터 생성 ──────────────────────────────────

def generate_cluster_gemini(keyword, category="정보형", min_subs=3, max_subs=10):
    """Gemini API로 토픽 클러스터를 동적 생성한다."""
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not (HAS_GEMINI and api_key.strip()):
        return None

    try:
        genai.configure(api_key=api_key)
        model = GenerativeModel("gemini-1.5-flash")

        prompt = f"""
당신은 수익형 블로그 SEO 전략 컨설턴트입니다.
사용자가 입력한 핵심 키워드를 중심으로, 검색 의도를 기반으로 한
토픽 클러스터(메인글 1개 + 서브글 {min_subs}~{max_subs}개)를 설계해 주십시오.

[핵심 키워드]: {keyword}
[카테고리]: {category}

[규칙]:
1. 메인글은 해당 키워드의 종합 안내 가이드 역할을 한다.
2. 서브글은 메인글에서 파생되는 세부 주제를 다루되, 각각 독립적인 검색 의도를 가진다.
3. 서브글 수는 키워드의 복잡도에 따라 {min_subs}~{max_subs}개 범위에서 AI가 판단한다.
4. 각 서브글에는 anchor_text(메인글에서 서브글로 연결할 때 쓸 자연스러운 CTA 문구)를 생성한다.
5. intent는 정보형/자격형/비교형/절차형/주의형/후기형/비용형 중 하나를 선택한다.

반드시 아래 JSON 형식으로만 응답하십시오. 백틱이나 설명 텍스트 금지.

{{
  "main": {{
    "title": "메인글 제목",
    "intent": "정보형",
    "summary": "메인글 한줄 요약"
  }},
  "subs": [
    {{
      "title": "서브글 제목",
      "intent": "자격형",
      "anchor": "서브글로 유도하는 CTA 문구",
      "summary": "서브글 한줄 요약"
    }}
  ]
}}
"""
        response = model.generateContent(prompt)
        raw = response.text.strip()

        # Strip markdown fences
        if raw.startswith("```"):
            import re
            raw = re.sub(r'^```json\s*', '', raw, flags=re.IGNORECASE)
            raw = re.sub(r'```$', '', raw).strip()

        parsed = json.loads(raw)

        # Validate structure
        if "main" in parsed and "subs" in parsed and isinstance(parsed["subs"], list):
            return parsed

    except Exception as e:
        sys.stderr.write(f"[ClusterEngine] Gemini 호출 실패: {str(e)}\n")

    return None


# ── 오프라인 Fallback 클러스터 생성 ────────────────────────────

# 서브글 의도 템플릿 풀
SUB_TEMPLATES = [
    {"suffix": "신청 대상 및 자격 조건", "intent": "자격형", "anchor": "신청 자격 확인하기"},
    {"suffix": "신청 방법 및 절차 안내", "intent": "절차형", "anchor": "신청 방법 바로 보기"},
    {"suffix": "지원 금액 및 혜택 비교", "intent": "비용형", "anchor": "지원 금액 확인하기"},
    {"suffix": "주의사항 및 흔한 실수", "intent": "주의형", "anchor": "주의사항 반드시 확인"},
    {"suffix": "자주 묻는 질문(FAQ) 총정리", "intent": "정보형", "anchor": "FAQ 전체 보기"},
    {"suffix": "vs 유사 제도 비교 분석", "intent": "비교형", "anchor": "비교 분석 보기"},
    {"suffix": "실제 후기 및 체험 사례", "intent": "후기형", "anchor": "실제 후기 읽어보기"},
    {"suffix": "필요 서류 및 준비물 체크리스트", "intent": "절차형", "anchor": "필요 서류 확인하기"},
    {"suffix": "기한 및 일정 스케줄 안내", "intent": "정보형", "anchor": "일정 확인하기"},
    {"suffix": "중도 해지 및 환불 규정", "intent": "주의형", "anchor": "해지 규정 확인하기"},
    {"suffix": "온라인 vs 오프라인 신청 차이", "intent": "비교형", "anchor": "신청 방식 비교하기"},
    {"suffix": "연령대별 맞춤 혜택 안내", "intent": "자격형", "anchor": "맞춤 혜택 확인하기"},
    {"suffix": "관련 법령 및 근거 조항", "intent": "정보형", "anchor": "법적 근거 확인하기"},
    {"suffix": "전문가 추천 활용 전략", "intent": "정보형", "anchor": "활용 전략 보기"},
    {"suffix": "2026년 최신 변경사항 요약", "intent": "정보형", "anchor": "최신 변경사항 보기"},
]


def _keyword_hash_int(keyword, salt="cluster"):
    """키워드 기반 결정적 해시 → 정수. 동일 키워드는 동일 클러스터를 생성."""
    h = hashlib.md5(f"{keyword}:{salt}".encode("utf-8")).hexdigest()
    return int(h[:8], 16)


def generate_cluster_fallback(keyword, min_subs=3, max_subs=10):
    """오프라인 fallback: 키워드 해시 기반으로 결정적 클러스터를 생성."""
    seed = _keyword_hash_int(keyword)
    rng = random.Random(seed)

    # 서브글 개수: 키워드 복잡도를 길이 + 해시로 시뮬레이션
    sub_count = min_subs + (seed % (max_subs - min_subs + 1))
    sub_count = min(sub_count, len(SUB_TEMPLATES))

    # 템플릿 셔플 후 선택
    pool = list(SUB_TEMPLATES)
    rng.shuffle(pool)
    selected = pool[:sub_count]

    subs = []
    for tmpl in selected:
        subs.append({
            "title": f"{keyword} {tmpl['suffix']}",
            "intent": tmpl["intent"],
            "anchor": tmpl["anchor"],
            "summary": f"{keyword}의 {tmpl['suffix']}에 대한 상세 안내"
        })

    return {
        "main": {
            "title": f"{keyword} 총정리 가이드 (2026 최신판)",
            "intent": "정보형",
            "summary": f"{keyword}에 관한 모든 정보를 한눈에 정리한 종합 가이드"
        },
        "subs": subs
    }


# ── 통합 인터페이스 ────────────────────────────────────────────

def generate_cluster(keyword, category="정보형", min_subs=3, max_subs=10):
    """
    토픽 클러스터를 생성하는 통합 함수.
    Gemini API가 사용 가능하면 AI 생성, 아니면 fallback.
    
    Returns:
        {
            "main": { "title": str, "intent": str, "summary": str },
            "subs": [
                { "title": str, "intent": str, "anchor": str, "summary": str },
                ...
            ]
        }
    """
    # Gemini 시도
    result = generate_cluster_gemini(keyword, category, min_subs, max_subs)
    if result:
        return result

    # Fallback
    sys.stderr.write("[ClusterEngine] Gemini 미사용 → fallback 클러스터 생성\n")
    return generate_cluster_fallback(keyword, min_subs, max_subs)


# ── CLI 진입점 ─────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Topic Cluster Engine v1.0")
    parser.add_argument("--keyword", type=str, required=True, help="핵심 키워드")
    parser.add_argument("--category", type=str, default="정보형")
    parser.add_argument("--min-subs", type=int, default=3)
    parser.add_argument("--max-subs", type=int, default=10)
    parser.add_argument("--dry-run", action="store_true", help="결과만 출력하고 저장하지 않음")

    args = parser.parse_args()

    cluster = generate_cluster(
        keyword=args.keyword,
        category=args.category,
        min_subs=args.min_subs,
        max_subs=args.max_subs
    )

    print("---JSON_START---")
    print(json.dumps(cluster, ensure_ascii=False, indent=2))
    print("---JSON_END---")
